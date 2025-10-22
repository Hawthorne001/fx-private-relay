from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from datetime import UTC, datetime
from functools import cache
from hashlib import sha256
from typing import Any, TypedDict

from django.apps import apps
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import jwt
import sentry_sdk
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers.fxa.views import FirefoxAccountsOAuth2Adapter
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from markus.utils import generate_tag
from oauthlib.oauth2.rfc6749.errors import CustomOAuth2Error
from requests.exceptions import JSONDecodeError
from rest_framework.decorators import api_view, schema

from emails.models import DomainAddress, RelayAddress
from emails.utils import incr_if_enabled

from .apps import PrivateRelayConfig
from .exceptions import CannotMakeSubdomainException
from .fxa_utils import NoSocialToken, _get_oauth2_session
from .validators import valid_available_subdomain

FXA_SCHEMA_BASE = "https://schemas.accounts.firefox.com/event"
FXA_PROFILE_CHANGE_EVENT = FXA_SCHEMA_BASE + "/profile-change"
FXA_SUBSCRIPTION_CHANGE_EVENT = FXA_SCHEMA_BASE + "/subscription-state-change"
FXA_DELETE_EVENT = FXA_SCHEMA_BASE + "/delete-user"
FXA_PWD_CHANGE_EVENT = FXA_SCHEMA_BASE + "/password-change"
PROFILE_EVENTS = [FXA_PROFILE_CHANGE_EVENT, FXA_SUBSCRIPTION_CHANGE_EVENT]
IGNORED_EVENTS = [FXA_PWD_CHANGE_EVENT]

logger = logging.getLogger("events")
info_logger = logging.getLogger("eventsinfo")


@cache
def _get_fxa(request):
    return request.user.socialaccount_set.filter(provider="fxa").first()


@api_view()
@schema(None)
@require_http_methods(["GET"])
def profile_refresh(request):
    if not request.user or request.user.is_anonymous:
        return redirect(reverse("fxa_login"))
    profile = request.user.profile

    fxa = _get_fxa(request)
    update_fxa(fxa)
    if "clicked-purchase" in request.COOKIES and profile.has_premium:
        event = "user_purchased_premium"
        incr_if_enabled(event, 1)

    return JsonResponse({})


@api_view(["POST", "GET"])
@schema(None)
@require_http_methods(["POST", "GET"])
def profile_subdomain(request):
    if not request.user or request.user.is_anonymous:
        return redirect(reverse("fxa_login"))
    profile = request.user.profile
    if not profile.has_premium:
        raise CannotMakeSubdomainException("error-premium-check-subdomain")
    try:
        if request.method == "GET":
            subdomain = request.GET.get("subdomain", None)
            valid_available_subdomain(subdomain)
            return JsonResponse({"available": True})
        else:
            subdomain = request.POST.get("subdomain", None)
            profile.add_subdomain(subdomain)
            return JsonResponse(
                {"status": "Accepted", "message": "success-subdomain-registered"},
                status=202,
            )
    except CannotMakeSubdomainException as e:
        return JsonResponse({"message": e.message, "subdomain": subdomain}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def metrics_event(request: HttpRequest) -> JsonResponse:
    """
    Handle metrics events from the Relay extension.

    This used to forward data to Google Analytics, but was not updated for GA4.

    Now it logs the information and updates statsd counters.
    """
    try:
        request_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"msg": "Could not decode JSON"}, status=415)
    if "ga_uuid" not in request_data:
        return JsonResponse({"msg": "No GA uuid found"}, status=404)
    event_data = {
        "ga_uuid_hash": sha256(request_data["ga_uuid"].encode()).hexdigest()[:16],
        "category": request_data.get("category", None),
        "action": request_data.get("action", None),
        "label": request_data.get("label", None),
        "value": request_data.get("value", None),
        "browser": request_data.get("browser", None),  # dimension5 in GA
        "source": request_data.get("dimension7", "website"),
    }
    info_logger.info("metrics_event", extra=event_data)
    tags = [
        generate_tag(key, val)
        for key, val in event_data.items()
        if val is not None and key != "ga_uuid_hash"
    ]
    incr_if_enabled("metrics_event", tags=tags)
    return JsonResponse({"msg": "OK"}, status=200)


@csrf_exempt
def fxa_rp_events(request: HttpRequest) -> HttpResponse:
    """MPP-4460: Track more data for FxA relying party exceptions"""
    if (auth := request.headers.get("Authorization")) is None or not auth.startswith(
        "Bearer "
    ):
        return HttpResponse(
            "401 Unauthorized", status=401, headers={"WWW-Authenticate": "Bearer"}
        )
    req_jwt = _parse_jwt_from_request(request)
    authentic_jwt = _authenticate_fxa_jwt(req_jwt)
    with sentry_sdk.new_scope() as scope:
        sentry_context = {"body": request.body, "jwt": authentic_jwt}
        scope.set_context("fxa_rp_event", sentry_context)
        return fxa_rp_events_process_event(authentic_jwt, sentry_context)


