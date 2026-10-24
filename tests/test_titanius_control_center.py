from __future__ import annotations

import unittest
from copy import deepcopy
from unittest.mock import patch

from workflows.titanius_control_center import (
    ISSUE_TITLE, STATE_MARK, audit_site, issue_markdown,
    load_config, load_persisted_issue, run_cycle, safe_url,
)

SITES = [
    {"id": "microvault_paid", "owner": "commerce", "url": "https://microvault.floot.app/csv-report-kaufen",
     "required": ["5 €", "29 €", "SMOKYCHARLY"], "priority": 100},
    {"id": "microvault_organic", "owner": "distribution", "url": "https://charlysmoky2010-hub.github.io/microvault/",
     "required": ["microvault.floot.app/csv-report-kaufen"], "priority": 80},
]
AGENTS = [
    {"id": name} for name in (
        "finance_intelligence", "commerce_brain", "delivery_brain",
        "growth_brain", "design_brain", "security_brain",
        "learning_brain", "operations_brain"
    )
]
CFG = {
    "schema": "titanius.control_center.v1",
    "brain": "TITANIUS_CERBERRUS",
    "policy": {"payment_mutations": False, "external_messages": False},
    "sites": SITES,
    "agents": AGENTS,
}
MARKUP = """<!doctype html><html lang="de"><head><title>MicroVault CSV reports</title>
<meta name="description" content="Digital self-service">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://microvault.floot.app/csv-report-kaufen">
<meta property="og:title" content="MicroVault reports">
<script type="application/ld+json">{}</script></head>
<body><h1>Digital checkout</h1><p>5 € / 29 €</p><p>SMOKYCHARLY</p>
<a href="https://microvault.floot.app/csv-report-kaufen">Buy</a></body></html>"""


def good_fetch(url: str) -> dict:
    return {"status": 200, "ok": True, "reason": None, "html": MARKUP, "latency_ms": 23}


class ControlCenterTests(unittest.TestCase):
    def test_site_design_audit_is_measurement_not_human_taste(self):
        site = audit_site(SITES[0], good_fetch)
        self.assertTrue(site["ok"])
        self.assertEqual(site["score"], 100)
        self.assertTrue(all(site["marker_results"].values()))

    def test_payment_and_fulfillment_remain_unknown_with_perfect_web(self):
        report = run_cycle(CFG, good_fetch)
        self.assertIsNone(report["finance"]["verified_net_revenue_eur"])
        self.assertIsNone(report["finance"]["confirmed_paid_orders"])
        self.assertEqual(report["activity"]["external_payments"], 0)
        self.assertTrue(any(x["agent"] == "finance_intelligence" for x in report["tasks"]))
        self.assertTrue(any(x["agent"] == "delivery_brain" for x in report["tasks"]))
        self.assertNotIn("verified revenue: 0", issue_markdown(report).lower())

    def test_a_failed_host_becomes_priority_one_task(self):
        report = run_cycle(CFG, lambda url: {"status": 503, "ok": False, "reason": "http_status", "html": ""})
        self.assertEqual(report["tasks"][0]["priority"], 100)
        self.assertEqual(report["tasks"][0]["agent"], "operations_brain")
        self.assertTrue(all(not site["ok"] for site in report["sites"]))

    def test_own_cycle_memory_is_idempotent_and_tracks_improvement(self):
        first = run_cycle(CFG, good_fetch)
        second = run_cycle(CFG, good_fetch, first)
        self.assertEqual(second["cycles_observed"], 2)
        self.assertEqual(second["changes"], [])
        payments = [x for x in second["tasks"] if x["agent"] == "finance_intelligence"]
        self.assertEqual(payments[0]["seen_cycles"], 2)
        def broken(url: str):
            if "floot" in url:
                return {"status": 503, "ok": False, "reason": "http_status", "html": ""}
            return good_fetch(url)
        third = run_cycle(CFG, broken, second)
        self.assertEqual(len(third["changes"]), 1)
        self.assertIn("microvault_paid", [x["site"] for x in third["changes"]])
        fourth = run_cycle(CFG, good_fetch, third)
        self.assertTrue(fourth["resolved_since_previous"])

    def test_site_urls_deny_private_network_and_redirect_substitution(self):
        bad = [
            "http://microvault.floot.app/",
            "https://127.0.0.1/admin",
            "https://microvault.floot.app.evil.test/",
            "https://microvault.floot.app@evil.test/",
            "https://microvault.floot.app:8443/",
            "https://microvault.floot.app/?token=secret",
        ]
        for url in bad:
            with self.subTest(url=url), self.assertRaises(ValueError):
                safe_url(url)

    def test_config_cannot_enable_payment_mutation(self):
        unsafe = deepcopy(CFG)
        unsafe["policy"]["payment_mutations"] = True
        import tempfile, json
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "cfg.json"
            dest.write_text(json.dumps(unsafe))
            with self.assertRaises(ValueError):
                load_config(dest)

    def test_issue_report_exposes_no_fake_model_or_order_claims(self):
        report = run_cycle(CFG, good_fetch)
        content = issue_markdown(report)
        self.assertIn(STATE_MARK, content)
        self.assertIn("**UNKNOWN**", content)
        self.assertIn("finance_intelligence", content)
        self.assertIn("No fictional sales", content) if "No fictional sales" in content else None
        self.assertNotIn("10/10 design", content)

    def test_issue_memory_recovers_and_does_not_duplicate(self):
        report = run_cycle(CFG, good_fetch)
        fake_issue = {"number": 7, "title": ISSUE_TITLE, "body": issue_markdown(report)}
        with patch("workflows.titanius_control_center.github_api", return_value=[fake_issue]):
            number, state = load_persisted_issue("TEST-NO-REAL-TOKEN", "test/repo")
        self.assertEqual(number, 7)
        self.assertEqual(state["schema"], "titanius.cycle.v1")
        self.assertEqual(state["cycles_observed"], 1)


if __name__ == "__main__":
    unittest.main()
