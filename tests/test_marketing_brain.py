from __future__ import annotations

import unittest

from workflows.marketing_brain import audit_digital_offer
from workflows.titanius_control_center import run_cycle


class MarketingBrainTests(unittest.TestCase):
    def setUp(self):
        self.html = """<!doctype html><html lang="de"><body>
          <h1>CSV-Datenqualität: Duplikate erkennen und leere Felder prüfen</h1>
          <p>5 € einmalig für den Deep Report; 29 € einmalig für den Decision Pack.</p>
          <p>Deine Daten bleiben lokal im Browser. Nach bestätigter Zahlung herunterladen.</p>
          <button>Kaufen</button>
          <p>Bezahlung: SMOKYCHARLY</p>
          <section><h2>Was genau wird geliefert?</h2><p>Eine Textdatei.</p></section>
          <a href="/rechtliches?page=privacy">Datenschutz</a>
          <script>window.fakeTestimonials="1000 delighted buyers";</script>
          </body></html>"""

    def test_real_onscreen_disclosures_recognized_without_fake_sales(self):
        a = audit_digital_offer(self.html, site_id="microvault_paid")
        self.assertTrue(a["checked"])
        self.assertEqual(a["passing_signals"], 8)
        self.assertEqual(a["missing"], [])
        self.assertIsNone(a["sales_verified"])
        self.assertIsNone(a["customer_reviews_verified"])

    def test_script_metadata_cannot_fake_a_buyer_promise(self):
        source = '<html><body><h1>CSV</h1><script>5 € 29 € einmalig kaufen SMOKYCHARLY direkt herunterladen</script></body></html>'
        a = audit_digital_offer(source, site_id="microvault_paid")
        for signal in ("visible_once_offers", "purchase_call_to_action",
                       "fulfillment_expectations", "provider_identity_visible"):
            self.assertFalse(a["signals"][signal])
        self.assertIsNone(a["sales_verified"])

    def test_unrelated_sites_are_not_graded_as_paid_csv(self):
        a = audit_digital_offer(self.html, site_id="ai_app_rescue")
        self.assertFalse(a["checked"])
        self.assertEqual(a["signals"], {})

    def test_missing_buyer_disclosures_create_just_one_safe_growth_task(self):
        config = {
            "schema": "titanius.control_center.v1",
            "brain": "TITANIUS_CERBERRUS",
            "agents": [{"id": x} for x in (
                "finance_intelligence","commerce_brain","delivery_brain","growth_brain",
                "design_brain","security_brain","learning_brain","operations_brain")],
            "sites": [{"id": "microvault_paid", "owner": "commerce",
                       "url": "https://microvault.floot.app/csv-report-kaufen", "required": []}],
        }
        result = run_cycle(config, lambda url:{
            "status": 200, "ok": True, "reason": None, "html":
                "<!doctype html><html><body><h1>CSV</h1><p>Produktseite</p></body></html>"})
        tasks = [task for task in result["tasks"] if task["agent"] == "growth_brain"]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["permission"], "review")
        self.assertNotIn("send email", tasks[0]["next_action"].lower())
        self.assertIsNone(result["finance"]["verified_net_revenue_eur"])
        self.assertEqual(result["activity"]["customer_messages"], 0)

    def test_complete_page_produces_no_unnecessary_growth_task(self):
        config = {
            "schema": "titanius.control_center.v1",
            "brain": "TITANIUS_CERBERRUS",
            "agents": [{"id": x} for x in (
                "finance_intelligence","commerce_brain","delivery_brain","growth_brain",
                "design_brain","security_brain","learning_brain","operations_brain")],
            "sites": [{"id": "microvault_paid", "owner": "commerce",
                       "url": "https://microvault.floot.app/csv-report-kaufen", "required": []}],
        }
        result = run_cycle(config, lambda url:{
            "status": 200, "ok": True, "reason": None, "html":self.html})
        self.assertEqual([task for task in result["tasks"] if task["agent"]=="growth_brain"], [])
        self.assertEqual(result["snapshot"]["microvault_paid"]["marketing_signals"], 8)


if __name__ == "__main__":
    unittest.main()
