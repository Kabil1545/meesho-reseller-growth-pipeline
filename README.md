# Meesho Reseller Growth & Alert Intelligence Pipeline

A small end-to-end monitoring pipeline: SQL layer -> Python guardrail/growth engine -> offline
AI-narrative layer -> guarded, human-reviewed mock agent.

**Zero API keys, no network, no paid services.** Everything runs offline with the Python 3
standard library (sqlite3, csv, json, unittest). The "AI narrative" is a deterministic template-fill.
Docs referenced: Python standard library docs for `sqlite3`, `csv`, `json`, `unittest`, `pathlib`.

## Run everything, in order (from the repo root)
```bash
# 0. Regenerate dataset (seed 42; do not change the script)
python data/generate_dataset.py          # writes resellers.csv, orders.csv, meesho_reseller.db

# 1. Part 1 - SQL queries -> part1_sql/output/*.csv
python part1_sql/run_queries.py

# 2. Part 2 - engine tests (uses fixtures/)
python -m unittest part2_engine.test_growth_engine -v

# 3. Part 3 - masking + template-fill tests
python -m unittest part3_narrative.test_part3 -v

# 4. Part 4 - mock agent: prints JSON and saves part4_agent/output/run_*.json
python part4_agent/mock_agent_runner.py all      # or: may | june | corrupted | boundary
python -m unittest part4_agent.test_mock_agent_runner -v

# Optional: run all tests at once
python -m unittest discover -s part2_engine -p "test_*.py" && \
python -m unittest discover -s part3_narrative -p "test_*.py" && \
python -m unittest discover -s part4_agent -p "test_*.py"
```

## How the Parts connect
`data/` -> **Part 1** `monthly_category_revenue.csv` -> **Part 2** `validate_feed` / `mom_growth` / `is_flagged`
(a copy is in `part2_engine/fixtures/`) -> **Part 3** template-fill (`narrative.py`) + masking ->
**Part 4** `mock_agent_runner.run(month, previous_month_csv, current_month_csv)` imports Part 2 unmodified and
Part 3's template, and emits one JSON object per run.

## Layout
```
data/                generate_dataset.py, resellers.csv, orders.csv, meesho_reseller.db
part1_sql/           queries.sql, run_queries.py, output/*.csv, output/README.md (COUNT(*) vs COUNT(col))
part2_engine/        growth_engine.py, test_growth_engine.py, fixtures/*.csv
part3_narrative/     prompt_pack.md, narrative_report.md, masking.py, narrative.py, test_part3.py
part4_agent/         agent_spec.md, mock_agent_runner.py, test_mock_agent_runner.py, output/run_*.json
```

## Workflow patterns each Part implements
- **Part 1 -> Part 2:** "compute real numbers via SQL first, then hand off" - numbers come from the database, never from a model.
- **Part 2:** explicit, testable rules and an input guardrail (validate before you act); exact-boundary cases escalate to a human.
- **Part 3:** Context -> Insight -> Implication narratives built from verified numbers, with a prompt pack and checklist (fact vs hypothesis) and masking of reseller names.
- **Part 4:** Intake -> Summary -> Report Draft -> Validate reporting flow, with Input/Action/Output guardrails, a 3-draft cap against notification flooding, Hard Stop on bad data, and human approval before anything is "sent".
