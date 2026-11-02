import unittest

from journey_patterns import PATTERNS, check


class JourneyTest(unittest.TestCase):
    def test_ten_patterns(self):
        self.assertEqual(len(PATTERNS), 10)

    def test_perfect_welcome(self):
        j = {"name": "x", "pattern": "welcome", "steps": PATTERNS["welcome"], "guards": ["exit_on_unsubscribe", "consent_check"]}
        self.assertEqual(check(j)["score"], 100)

    def test_order_matters(self):
        j = {"name": "x", "pattern": "welcome", "steps": ["preference_center", "email", "wait", "email", "trigger:signup"],
             "guards": ["exit_on_unsubscribe", "consent_check"]}
        self.assertIn("preference_center", check(j)["missing_steps"])

    def test_transactional_needs_no_consent_guard(self):
        j = {"name": "x", "pattern": "transactional", "steps": ["trigger:event", "email"], "guards": ["exit_on_unsubscribe"]}
        self.assertEqual(check(j)["score"], 100)


if __name__ == "__main__":
    unittest.main()
