"""Read-only worldwide discovery and metacognitive evidence loop for TITANIUS.

A site being reachable, localized or indexed is NOT proof of real visits or sales.
No tokens, external customer messages, cookies, secrets or payment calls.
"""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from typing import Callable, Any

BASE = "https://charlysmoky2010-hub.github.io"
LOCALES = (
    ("de", "/microvault/"),
    ("en", "/microvault/csv-quality-report/"),
    ("es", "/microvault/es/"),
    ("fr", "/microvault/fr/"),
    ("pt-BR", "/microvault/pt-br/"),
    ("ar", "/microvault/ar/"),
    ("ja", "/microvault/ja/"),
)
MAX_HTML = 160_000


class DenyRedirects(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect outside the exact public audit URL."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read_owned_page(url: str) -> dict[str, Any]:
    """Allowlisted GET only; no dynamic URLs, credentials or tracking."""
    if url not in {BASE + path for _, path in LOCALES}:
        raise ValueError("Outside explicitly owned page allowlist")
    req = urllib.request.Request(url, headers={"User-Agent": "TITANIUS-World-Reach/1.0"})
    try:
        with urllib.request.build_opener(DenyRedirects()).open(req, timeout=12) as response:
            html = response.read(MAX_HTML).decode("utf-8", "replace")
            return {"status": response.status, "html": html}
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "html": ""}
    except (urllib.error.URLError, TimeoutError, OSError):
        return {"status": None, "html": ""}


def assess_world(fetch: Callable[[str], dict[str, Any]] = read_owned_page,
                 previous: dict[str, Any] | None = None) -> dict[str, Any]:
    """Classify what can be observed, and challenge unsupported market inferences."""
    former = {item.get("locale"): item for item in (previous or {}).get("pages", [])
              if isinstance(item, dict)}
    pages: list[dict[str, Any]] = []
    for locale, path in LOCALES:
        url = BASE + path
        try:
            result = fetch(url)
            status = result.get("status")
            markup = result.get("html", "")[:MAX_HTML]
        except (ValueError, OSError, KeyError, TypeError):
            status, markup = None, ""
        reachable = status == 200 and bool(markup)
        lang_match = re.search(r"<html\b[^>]*\blang=['\"]([^'\"]+)", markup, re.I)
        lang = lang_match.group(1) if lang_match else None
        lang_ok = bool(lang and lang.lower() == locale.lower())
        canonical = bool(re.search(
            r'<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']'
            + re.escape(url) + r'["\'])[^>]*>', markup, re.I))
        handoff = "microvault.floot.app" in markup or "/microvault/global/checker.html" in markup
        page = {"locale": locale, "url": url, "http_status": status,
                "reachable": reachable, "language_ok": lang_ok if reachable else False,
                "canonical_ok": canonical if reachable else False,
                "visible_product_handoff": handoff if reachable else False}
        prior = former.get(locale, {})
        page["changed_since_last_cycle"] = bool(prior) and any(
            page[key] != prior.get(key) for key in
            ("http_status", "reachable", "language_ok", "canonical_ok", "visible_product_handoff"))
        pages.append(page)

    unhealthy = [x["locale"] for x in pages if not x["reachable"]]
    metadata_gaps = [x["locale"] for x in pages if x["reachable"] and
                     (not x["language_ok"] or not x["canonical_ok"] or
                      not x["visible_product_handoff"])]
    if unhealthy:
        decision = "REPAIR_PUBLIC_REACHABILITY"
        next_action = "Review unreachable owned-language pages before submitting index notifications."
    elif metadata_gaps:
        decision = "REPAIR_LOCALIZATION_AND_HANDOFF"
        next_action = "Review canonical, html language and product handoff for the listed locales."
    else:
        decision = "CONNECT_MEASURED_ACQUISITION"
        next_action = ("Connect privacy-respecting, verifiable aggregate visits and conversion "
                       "events for each market; use observed results before scaling.")
    measured_visitors = None  # Cannot obtain actual visitors from HTML, sitemap or IndexNow.
    measured_checkout_clicks = None
    measured_paid_buyers = None
    return {
        "schema": "titanius.world_reach.v1",
        "pages": pages,
        "reachable_pages": sum(x["reachable"] for x in pages),
        "total_pages": len(LOCALES),
        "unreachable_locales": unhealthy,
        "metadata_or_handoff_gaps": metadata_gaps,
        "qualifying_visitors": measured_visitors,
        "checkout_clicks": measured_checkout_clicks,
        "verified_paid_buyers": measured_paid_buyers,
        "evidence_scope": "read-only owned HTTP HTML, not search rankings or customer analytics",
        "decision": decision,
        "next_action": next_action,
        "changed_public_surfaces": sum(x["changed_since_last_cycle"] for x in pages),
        "reflection": {
            "L1_observation": "HTTP and metadata are directly checked on the owned public URLs",
            "L2_self_critique": "Global language coverage cannot establish international customer reach",
            "L3_meta_critique": "No verified impressions, qualified visits or checkout attribution source",
            "L4_critique_of_critique": "Page-health improvement is not evidence of causal sales uplift",
            "L5_learning_gate": "BLOCKED_NO_OUTCOME_PAIRS",
            "L6_audit": "Do not claim metacognition as consciousness or code tests as revenue",
            "self_correction_from_market_outcomes_proven": False,
        },
        "external_actions": 0,
        "model_calls": 0,
    }
