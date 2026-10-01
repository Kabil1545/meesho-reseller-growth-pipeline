# Agent specification: Category Growth Monitoring Agent

## 4.1 Five core components

**Goal:** Keep Meesho category managers informed of any category whose month-on-month revenue moves beyond the 8% threshold, with a human approving every message before it goes out.

**Tools:**
- `validate_feed(csv_path)`, `mom_growth(previous, current)`, `is_flagged(mom_pct, threshold=8.0)` (Part 2, `part2_engine/growth_engine.py`, used unmodified).
- `draft_message(...)` / `fill_prompt(...)` (Part 3, `part3_narrative/narrative.py`, the offline prompt-pack template-fill).
- Input data comes from Part 1's `monthly_category_revenue.csv`.

**Memory/State:** Between runs the agent must remember each category's previous-month revenue (to compute the next run's MoM), the month already processed, and the list of categories suppressed or escalated in the last run (so a human can follow up). In this mock the state is the previous-month feed CSV passed into `run()`.

**Planner:** The ordered subtasks in section 4.2.

**Feedback Loop:** Human approval checkpoint. Every draft is emitted with `action_taken = "drafted_and_held_for_approval"` and a "DRAFT - held for human approval, not sent" status line. Nothing is sent; "sent" is only ever a human decision after review (simulated as this flag; no Gmail/SMTP).

## Guardrails
- **Input guardrail:** `validate_feed` must pass on the feeds before anything else runs.
- **Action guardrail:** No message is ever auto-sent; messages are only drafted and held. At most 3 drafts per run (anti notification-flooding). Exact-boundary cases are never auto-decided.
- **Output guardrail:** Every number in a drafted message traces back to a Part 1 / Part 2 value (category revenues and `mom_pct`); the template-fill function takes only those values, so no figure can be invented. Resellers are referenced only via `alias_for` (Part 3 masking).

## Stopping conditions
- **Success:** Drafts produced (or correctly zero drafts if nothing crossed the threshold), every number traceable, and every flagged/suppressed/escalated category accounted for in the JSON.
- **Error:** `validate_feed` returns False. The run is a **Hard Stop** (`action_taken = "hard_stop"`) with `validation_errors` surfaced. It is never a silent skip, and no MoM is computed on invalid data.

## 4.2 Ordered subtasks (Planner)
1. Load the monthly revenue feed(s) and run `validate_feed`.
2. If invalid: Hard Stop and report the errors.
3. If valid: compute `mom_growth` for every category against the previous month.
4. Run `is_flagged` on every category.
5. Sort flagged categories by `abs(mom_pct)` descending.
6. Draft a message (via Part 3's template) for at most the top 3 by magnitude; the cap prevents notification flooding.
7. Log any remaining flagged categories as "suppressed, review manually" (in `suppressed_categories`) without drafting a message.
   - 7b. Separately, log every category whose result is `"escalate_exact_boundary"` into `escalated_categories`, without drafting. It is neither flagged nor not_flagged, so it is never silently dropped or mistaken for either.
8. Emit one structured JSON object per run.

## 4.3 JSON output schema
Exactly these top-level keys, on every run (success or Hard Stop):

```json
{
  "run_month": "May",
  "validation_status": "valid | invalid",
  "validation_errors": [],
  "flagged_categories": [
    {"category": "...", "mom_pct": 0.0, "previous_revenue": 0.0, "current_revenue": 0.0,
     "drafted": true, "message": "... (present when drafted)"}
  ],
  "suppressed_categories": [],
  "escalated_categories": [],
  "action_taken": "drafted_and_held_for_approval | hard_stop"
}
```
`escalated_categories` is `[]` in the May, June and corrupted-feed scenarios and is non-empty only for the synthetic 8.0% boundary case (`python part4_agent/mock_agent_runner.py boundary`).

## Given-When-Then specs (agent level)
1. **GIVEN** April to May Ethnic Wear revenue moves from 104520.77 to 185107.61, **WHEN** the agent evaluates it with `mom_growth` then `is_flagged`, **THEN** it records a growth of 77.1% and a result of "flagged", and drafts a held message for it.
2. **GIVEN** May to June Beauty & Personal Care revenue moves from 35542.11 to 37559.07, **WHEN** the agent evaluates it, **THEN** it records 5.67% and "not_flagged", and the category appears in neither `flagged_categories` nor `suppressed_categories`.
3. **GIVEN** a synthetic pair previous=100000, current=108000 (exactly on the threshold), **WHEN** the agent evaluates it, **THEN** it computes exactly 8.0% and "escalate_exact_boundary": the category goes to `escalated_categories`, not "flagged" and not "not_flagged", and no message is drafted.
4. **GIVEN** the corrupted feed fixture, **WHEN** the agent runs `validate_feed` on it, **THEN** it returns (False, errors) with exactly 3 entries (the negative-revenue row, the missing-category row, the missing-revenue row), and the run ends as a Hard Stop with no MoM computed.
