import unittest
from workflows.world_reach import assess_world, BASE, LOCALES, read_owned_page

def valid(url):
    locale = next(locale for locale, path in LOCALES if BASE + path == url)
    html = '<html lang="' + locale + '"><head><link rel="canonical" href="' + url + '"></head><body><a href="https://microvault.floot.app/">Tool</a></body></html>'
    return {"status": 200, "html": html}

class WorldReachTests(unittest.TestCase):
    def test_localized_pages_not_equal_buyers(self):
        result = assess_world(valid)
        self.assertEqual(result["reachable_pages"], 7)
        self.assertEqual(result["decision"], "CONNECT_MEASURED_ACQUISITION")
        self.assertIsNone(result["qualifying_visitors"])
        self.assertIsNone(result["verified_paid_buyers"])
        self.assertFalse(result["reflection"]["self_correction_from_market_outcomes_proven"])

    def test_offline_site_precedes_growth(self):
        def fetch(url):
            return {"status": 404, "html": ""} if url.endswith("/ja/") else valid(url)
        result = assess_world(fetch)
        self.assertEqual(result["decision"], "REPAIR_PUBLIC_REACHABILITY")
        self.assertEqual(result["unreachable_locales"], ["ja"])

    def test_bad_canonical_precedes_growth(self):
        def fetch(url):
            info = valid(url)
            if url.endswith("/fr/"):
                info["html"] = '<html lang="fr">French</html>'
            return info
        result = assess_world(fetch)
        self.assertEqual(result["decision"], "REPAIR_LOCALIZATION_AND_HANDOFF")
        self.assertIn("fr", result["metadata_or_handoff_gaps"])

    def test_repeated_checks_not_fabricated_learning(self):
        first = assess_world(valid)
        second = assess_world(valid, first)
        self.assertEqual(second["changed_public_surfaces"], 0)
        self.assertEqual(second["reflection"]["L5_learning_gate"], "BLOCKED_NO_OUTCOME_PAIRS")

    def test_only_approved_urls(self):
        with self.assertRaises(ValueError):
            read_owned_page("https://example.com/")

if __name__ == "__main__":
    unittest.main()
