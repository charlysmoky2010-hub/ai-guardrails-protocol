from __future__ import annotations

import unittest

from workflows.payment_delivery_gate import canary_result, PROBE_URL, INVALID_SESSION
from workflows.titanius_control_center import run_cycle


class CheckoutGateTests(unittest.TestCase):
    def test_strict_denial_canary_is_safe_but_not_paid_delivery(self):
        actual = canary_result(lambda: (400, {"paid": False, "error": "bad receipt"}))
        self.assertTrue(actual["invalid_receipt_rejected"])
        self.assertEqual(actual["state"], "negative_path_verified")
        self.assertIsNone(actual["actual_paid_delivery_verified"])
        self.assertIsNone(actual["paid_orders_count"])
        self.assertFalse(actual["performed_payment"])

    def test_deny_boolean_true_even_if_http_is_4xx(self):
        for signal in ("paid", "eligible", "download_allowed", "entitled",
                       "access_granted", "verified", "success"):
            with self.subTest(signal=signal):
                body = {"paid": False, signal: True}
                self.assertFalse(canary_result(lambda: (400, body))["invalid_receipt_rejected"])

    def test_missing_explicit_false_or_http_200_is_not_proven(self):
        probes = [
            (400, {"error": "bad receipt"}),
            (500, {"paid": False}),
            (200, {"paid": False}),
            (302, {"paid": False}),
            (400, {"paid": "false"}),
            (400, None),
            (None, None),
        ]
        for status, body in probes:
            with self.subTest(status=status, body=body):
                self.assertEqual(canary_result(lambda: (status, body))["state"], "unverified_or_unsafe")

    def test_exception_does_not_grant_access_or_create_sale(self):
        def fail():
            raise TimeoutError("no connectivity")
        a = canary_result(fail)
        self.assertFalse(a["invalid_receipt_rejected"])
        self.assertFalse(a["buyer_data_accessed"])
        self.assertIsNone(a["download_receipt_count"])

    def test_only_one_owned_endpoint_and_fixed_bad_id(self):
        self.assertEqual(PROBE_URL, "https://microvault.floot.app/_api/payment/verify")
        self.assertEqual(INVALID_SESSION, "invalid-not-a-real-session")

    def test_security_brain_raises_one_review_blocker_when_guard_unsafe(self):
        cfg = {
            "schema": "titanius.control_center.v1", "brain": "TITANIUS_CERBERRUS",
            "agents": [{"id": x} for x in (
                "finance_intelligence","commerce_brain","delivery_brain","growth_brain",
                "design_brain","security_brain","learning_brain","operations_brain")],
            "sites": [{"id": "microvault_paid", "owner": "commerce",
                       "url": "https://microvault.floot.app/csv-report-kaufen", "required": []}],
        }
        def fetch(_):
            return {"ok": True, "status": 200, "reason": None, "html": "<title>MICROVAULT</title>"}
        first = run_cycle(cfg, fetch, payment_canary={"state":"unverified_or_unsafe"})
        security = [t for t in first["tasks"] if t["agent"] == "security_brain"]
        self.assertEqual(len(security), 1)
        self.assertEqual(security[0]["priority"], 100)
        self.assertEqual(security[0]["permission"], "review")
        self.assertEqual(first["finance"]["confirmed_deliveries"], None)
        second = run_cycle(cfg, fetch, first, payment_canary={"state":"negative_path_verified"})
        self.assertFalse(any(t["agent"] == "security_brain" for t in second["tasks"]))
        self.assertIn(security[0]["id"], second["resolved_since_previous"])
        self.assertIsNone(second["finance"]["confirmed_paid_orders"])


if __name__ == "__main__":
    unittest.main()
