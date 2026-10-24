"""Marketing brain: evidence-bounded, zero-LLM offer audit for paid digital products.

Source interpretation: Seth Godin's 2026 podcast *episode notes* and Sabri Suby's
2026 digital-marketing *episode description* motivate the audit categories.
This does not reproduce or claim an unavailable complete video transcript.
No automated outreach, paid advertising, price changes, or fake social proof.
"""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from typing import Any


class PageReader(HTMLParser):
    """Keep visible, first-party page copy; discard script/style/hidden blocks."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.tag_stack: list[tuple[str, bool]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        ignored = tag in {"script", "style", "template", "noscript", "svg"} or self.skip > 0
        self.tag_stack.append((tag, ignored))
        if ignored:
            self.skip += 1
        if tag == "a" and not ignored:
            self.links.append((attributes.get("href") or "", attributes.get("aria-label") or ""))
        if tag in {"img", "input", "button"} and not ignored:
            alt = (attributes.get("alt") or "") + " " + (attributes.get("aria-label") or "")
            if alt.strip():
                self.parts.append(alt)
        if tag in {"br", "p", "h1", "h2", "h3", "button", "a", "li"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self.tag_stack:
            return
        # HTMLParser is intentionally tolerant of browser-generated markup,
        # but stacks are always unwound only at the correct ending tag.
        for i in range(len(self.tag_stack) - 1, -1, -1):
            if self.tag_stack[i][0] == tag:
                removed = self.tag_stack[i:]
                self.tag_stack = self.tag_stack[:i]
                self.skip = max(0, self.skip - sum(int(x[1]) for x in removed))
                break
        if tag in {"p", "h1", "h2", "h3", "button", "a", "li"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self.skip == 0:
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", html.unescape(" ".join(self.parts))).strip()


def audit_digital_offer(markup: str, *, site_id: str) -> dict[str, Any]:
    """Assess page disclosure, *not* demand, sales, actual trust, or real UX."""
    if site_id != "microvault_paid":
        return {"checked": False, "signals": {}, "missing": [], "scope": "not_a_paid_microvault_page"}
    parser = PageReader()
    parser.feed(markup[:192000])
    text = parser.text().casefold()
    links = [href.lower() for href, _ in parser.links]
    # Explicit marker groups are independently testable observations.
    # Absence may be a JS-rendering/visibility issue; it is a review signal.
    checks: dict[str, bool] = {
        "specific_customer_problem": (
            ("csv" in text) and any(x in text for x in ("daten", "duplikat", "leere", "prüfung", "prüf"))
        ),
        "visible_once_offers": bool(re.search(r"(?:5\s*€|€\s*5)", text)) and
            bool(re.search(r"(?:29\s*€|€\s*29)", text)) and
            any(x in text for x in ("einmalig", "einmalzahlung", "ohne abo")),
        "purchase_call_to_action": bool(
            re.search(r"(kaufen|jetzt bezahlen|zum checkout|bericht bestellen)", text)
        ),
        "fulfillment_expectations": any(x in text for x in
            ("herunterladen", "download", "direkt nach", "nach bestätigter zahlung")),
        "data_handling_disclosure": any(x in text for x in
            ("im browser", "lokal", "deinem gerät", "datenschutz")),
        "legal_information_path": any(
            any(token in href for token in ("rechtliches", "imprint", "privacy", "datenschutz"))
            for href in links
        ),
        "buyer_questions_answered": any(x in text for x in
            ("was genau", "häufige fragen", "faq", "welche datei")),
        "provider_identity_visible": ("smokycharly" in text),
    }
    return {
        "checked": True,
        "signals": checks,
        "missing": [name for name, passed in checks.items() if not passed],
        "passing_signals": sum(checks.values()),
        "total_signals": len(checks),
        "measurement": "visible_html_offer_disclosure_not_real_conversions",
        "sales_verified": None,
        "customer_reviews_verified": None,
        "source": "2026_video_episode_notes_and_live_html_only",
    }
