"""Read-only payment-to-delivery denial canary for MicroVault.

This is one intentionally invalid, synthetic session identifier per scheduled run.
It NEVER creates a Stripe session, charges a card, reads buyer PII, or grants access.
A DENIED result verifies only the negative access path -- not real fulfillment.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Callable

PROBE_URL = "https://microvault.floot.app/_api/payment/verify"
INVALID_SESSION = "invalid-not-a-real-session"
ALLOWED_STATUSES = frozenset({400, 401, 403})


class DenyAllRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def request_invalid_checkout() -> tuple[int | None, Any]:
    """A bounded self-owned HTTP POST, not a purchase or third-party scan."""
    request = urllib.request.Request(
        PROBE_URL,
        method="POST",
        data=json.dumps({"sessionId": INVALID_SESSION}, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 "User-Agent": "TITANIUS-Payment-Denial-Canary/1.0"},
    )
    opener = urllib.request.build_opener(DenyAllRedirects)
    try:
        with opener.open(request, timeout=12) as response:
            body = response.read(4096)
            return response.status, _parse_json(body)
    except urllib.error.HTTPError as error:
        return error.code, _parse_json(error.read(4096))
    except (urllib.error.URLError, TimeoutError, OSError):
        return None, None


def _parse_json(value: bytes) -> Any:
    try:
        obj = json.loads(value.decode("utf-8", errors="replace"))
    except (ValueError, UnicodeError):
        return None
    return obj if isinstance(obj, dict) else None


def canary_result(check: Callable[[], tuple[int | None, Any]] = request_invalid_checkout) -> dict[str, Any]:
    try:
        status, body = check()
    except Exception:  # Fail closed on transport/mocking errors.
        status, body = None, None
    denied = (status in ALLOWED_STATUSES and isinstance(body, dict) and
              body.get("paid") is False and
              all(body.get(key) is not True for key in
                  ("access_granted", "eligible", "download_allowed", "can_download",
                   "verified", "is_paid", "entitled", "success")))
    return {
        "probe": "deliberately_invalid_stripe_session",
        "http_status": status if isinstance(status, int) else None,
        "invalid_receipt_rejected": bool(denied),
        "state": "negative_path_verified" if denied else "unverified_or_unsafe",
        "actual_paid_delivery_verified": None,
        "paid_orders_count": None,
        "download_receipt_count": None,
        "performed_payment": False,
        "buyer_data_accessed": False,
    }