def fxa_rp_events_process_event(
    authentic_jwt: FxAEvent, sentry_context: dict[str, Any]
) -> HttpResponse:
    """Augment previous version of fxa_rp_events with additional sentry data"""

    event_keys = _get_event_keys_from_jwt(authentic_jwt)
    try:
        social_account = _get_account_from_jwt(authentic_jwt)
    except SocialAccount.DoesNotExist:
        # Don't error, or FXA will retry
        return HttpResponse("202 Accepted", status=202)

    for event_key in event_keys:
        sentry_context["event_key"] = event_key
        if event_key in PROFILE_EVENTS:
            if settings.DEBUG:
                info_logger.info(
                    "fxa_profile_update",
                    extra={
                        "jwt": authentic_jwt,
                        "event_key": event_key,
                    },
                )
            update_fxa(social_account, authentic_jwt, event_key)
        elif event_key == FXA_DELETE_EVENT:
            _handle_fxa_delete(authentic_jwt, social_account, event_key)
        elif event_key not in IGNORED_EVENTS:
            sentry_sdk.capture_message(f"fxa_rp_events: Unknown event key {event_key}")
    return HttpResponse("200 OK", status=200)


def _parse_jwt_from_request(request: HttpRequest) -> str:
    request_auth = request.headers["Authorization"]
    return request_auth.split("Bearer ")[1]


def fxa_verifying_keys(reload: bool = False) -> list[dict[str, Any]]:
    """Get list of FxA verifying (public) keys."""
    private_relay_config = apps.get_app_config("privaterelay")
    if not isinstance(private_relay_config, PrivateRelayConfig):
        raise TypeError("private_relay_config must be PrivateRelayConfig")
    if reload:
        private_relay_config.ready()
    return private_relay_config.fxa_verifying_keys


def fxa_social_app(reload: bool = False) -> SocialApp:
    """Get FxA SocialApp from app config or DB."""
    private_relay_config = apps.get_app_config("privaterelay")
    if not isinstance(private_relay_config, PrivateRelayConfig):
        raise TypeError("private_relay_config must be PrivateRelayConfig")
    if reload:
        private_relay_config.ready()
    return private_relay_config.fxa_social_app


class FxAEvent(TypedDict):
    """
    FxA Security Event Token (SET) payload, sent to relying parties.

    See:
    https://github.com/mozilla/fxa/tree/main/packages/fxa-event-broker
    https://www.rfc-editor.org/rfc/rfc8417 (Security Event Token)
    """

    iss: str  # Issuer, https://accounts.firefox.com/
    sub: str  # Subject, FxA user ID
    aud: str  # Audience, Relay's client ID
    iat: int  # Creation time, timestamp
    jti: str  # JWT ID, unique for this SET
    events: dict[str, dict[str, Any]]  # Event data


def _authenticate_fxa_jwt(req_jwt: str) -> FxAEvent:
    authentic_jwt = _verify_jwt_with_fxa_key(req_jwt, fxa_verifying_keys())

    if not authentic_jwt:
        # FXA key may be old? re-fetch FXA keys and try again
        authentic_jwt = _verify_jwt_with_fxa_key(
            req_jwt, fxa_verifying_keys(reload=True)
        )
        if not authentic_jwt:
            raise Exception("Could not authenticate JWT with FXA key.")

    return authentic_jwt


def _verify_jwt_with_fxa_key(
    req_jwt: str, verifying_keys: list[dict[str, Any]]
) -> FxAEvent | None:
    if not verifying_keys:
        raise Exception("FXA verifying keys are not available.")
    social_app = fxa_social_app()
    if not social_app:
        raise Exception("FXA SocialApp is not available.")
    if not isinstance(social_app, SocialApp):
        raise TypeError("social_app must be SocialApp")
    for verifying_key in verifying_keys:
        if verifying_key["alg"] == "RS256":
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(verifying_key))
            if not isinstance(public_key, RSAPublicKey):
                raise TypeError("public_key must be RSAPublicKey")
            try:
                security_event = jwt.decode(
                    req_jwt,
                    public_key,
                    audience=social_app.client_id,
                    algorithms=["RS256"],
                    leeway=5,  # allow iat to be slightly in future, for clock skew
                )
            except jwt.ImmatureSignatureError:
                # Issue 2738: Log age of iat, if present
                claims = jwt.decode(
                    req_jwt,
                    public_key,
                    algorithms=["RS256"],
                    options={"verify_signature": False},
                )
                iat = claims.get("iat")
                iat_age = None
                if iat:
                    iat_age = round(datetime.now(tz=UTC).timestamp() - iat, 3)
                info_logger.warning(
                    "fxa_rp_event.future_iat", extra={"iat": iat, "iat_age_s": iat_age}
                )
                raise
            return FxAEvent(
                iss=security_event["iss"],
                sub=security_event["sub"],
                aud=security_event["aud"],
                iat=security_event["iat"],
                jti=security_event["jti"],
                events=security_event["events"],
            )
    return None


