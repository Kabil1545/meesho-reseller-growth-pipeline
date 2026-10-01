"""Part 3 - offline, deterministic template-fill for the prompt pack.

`fill_prompt` renders the prompt text from prompt_pack.md (usable with any LLM, optional).
`draft_message` is the offline "AI narrative" step used by the Part 4 agent: it fills a
Context -> Insight -> Implication template using ONLY the supplied values, so no number
can be invented. Standard library only; no API key.
"""

PROMPT_TEMPLATE = """You are drafting a short update for a Meesho regional category manager.
Category: {category}. {month} revenue vs {prev_month}: INR {previous_revenue} -> INR {current_revenue} ({mom_pct}% month-on-month).
Write three labelled parts: Context, Insight, Implication.
Rules: use ONLY the numbers given above and never state any other number; label the Insight as FACT;
label any proposed cause as HYPOTHESIS; end with one specific next step (what to check, and who checks it);
write for a non-technical manager; do not name any individual reseller (use aliases only)."""

_IMPLICATION = {
    "up": ("HYPOTHESIS: the rise may come from a demand spike, a promotion or a few high-volume resellers; "
           "the data alone does not prove which. Next step: the category manager should check which resellers "
           "and regions drove the increase and confirm that stock and fulfilment can sustain it."),
    "down": ("HYPOTHESIS: the fall may be a fade-out of the previous month's spike, reduced reseller activity "
             "or stock gaps; the data alone does not prove which. Next step: the category manager should compare "
             "active resellers and cancel/return rates in {category} across the two months before changing targets."),
}


def fill_prompt(category, month, prev_month, previous_revenue, current_revenue, mom_pct) -> str:
    return PROMPT_TEMPLATE.format(category=category, month=month, prev_month=prev_month,
                                  previous_revenue=previous_revenue, current_revenue=current_revenue,
                                  mom_pct=mom_pct)


def draft_message(category, month, prev_month, previous_revenue, current_revenue, mom_pct) -> str:
    direction = "up" if mom_pct > 0 else "down"
    return (
        f"Context: {category} revenue in {month} compared with {prev_month}.\n"
        f"Insight (FACT): {category} revenue moved from INR {previous_revenue} in {prev_month} to "
        f"INR {current_revenue} in {month}, a change of {mom_pct}% month-on-month.\n"
        f"Implication: " + _IMPLICATION[direction].format(category=category) + "\n"
        "Status: DRAFT - held for human approval, not sent."
    )
