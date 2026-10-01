"""Given-When-Then tests for growth_engine.  Run:  python -m unittest part2_engine.test_growth_engine -v
(or: pytest part2_engine)"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from growth_engine import mom_growth, is_flagged, validate_feed  # noqa: E402

FIX = HERE / "fixtures"


class TestGrowthEngine(unittest.TestCase):
    def test_given_may_ethnic_wear_jump_when_evaluated_then_flagged(self):
        # GIVEN April -> May Ethnic Wear revenue 104520.77 -> 185107.61
        pct = mom_growth(104520.77, 185107.61)            # WHEN
        self.assertEqual(pct, 77.1)                       # THEN
        self.assertEqual(is_flagged(pct), "flagged")

    def test_given_june_beauty_small_move_when_evaluated_then_not_flagged(self):
        pct = mom_growth(35542.11, 37559.07)
        self.assertEqual(pct, 5.67)
        self.assertEqual(is_flagged(pct), "not_flagged")

    def test_given_exact_boundary_when_evaluated_then_escalate(self):
        pct = mom_growth(100000, 108000)
        self.assertEqual(pct, 8.0)
        self.assertEqual(is_flagged(pct), "escalate_exact_boundary")
        self.assertNotIn(is_flagged(pct), ("flagged", "not_flagged"))

    def test_given_negative_boundary_when_evaluated_then_escalate(self):
        self.assertEqual(is_flagged(-8.0), "escalate_exact_boundary")

    def test_given_corrupted_feed_when_validated_then_three_exact_errors(self):
        ok, errors = validate_feed(str(FIX / "corrupted_feed.csv"))
        self.assertFalse(ok)
        self.assertEqual(errors, [
            "line 3: negative revenue (-4200.0) for category=Western Wear",
            "line 4: missing category (month=July)",
            "line 6: missing revenue (category=Home & Kitchen)",
        ])

    def test_given_validated_part1_feed_when_validated_then_clean(self):
        self.assertEqual(validate_feed(str(FIX / "monthly_category_revenue.csv")), (True, []))

    def test_given_non_numeric_revenue_when_validated_then_reported(self):
        p = FIX.parent / "_tmp_bad.csv"
        p.write_text("month,category,revenue,n_orders\nJuly,Kids Wear,abc,5\n")
        try:
            ok, errors = validate_feed(str(p))
        finally:
            p.unlink()
        self.assertFalse(ok)
        self.assertEqual(errors, ["line 2: revenue not numeric: 'abc'"])

    def test_given_zero_previous_when_mom_growth_then_value_error(self):
        with self.assertRaises(ValueError):
            mom_growth(0, 100)

    def test_full_mom_tables_match_acceptance_criteria(self):
        import csv
        with open(FIX / "monthly_category_revenue.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        rev = {(r["month"], r["category"]): float(r["revenue"]) for r in rows}
        cats = ["Ethnic Wear", "Western Wear", "Kids Wear", "Home & Kitchen", "Beauty & Personal Care"]
        may = [mom_growth(rev[("April", c)], rev[("May", c)]) for c in cats]
        june = [mom_growth(rev[("May", c)], rev[("June", c)]) for c in cats]
        self.assertEqual(may, [77.1, -23.6, -23.48, -9.25, -12.75])
        self.assertEqual(june, [-58.74, 11.97, 23.9, 42.59, 5.67])
        self.assertEqual([is_flagged(p) for p in may].count("flagged"), 5)
        self.assertEqual([is_flagged(p) for p in june].count("flagged"), 4)


if __name__ == "__main__":
    unittest.main()
