"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

AUTOGENERATED BY glean_parser v17.3.0. DO NOT EDIT. To recreate, run:

bash .circleci/python_job.bash run build_glean
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

GLEAN_EVENT_MOZLOG_TYPE = "glean-server-event"


class EventsServerEventLogger:
    def __init__(
        self, application_id: str, app_display_version: str, channel: str
    ) -> None:
        """
        Create EventsServerEventLogger instance.

        :param str application_id: The application ID.
        :param str app_display_version: The application display version.
        :param str channel: The channel.
        """
        self._application_id = application_id
        self._app_display_version = app_display_version
        self._channel = channel

    def _record(self, user_agent: str, ip_address: str, event: dict[str, Any]) -> None:
        now = datetime.now(UTC)
        timestamp = now.isoformat()
        event["timestamp"] = int(1000.0 * now.timestamp())  # Milliseconds since epoch
        event_payload = {
            "metrics": {},
            "events": [event],
            "ping_info": {
                # seq is required in the Glean schema, however is not useful in server context
                "seq": 0,
                "start_time": timestamp,
                "end_time": timestamp,
            },
            # `Unknown` fields below are required in the Glean schema, however they are
            # not useful in server context
            "client_info": {
                "telemetry_sdk_build": "glean_parser v17.3.0",
                "first_run_date": "Unknown",
                "os": "Unknown",
                "os_version": "Unknown",
                "architecture": "Unknown",
                "app_build": "Unknown",
                "app_display_version": self._app_display_version,
                "app_channel": self._channel,
            },
        }
        event_payload_serialized = json.dumps(event_payload)

        # This is the message structure that Decoder expects:
        # https://github.com/mozilla/gcp-ingestion/pull/2400
        ping = {
            "document_namespace": self._application_id,
            "document_type": "events",
            "document_version": "1",
            "document_id": str(uuid4()),
            "user_agent": user_agent,
            "ip_address": ip_address,
            "payload": event_payload_serialized,
        }

        self.emit_record(now, ping)

    def emit_record(self, now: datetime, ping: dict[str, Any]) -> None:
        """Log the ping to STDOUT.
        Applications might want to override this method to use their own logging.
        If doing so, make sure to log the ping as JSON, and to include the
        `Type: GLEAN_EVENT_MOZLOG_TYPE`."""
        ping_envelope = {
            "Timestamp": now.isoformat(),
            "Logger": "glean",
            "Type": GLEAN_EVENT_MOZLOG_TYPE,
            "Fields": ping,
        }
        ping_envelope_serialized = json.dumps(ping_envelope)

        print(ping_envelope_serialized)

    def record_api_accessed(
        self,
        user_agent: str,
        ip_address: str,
        endpoint: str,
        method: str,
        fxa_id: str,
    ) -> None:
        """
        Record and submit a api_accessed event:
        An API endpoint was accessed.
        Event is logged to STDOUT via `print`.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str endpoint: The name of the endpoint accessed
        :param str method: HTTP method used
        :param str fxa_id: Mozilla accounts user ID
        """
        event = {
            "category": "api",
            "name": "accessed",
            "extra": {
                "endpoint": str(endpoint),
                "method": str(method),
                "fxa_id": str(fxa_id),
            },
        }
        self._record(user_agent, ip_address, event)

    def record_email_blocked(
        self,
        user_agent: str,
        ip_address: str,
        fxa_id: str,
        platform: str,
        n_random_masks: int,
        n_domain_masks: int,
        n_deleted_random_masks: int,
        n_deleted_domain_masks: int,
        date_joined_relay: int,
        premium_status: str,
        date_joined_premium: int,
        has_extension: bool,
        date_got_extension: int,
        is_random_mask: bool,
        is_reply: bool,
        reason: str,
    ) -> None:
        """
        Record and submit a email_blocked event:
        Relay receives but does not forward an email for a Relay user.
        Event is logged to STDOUT via `print`.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str fxa_id: Mozilla accounts user ID
        :param str platform: Relay client platform
        :param int n_random_masks: Number of random masks
        :param int n_domain_masks: Number of premium subdomain masks
        :param int n_deleted_random_masks: Number of deleted random masks
        :param int n_deleted_domain_masks: Number of deleted domain masks
        :param int date_joined_relay: Timestamp for joining Relay, seconds since epoch
        :param str premium_status: Subscription type and term
        :param int date_joined_premium: Timestamp for starting premium_status subscription, seconds since epoch, -1 if not subscribed
        :param bool has_extension: The user has the Relay Add-on
        :param int date_got_extension: Timestamp for adding Relay Add-on, seconds since epoch, -1 if not used
        :param bool is_random_mask: The mask is a random mask, instead of a domain mask
        :param bool is_reply: The email is a reply from the Relay user
        :param str reason: Code describing why the email was blocked
        """
        event = {
            "category": "email",
            "name": "blocked",
            "extra": {
                "fxa_id": str(fxa_id),
                "platform": str(platform),
                "n_random_masks": str(n_random_masks),
                "n_domain_masks": str(n_domain_masks),
                "n_deleted_random_masks": str(n_deleted_random_masks),
                "n_deleted_domain_masks": str(n_deleted_domain_masks),
                "date_joined_relay": str(date_joined_relay),
                "premium_status": str(premium_status),
                "date_joined_premium": str(date_joined_premium),
                "has_extension": str(has_extension).lower(),
                "date_got_extension": str(date_got_extension),
                "is_random_mask": str(is_random_mask).lower(),
                "is_reply": str(is_reply).lower(),
                "reason": str(reason),
            },
        }
        self._record(user_agent, ip_address, event)

    def record_email_forwarded(
        self,
        user_agent: str,
        ip_address: str,
        fxa_id: str,
        platform: str,
        n_random_masks: int,
        n_domain_masks: int,
        n_deleted_random_masks: int,
        n_deleted_domain_masks: int,
        date_joined_relay: int,
        premium_status: str,
        date_joined_premium: int,
        has_extension: bool,
        date_got_extension: int,
        is_random_mask: bool,
        is_reply: bool,
    ) -> None:
        """
        Record and submit a email_forwarded event:
        Relay receives and forwards an email for a Relay user.
        Event is logged to STDOUT via `print`.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str fxa_id: Mozilla accounts user ID
        :param str platform: Relay client platform
        :param int n_random_masks: Number of random masks
        :param int n_domain_masks: Number of premium subdomain masks
        :param int n_deleted_random_masks: Number of deleted random masks
        :param int n_deleted_domain_masks: Number of deleted domain masks
        :param int date_joined_relay: Timestamp for joining Relay, seconds since epoch
        :param str premium_status: Subscription type and term
        :param int date_joined_premium: Timestamp for starting premium_status subscription, seconds since epoch, -1 if not subscribed
        :param bool has_extension: The user has the Relay Add-on
        :param int date_got_extension: Timestamp for adding Relay Add-on, seconds since epoch, -1 if not used
        :param bool is_random_mask: The mask is a random mask, instead of a domain mask
        :param bool is_reply: The email is a reply from the Relay user
        """
        event = {
            "category": "email",
            "name": "forwarded",
            "extra": {
                "fxa_id": str(fxa_id),
                "platform": str(platform),
                "n_random_masks": str(n_random_masks),
                "n_domain_masks": str(n_domain_masks),
                "n_deleted_random_masks": str(n_deleted_random_masks),
                "n_deleted_domain_masks": str(n_deleted_domain_masks),
                "date_joined_relay": str(date_joined_relay),
                "premium_status": str(premium_status),
                "date_joined_premium": str(date_joined_premium),
                "has_extension": str(has_extension).lower(),
                "date_got_extension": str(date_got_extension),
                "is_random_mask": str(is_random_mask).lower(),
                "is_reply": str(is_reply).lower(),
            },
        }
        self._record(user_agent, ip_address, event)

    def record_email_mask_created(
        self,
        user_agent: str,
        ip_address: str,
        fxa_id: str,
        platform: str,
        n_random_masks: int,
        n_domain_masks: int,
        n_deleted_random_masks: int,
        n_deleted_domain_masks: int,
        date_joined_relay: int,
        premium_status: str,
        date_joined_premium: int,
        has_extension: bool,
        date_got_extension: int,
        is_random_mask: bool,
        created_by_api: bool,
        has_website: bool,
    ) -> None:
        """
        Record and submit a email_mask_created event:
        A Relay user creates an email mask.
        Event is logged to STDOUT via `print`.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str fxa_id: Mozilla accounts user ID
        :param str platform: Relay client platform
        :param int n_random_masks: Number of random masks
        :param int n_domain_masks: Number of premium subdomain masks
        :param int n_deleted_random_masks: Number of deleted random masks
        :param int n_deleted_domain_masks: Number of deleted domain masks
        :param int date_joined_relay: Timestamp for joining Relay, seconds since epoch
        :param str premium_status: Subscription type and term
        :param int date_joined_premium: Timestamp for starting premium_status subscription, seconds since epoch, -1 if not subscribed
        :param bool has_extension: The user has the Relay Add-on
        :param int date_got_extension: Timestamp for adding Relay Add-on, seconds since epoch, -1 if not used
        :param bool is_random_mask: The mask is a random mask, instead of a domain mask
        :param bool created_by_api: The mask was created via the API, rather than an incoming email
        :param bool has_website: The mask was created by the Add-on or integration on a website
        """
        event = {
            "category": "email_mask",
            "name": "created",
            "extra": {
                "fxa_id": str(fxa_id),
                "platform": str(platform),
                "n_random_masks": str(n_random_masks),
                "n_domain_masks": str(n_domain_masks),
                "n_deleted_random_masks": str(n_deleted_random_masks),
                "n_deleted_domain_masks": str(n_deleted_domain_masks),
                "date_joined_relay": str(date_joined_relay),
                "premium_status": str(premium_status),
                "date_joined_premium": str(date_joined_premium),
                "has_extension": str(has_extension).lower(),
                "date_got_extension": str(date_got_extension),
                "is_random_mask": str(is_random_mask).lower(),
                "created_by_api": str(created_by_api).lower(),
                "has_website": str(has_website).lower(),
            },
        }
        self._record(user_agent, ip_address, event)

    def record_email_mask_deleted(
        self,
        user_agent: str,
        ip_address: str,
        fxa_id: str,
        platform: str,
        n_random_masks: int,
        n_domain_masks: int,
        n_deleted_random_masks: int,
        n_deleted_domain_masks: int,
        date_joined_relay: int,
        premium_status: str,
        date_joined_premium: int,
        has_extension: bool,
        date_got_extension: int,
        is_random_mask: bool,
    ) -> None:
        """
        Record and submit a email_mask_deleted event:
        A Relay user deletes an email mask.
        Event is logged to STDOUT via `print`.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str fxa_id: Mozilla accounts user ID
        :param str platform: Relay client platform
        :param int n_random_masks: Number of random masks
        :param int n_domain_masks: Number of premium subdomain masks
        :param int n_deleted_random_masks: Number of deleted random masks
        :param int n_deleted_domain_masks: Number of deleted domain masks
        :param int date_joined_relay: Timestamp for joining Relay, seconds since epoch
        :param str premium_status: Subscription type and term
        :param int date_joined_premium: Timestamp for starting premium_status subscription, seconds since epoch, -1 if not subscribed
        :param bool has_extension: The user has the Relay Add-on
        :param int date_got_extension: Timestamp for adding Relay Add-on, seconds since epoch, -1 if not used
        :param bool is_random_mask: The mask is a random mask, instead of a domain mask
        """
        event = {
            "category": "email_mask",
            "name": "deleted",
            "extra": {
                "fxa_id": str(fxa_id),
                "platform": str(platform),
                "n_random_masks": str(n_random_masks),
                "n_domain_masks": str(n_domain_masks),
                "n_deleted_random_masks": str(n_deleted_random_masks),
                "n_deleted_domain_masks": str(n_deleted_domain_masks),
                "date_joined_relay": str(date_joined_relay),
                "premium_status": str(premium_status),
                "date_joined_premium": str(date_joined_premium),
                "has_extension": str(has_extension).lower(),
                "date_got_extension": str(date_got_extension),
                "is_random_mask": str(is_random_mask).lower(),
            },
        }
        self._record(user_agent, ip_address, event)

    def record_email_mask_label_updated(
        self,
        user_agent: str,
        ip_address: str,
        fxa_id: str,
        platform: str,
        n_random_masks: int,
        n_domain_masks: int,
        n_deleted_random_masks: int,
        n_deleted_domain_masks: int,
        date_joined_relay: int,
        premium_status: str,
        date_joined_premium: int,
        has_extension: bool,
        date_got_extension: int,
        is_random_mask: bool,
    ) -> None:
        """
        Record and submit a email_mask_label_updated event:
        A Relay user updates an email mask's label.
        Event is logged to STDOUT via `print`.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str fxa_id: Mozilla accounts user ID
        :param str platform: Relay client platform
        :param int n_random_masks: Number of random masks
        :param int n_domain_masks: Number of premium subdomain masks
        :param int n_deleted_random_masks: Number of deleted random masks
        :param int n_deleted_domain_masks: Number of deleted domain masks
        :param int date_joined_relay: Timestamp for joining Relay, seconds since epoch
        :param str premium_status: Subscription type and term
        :param int date_joined_premium: Timestamp for starting premium_status subscription, seconds since epoch, -1 if not subscribed
        :param bool has_extension: The user has the Relay Add-on
        :param int date_got_extension: Timestamp for adding Relay Add-on, seconds since epoch, -1 if not used
        :param bool is_random_mask: The mask is a random mask, instead of a domain mask
        """
        event = {
            "category": "email_mask",
            "name": "label_updated",
            "extra": {
                "fxa_id": str(fxa_id),
                "platform": str(platform),
                "n_random_masks": str(n_random_masks),
                "n_domain_masks": str(n_domain_masks),
                "n_deleted_random_masks": str(n_deleted_random_masks),
                "n_deleted_domain_masks": str(n_deleted_domain_masks),
                "date_joined_relay": str(date_joined_relay),
                "premium_status": str(premium_status),
                "date_joined_premium": str(date_joined_premium),
                "has_extension": str(has_extension).lower(),
                "date_got_extension": str(date_got_extension),
                "is_random_mask": str(is_random_mask).lower(),
            },
        }
        self._record(user_agent, ip_address, event)

    def record_phone_call_received(
        self,
        user_agent: str,
        ip_address: str,
        fxa_id: str,
    ) -> None:
        """
        Record and submit a phone_call_received event:
        A Relay user receives a phone call.
        Event is logged to STDOUT via `print`.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str fxa_id: Mozilla accounts user ID
        """
        event = {
            "category": "phone",
            "name": "call_received",
            "extra": {
                "fxa_id": str(fxa_id),
            },
        }
        self._record(user_agent, ip_address, event)

    def record_phone_text_received(
        self,
        user_agent: str,
        ip_address: str,
        fxa_id: str,
    ) -> None:
        """
        Record and submit a phone_text_received event:
        A Relay user receives a text message.
        Event is logged to STDOUT via `print`.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str fxa_id: Mozilla accounts user ID
        """
        event = {
            "category": "phone",
            "name": "text_received",
            "extra": {
                "fxa_id": str(fxa_id),
            },
        }
        self._record(user_agent, ip_address, event)


def create_events_server_event_logger(
    application_id: str,
    app_display_version: str,
    channel: str,
) -> EventsServerEventLogger:
    """
    Factory function that creates an instance of Glean Server Event Logger to record
    `events` ping events.
    :param str application_id: The application ID.
    :param str app_display_version: The application display version.
    :param str channel: The channel.
    :return: An instance of EventsServerEventLogger.
    :rtype: EventsServerEventLogger
    """
    return EventsServerEventLogger(application_id, app_display_version, channel)
