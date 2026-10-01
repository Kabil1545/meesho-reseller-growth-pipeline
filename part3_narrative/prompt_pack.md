# Prompt pack: flagged-category stakeholder update

## 1. Trigger
Start this prompt only when a category's `is_flagged(mom_pct)` result is **`"flagged"`**
(i.e. `abs(mom_pct) > 8.0`). Never trigger it for `"not_flagged"`. For
`"escalate_exact_boundary"` do **not** draft; hand the category to a human for review.

## 2. Input list
Every placeholder below must be supplied from Part 1 / Part 2 output (no manual typing of figures):

| Placeholder | Meaning | Source |
|---|---|---|
| `{category}` | Category name, e.g. Ethnic Wear | Part 1 `monthly_category_revenue.csv` |
| `{month}` | Current month, e.g. May | feed |
| `{prev_month}` | Prior month, e.g. April | feed |
| `{previous_revenue}` | Prior-month revenue (INR) | Part 1 |
| `{current_revenue}` | Current-month revenue (INR) | Part 1 |
| `{mom_pct}` | Month-on-Month growth % | Part 2 `mom_growth` |

## 3. Prompt
```
You are drafting a short update for a Meesho regional category manager.
Category: [category]. [month] revenue vs [prev_month]: INR [previous_revenue] -> INR [current_revenue] ([mom_pct]% month-on-month).
Write three labelled parts: Context, Insight, Implication.
Rules: use ONLY the numbers given above and never state any other number; label the Insight as FACT;
label any proposed cause as HYPOTHESIS; end with one specific next step (what to check, and who checks it);
write for a non-technical manager; do not name any individual reseller (use aliases only).
```
Offline implementation: `part3_narrative/narrative.py` (`fill_prompt` renders this prompt;
`draft_message` is the deterministic template-fill used by the agent - no LLM or API key needed).

## 4. Checklist (run on every draft before use)
1. **Numbers exact:** every number in the draft equals a supplied placeholder value exactly (category revenues, `mom_pct`); no extra figures.
2. **Fact vs hypothesis:** the Insight is labelled FACT; any proposed cause is labelled HYPOTHESIS.
3. **Actionable:** the Implication names a concrete next step (what to check, who checks it), not "look into it".
4. **Correct labels:** category name, month and prior month are correct and the direction (up/down) matches the sign of `mom_pct`.
5. **Masked:** any reseller is referenced only as region + `alias_for(reseller_id)`; `assert_no_raw_names_leak` returns True.
6. **Audience fit & status:** plain language for a regional manager, and the draft is marked "held for human approval".
