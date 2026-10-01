"""Part 4 - Mock agent runner: ties Parts 1-3 into one guarded, human-reviewed workflow.

run(month, previous_month_csv, current_month_csv) -> dict   (subtasks 1-8 of agent_spec.md)
Uses Part 2's growth_engine functions unmodified and Part 3's template-fill. No network,
no API key, no message sending: drafts are only produced and held for human approval.

CLI:  python part4_agent/mock_agent_runner.py [may|june|corrupted|boundary|all]
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "part2_engine"))
sys.path.insert(0, str(ROOT / "part3_narrative"))
from growth_engine import mom_growth, is_flagged, validate_feed  # noqa: E402
from narrative import draft_message  # noqa: E402

MONTH_ORDER = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
MAX_DRAFTS = 3  # notification-flooding cap


def _previous_month(month: str) -> str:
    return MONTH_ORDER[(MONTH_ORDER.index(month) - 1) % 12]


def _load_month(csv_path: str, month: str) -> dict:
    """category -> revenue for the rows of `month` (feed already validated)."""
    with open(csv_path, newline="") as f:
        return {r["category"]: float(r["revenue"]) for r in csv.DictReader(f) if r["month"] == month}


def _result(month, status, errors, flagged, suppressed, escalated, action):
    return {
        "run_month": month,
        "validation_status": status,
        "validation_errors": errors,
        "flagged_categories": flagged,
        "suppressed_categories": suppressed,
        "escalated_categories": escalated,
        "action_taken": action,
    }


def run(month: str, previous_month_csv: str, current_month_csv: str) -> dict:
    prev_month = _previous_month(month)

    # (1) load feeds and run validate_feed (input guardrail) on both
    errors = []
    for path in (previous_month_csv, current_month_csv):
        ok, errs = validate_feed(path)
        errors.extend(e for e in errs if e not in errors)

    # (2) invalid -> Hard Stop, errors surfaced, no MoM attempted
    if errors:
        return _result(month, "invalid", errors, [], [], [], "hard_stop")

    previous = _load_month(previous_month_csv, prev_month)
    current = _load_month(current_month_csv, month)
    missing = sorted(set(previous) ^ set(current)) or (["<all>"] if not current or not previous else [])
    if missing:
        errs = [f"feed mismatch: no matching {prev_month}/{month} rows for category={c}" for c in missing]
        return _result(month, "invalid", errs, [], [], [], "hard_stop")

    # (3) mom_growth for every category and (4) is_flagged for every category
    flagged, escalated = [], []
    for category in current:
        pct = mom_growth(previous[category], current[category])
        decision = is_flagged(pct)
        if decision == "flagged":
            flagged.append((category, pct))
        elif decision == "escalate_exact_boundary":
            escalated.append(category)  # (7b) never drafted, never silently dropped

    # (5) sort flagged by abs(mom_pct) descending
    flagged.sort(key=lambda x: abs(x[1]), reverse=True)

    # (6) draft for at most the top 3; (7) suppress the rest
    drafted = []
    for category, pct in flagged[:MAX_DRAFTS]:
        drafted.append({
            "category": category,
            "mom_pct": pct,
            "previous_revenue": previous[category],
            "current_revenue": current[category],
            "drafted": True,
            "message": draft_message(category, month, prev_month, previous[category], current[category], pct),
        })
    suppressed = [c for c, _ in flagged[MAX_DRAFTS:]]

    # (8) one structured JSON-able object per run
    return _result(month, "valid", [], drafted, suppressed, escalated, "drafted_and_held_for_approval")


def _scenarios():
    feed = str(ROOT / "part1_sql" / "output" / "monthly_category_revenue.csv")
    bad = str(ROOT / "part2_engine" / "fixtures" / "corrupted_feed.csv")
    return {
        "may": ("May", feed, feed),
        "june": ("June", feed, feed),
        "corrupted": ("July", feed, bad),
    }


def _boundary_scenario(tmp_dir: Path) -> dict:
    """Synthetic exact-8.0% case: previous 100000 -> current 108000."""
    prev = tmp_dir / "boundary_prev.csv"
    cur = tmp_dir / "boundary_cur.csv"
    prev.write_text("month,category,revenue,n_orders\nJune,Ethnic Wear,100000.00,10\n")
    cur.write_text("month,category,revenue,n_orders\nJuly,Ethnic Wear,108000.00,10\n")
    return run("July", str(prev), str(cur))


def main(argv):
    which = argv[1].lower() if len(argv) > 1 else "all"
    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(exist_ok=True)
    scenarios = _scenarios()
    names = list(scenarios) + ["boundary"] if which == "all" else [which]
    for name in names:
        result = _boundary_scenario(out_dir) if name == "boundary" else run(*scenarios[name])
        if name == "boundary":
            for f in ("boundary_prev.csv", "boundary_cur.csv"):
                (out_dir / f).unlink(missing_ok=True)
        text = json.dumps(result, indent=2)
        (out_dir / f"run_{name}.json").write_text(text + "\n")
        print(f"=== scenario: {name} ===\n{text}\n")


if __name__ == "__main__":
    main(sys.argv)