def _get_account_from_jwt(authentic_jwt: FxAEvent) -> SocialAccount:
    social_account_uid = authentic_jwt["sub"]
    return SocialAccount.objects.get(uid=social_account_uid, provider="fxa")


def _get_event_keys_from_jwt(authentic_jwt: FxAEvent) -> Iterable[str]:
    return authentic_jwt["events"].keys()


def update_fxa(
    social_account: SocialAccount,
    authentic_jwt: FxAEvent | None = None,
    event_key: str | None = None,
) -> HttpResponse:
    """MPP-4460: Track more data for FxA profile update exceptions"""

    with sentry_sdk.new_scope() as scope:
        sentry_context = {
            "social_account_uid": social_account.uid,
            "authentic_jwt": authentic_jwt,
            "event_key": event_key,
        }
        scope.set_context("update_fxa", sentry_context)
        return update_fxa_inner(
            social_account, sentry_context, authentic_jwt, event_key
        )


def update_fxa_inner(
    social_account: SocialAccount,
    sentry_context: dict[str, Any],
    authentic_jwt: FxAEvent | None = None,
    event_key: str | None = None,
) -> HttpResponse:
    """Augment previous version of update_fxa with additional sentry data"""

    try:
        client = _get_oauth2_session(social_account)
    except NoSocialToken as e:
        sentry_sdk.capture_exception(e)
        return HttpResponse("202 Accepted", status=202)

    # TODO: more graceful handling of profile fetch failures
    try:
        resp = client.get(FirefoxAccountsOAuth2Adapter.profile_url)
    except CustomOAuth2Error as e:
        sentry_sdk.capture_exception(e)
        return HttpResponse("202 Accepted", status=202)

    sentry_context["profile_status_code"] = resp.status_code
    try:
        extra_data = resp.json()
    except JSONDecodeError:
        sentry_context["profile_resp_body"] = resp.body
        raise
    sentry_context["profile_resp"] = extra_data

    try:
        new_email = extra_data["email"]
    except KeyError as e:
        sentry_sdk.capture_exception(e)
        return HttpResponse("202 Accepted", status=202)

    if authentic_jwt and event_key:
        info_logger.info(
            "fxa_rp_event",
            extra={
                "fxa_uid": authentic_jwt["sub"],
                "event_key": event_key,
                "real_address": sha256(new_email.encode("utf-8")).hexdigest(),
            },
        )

    return _update_all_data(social_account, extra_data, new_email)


def _update_all_data(
    social_account: SocialAccount, extra_data: dict[str, Any], new_email: str
) -> HttpResponse:
    try:
        profile = social_account.user.profile
        had_premium = profile.has_premium
        had_phone = profile.has_phone
        with transaction.atomic():
            social_account.extra_data = extra_data
            social_account.save()
            profile = social_account.user.profile
            now_has_premium = profile.has_premium
            newly_premium = not had_premium and now_has_premium
            no_longer_premium = had_premium and not now_has_premium
            if newly_premium:
                incr_if_enabled("user_purchased_premium", 1)
                profile.date_subscribed = datetime.now(UTC)
                profile.save()
            if no_longer_premium:
                incr_if_enabled("user_has_downgraded", 1)
            now_has_phone = profile.has_phone
            newly_phone = not had_phone and now_has_phone
            no_longer_phone = had_phone and not now_has_phone
            if newly_phone:
                incr_if_enabled("user_purchased_phone", 1)
                profile.date_subscribed_phone = datetime.now(UTC)
                profile.date_phone_subscription_reset = datetime.now(UTC)
                profile.save()
            if no_longer_phone:
                incr_if_enabled("user_has_dropped_phone", 1)
            social_account.user.email = new_email
            social_account.user.save()
            email_address_record = social_account.user.emailaddress_set.first()
            if email_address_record:
                email_address_record.email = new_email
                email_address_record.save()
            else:
                social_account.user.emailaddress_set.create(email=new_email)
            return HttpResponse("202 Accepted", status=202)
    except IntegrityError as e:
        sentry_sdk.capture_exception(e)
        return HttpResponse("Conflict", status=409)


def _handle_fxa_delete(
    authentic_jwt: FxAEvent, social_account: SocialAccount, event_key: str
) -> None:
    # Using for loops here because QuerySet.delete() does a bulk delete which does
    # not call the model delete() methods that create DeletedAddress records
    for relay_address in RelayAddress.objects.filter(user=social_account.user):
        relay_address.delete()
    for domain_address in DomainAddress.objects.filter(user=social_account.user):
        domain_address.delete()

    social_account.user.delete()
    info_logger.info(
        "fxa_rp_event",
        extra={
            "fxa_uid": authentic_jwt["sub"],
            "event_key": event_key,
        },
    )
