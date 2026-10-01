"""Tests for masking and template-fill.  Run: python -m unittest part3_narrative.test_part3 -v"""
import csv
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from masking import alias_for, assert_no_raw_names_leak  # noqa: E402
from narrative import draft_message, fill_prompt  # noqa: E402


def reseller_names():
    with open(HERE.parent / "data" / "resellers.csv", newline="") as f:
        return [r["reseller_name"] for r in csv.DictReader(f)]


def masked_narrative():
    text = (HERE / "narrative_report.md").read_text()
    return re.search(r"<!-- MASKED_NARRATIVE_START -->(.*?)<!-- MASKED_NARRATIVE_END -->", text, re.S).group(1)


class TestMasking(unittest.TestCase):
    def test_alias(self):
        self.assertEqual(alias_for("RS019"), "ALIAS-19")
        self.assertEqual(alias_for("RS006"), "ALIAS-06")

    def test_final_narrative_has_no_leak(self):
        self.assertTrue(assert_no_raw_names_leak(masked_narrative(), reseller_names()))

    def test_negative_case_leak_detected(self):
        leaky = masked_narrative().replace("ALIAS-19", "Mumbai Reseller 1")
        self.assertIn("Mumbai Reseller 1", leaky)
        self.assertFalse(assert_no_raw_names_leak(leaky, reseller_names()))

    def test_whole_report_has_no_raw_names(self):
        full = (HERE / "narrative_report.md").read_text()
        self.assertTrue(assert_no_raw_names_leak(full, reseller_names()))


class TestTemplate(unittest.TestCase):
    def test_message_contains_category_and_exact_pct(self):
        m = draft_message("Ethnic Wear", "May", "April", 104520.77, 185107.61, 77.1)
        self.assertIn("Ethnic Wear", m)
        self.assertIn("77.1%", m)

    def test_prompt_has_all_placeholders_filled(self):
        p = fill_prompt("Ethnic Wear", "June", "May", 185107.61, 76371.53, -58.74)
        self.assertNotIn("{", p)
        self.assertIn("-58.74%", p)


if __name__ == "__main__":
    unittest.main()
