"""Agent-level tests.  Run: python -m unittest part4_agent.test_mock_agent_runner -v"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mock_agent_runner as m  # noqa: E402

FEED = str(HERE.parent / "part1_sql" / "output" / "monthly_category_revenue.csv")
BAD = str(HERE.parent / "part2_engine" / "fixtures" / "corrupted_feed.csv")
KEYS = ["run_month", "validation_status", "validation_errors", "flagged_categories",
        "suppressed_categories", "escalated_categories", "action_taken"]


class TestAgent(unittest.TestCase):
    def test_may(self):
        r = m.run("May", FEED, FEED)
        self.assertEqual(list(r), KEYS)
        self.assertEqual(r["validation_status"], "valid")
        self.assertEqual([(d["category"], d["mom_pct"]) for d in r["flagged_categories"]],
                         [("Ethnic Wear", 77.1), ("Western Wear", -23.6), ("Kids Wear", -23.48)])
        self.assertTrue(all(d["drafted"] for d in r["flagged_categories"]))
        self.assertEqual(sorted(r["suppressed_categories"]), ["Beauty & Personal Care", "Home & Kitchen"])
        self.assertEqual(r["escalated_categories"], [])
        self.assertEqual(r["action_taken"], "drafted_and_held_for_approval")

    def test_june(self):
        r = m.run("June", FEED, FEED)
        self.assertEqual([(d["category"], d["mom_pct"]) for d in r["flagged_categories"]],
                         [("Ethnic Wear", -58.74), ("Home & Kitchen", 42.59), ("Kids Wear", 23.9)])
        self.assertEqual(r["suppressed_categories"], ["Western Wear"])
        names = [d["category"] for d in r["flagged_categories"]] + r["suppressed_categories"]
        self.assertNotIn("Beauty & Personal Care", names)
        self.assertEqual(r["escalated_categories"], [])

    def test_corrupted_hard_stop(self):
        r = m.run("July", FEED, BAD)
        self.assertEqual(r["validation_status"], "invalid")
        self.assertEqual(r["action_taken"], "hard_stop")
        self.assertEqual(r["validation_errors"], [
            "line 3: negative revenue (-4200.0) for category=Western Wear",
            "line 4: missing category (month=July)",
            "line 6: missing revenue (category=Home & Kitchen)"])
        self.assertEqual(r["flagged_categories"], [])
        self.assertEqual(r["suppressed_categories"], [])

    def test_messages_only_traceable_numbers(self):
        for month in ("May", "June"):
            r = m.run(month, FEED, FEED)
            for d in r["flagged_categories"]:
                msg = d["message"]
                self.assertIn(d["category"], msg)
                self.assertIn(f'{d["mom_pct"]}%', msg)
                allowed = {str(d["mom_pct"]).lstrip("-"), str(d["previous_revenue"]), str(d["current_revenue"])}
                for num in re.findall(r"\d+(?:\.\d+)?", msg):
                    self.assertIn(num, allowed)

    def test_exact_boundary_is_escalated_not_dropped(self):
        with tempfile.TemporaryDirectory() as d:
            r = m._boundary_scenario(Path(d))
        self.assertEqual(r["escalated_categories"], ["Ethnic Wear"])
        self.assertEqual(r["flagged_categories"], [])
        self.assertEqual(r["suppressed_categories"], [])


if __name__ == "__main__":
    unittest.main()
