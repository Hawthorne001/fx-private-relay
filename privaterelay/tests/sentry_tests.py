"""Tests for Sentry configuration and _sentry_before_send hook."""

from typing import cast

from sentry_sdk.types import Event

from privaterelay.settings import _sentry_before_send


def test_sentry_before_send_tags_relay_client_platform() -> None:
    """Events with X-Relay-Client header get relay_client_platform tag and context."""
    event = cast(Event, {"request": {"headers": {"X-Relay-Client": "appservices-ios"}}})
    result = _sentry_before_send(event, {})
    assert result is not None
    assert result["tags"]["relay_client_platform"] == "ios"
    assert result["contexts"]["relay_client"] == {
        "header_value": "appservices-ios",
        "os": "ios",
        "platform": "mobile-ios",
    }


def test_sentry_before_send_no_relay_client_header() -> None:
    """Events without X-Relay-Client header are returned unchanged."""
    event = cast(Event, {"request": {"headers": {"User-Agent": "curl/8.7.1"}}})
    result = _sentry_before_send(event, {})
    assert result is not None
    assert "tags" not in result
    assert "contexts" not in result


def test_sentry_before_send_no_request() -> None:
    """Events without a request are returned unchanged."""
    event = cast(Event, {"exception": {"values": []}})
    result = _sentry_before_send(event, {})
    assert result is not None
    assert "tags" not in result
    assert "contexts" not in result


def test_sentry_before_send_preserves_existing_tags() -> None:
    """Existing event tags are preserved when relay_client_platform is added."""
    event = cast(
        Event,
        {
            "request": {"headers": {"X-Relay-Client": "appservices-ios"}},
            "tags": {"existing_tag": "existing_value"},
        },
    )
    result = _sentry_before_send(event, {})
    assert result is not None
    assert result["tags"]["existing_tag"] == "existing_value"
    assert result["tags"]["relay_client_platform"] == "ios"


def test_sentry_before_send_preserves_existing_contexts() -> None:
    """Existing event contexts are preserved when relay_client context is added."""
    event = cast(
        Event,
        {
            "request": {"headers": {"X-Relay-Client": "appservices-android"}},
            "contexts": {"existing_context": {"key": "value"}},
        },
    )
    result = _sentry_before_send(event, {})
    assert result is not None
    assert result["contexts"]["existing_context"] == {"key": "value"}
    assert "relay_client" in result["contexts"]
