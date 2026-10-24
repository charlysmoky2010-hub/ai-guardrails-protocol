import unittest
from workflows.world_reach import assess_world

class WorldReachTests(unittest.TestCase):
    def test_unknown_paid_buyers(self):
        def offline(url):
            return {'status': 404, 'html': ''}
        result = assess_world(offline)
        self.assertIsNone(result['verified_paid_buyers'])
        self.assertEqual(result['decision'], 'REPAIR_PUBLIC_REACHABILITY')
        self.assertEqual(result['external_actions'], 0)
