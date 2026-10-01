# Narrative report (all figures from Part 1 / Part 2 output)

## 3.2 Worked narratives

### May - Ethnic Wear (+77.1% MoM, flagged)

**Context:** This update looks at how much money Ethnic Wear earned in May 2026 compared with April 2026, using Meesho's reseller order data.

**Insight (FACT):** Ethnic Wear revenue grew from INR 104520.77 in April to INR 185107.61 in May. That is a growth of 77.1% month-on-month, which is above the flagging limit, so this category is flagged.

**Implication:** HYPOTHESIS: this big jump may be because of a festive-season demand or a special offer on Ethnic Wear, but the data alone cannot prove the reason. Next step: the Ethnic Wear category manager should find out which resellers and which regions brought most of the extra sales, and check that stock and delivery can keep up with this level.

### June - Ethnic Wear (-58.74% MoM, flagged)

**Context:** This update looks at how much money Ethnic Wear earned in June 2026 compared with May 2026, using Meesho's reseller order data.

**Insight (FACT):** Ethnic Wear revenue dropped from INR 185107.61 in May to INR 76371.53 in June. That is a change of -58.74% month-on-month, which is above the flagging limit in the opposite direction, so this category is flagged.

**Implication:** HYPOTHESIS: the drop may be because May's high sales were a short-term spike that faded, or because fewer resellers were active or some stock was missing, but the data alone cannot prove which. Next step: the Ethnic Wear category manager should compare the number of active resellers and the cancellation and return rates for Ethnic Wear between May and June before changing any targets.

### Self-score against the 4-criterion refinement checklist (applies to both narratives)

| Criterion | Pass? | Why |
|---|---|---|
| Specificity | Pass | Each block names the exact category (Ethnic Wear), the exact months, both revenue values and the exact percentage (77.1% / -58.74%). |
| Audience fit | Pass | It is written in plain business language for a regional manager, with no SQL, code or statistical jargon. |
| Completeness | Pass | Each block has Context, Insight and Implication, in that order. |
| Actionability | Pass | Each Implication names a concrete check (resellers/regions driving the change; active resellers and cancel/return rates), assigns it to the category manager, and labels the cause as a hypothesis. |

### Top-reseller narrative (masked)
<!-- MASKED_NARRATIVE_START -->
Five resellers each spent more than INR 50000 across April to June 2026. The two highest are in the West region: ALIAS-19 (INR 75295.09) and ALIAS-22 (INR 73882.33). Next is ALIAS-12 in the South region (INR 69936.46), followed by two North-region resellers: ALIAS-06 (INR 64238.97) and ALIAS-05 (INR 61825.02). (FACT) Recommendation (HYPOTHESIS): the West region's two top spenders may be a sign of concentrated demand there; the regional manager should check whether these accounts have enough stock support and whether similar resellers in other regions can be onboarded the same way.
<!-- MASKED_NARRATIVE_END -->

Resellers are referenced only by region and `alias_for(reseller_id)`; `assert_no_raw_names_leak` returns True on the text above (tested in `test_part3.py`).

## 3.3 Chart-choice justification (text only; no images)

**Q1 - "Which month had the highest total revenue?" (April INR 419417.43, May INR 444594.25, June INR 398055.24).**
I would use a simple vertical bar (column) chart with one bar per month. This is a bivariate view (one categorical variable, month, against one numeric measure, revenue). Bars let the eye compare lengths, so the message "May is highest" is clear within 10 seconds. The y-axis must start at zero because the three totals are close together and a truncated axis would exaggerate small differences. There is a single series, so no legend is needed, and I would avoid 3D effects, which distort bar heights.

**Q2 - "What percentage share does Ethnic Wear represent of April's total revenue?" (INR 104520.77 of INR 419417.43 = 24.92%).**
This is a part-to-whole question about one measure (April revenue) split across categories, so I would use a two-slice donut (or a single 100% stacked bar): Ethnic Wear against all other categories, with "24.92%" labelled directly. With only two segments, the share is readable within 10 seconds, which is why a pie/donut is acceptable here but would not be for many slices. Direct labels replace a legend, since a legend is only needed when there are multiple series, and the chart must be flat, not 3D, because 3D tilt distorts slice areas.

**Q3 - "How do the four regions compare on total revenue?" (North INR 337125.46, West INR 333106.33, South INR 316736.68, East INR 275098.45).**
I would use a horizontal bar chart sorted from highest to lowest, one bar per region. This is a bivariate comparison (a categorical variable, region, against a numeric measure, revenue); sorting makes the ranking obvious in under 10 seconds. The x-axis (bar length) must start at zero so the lengths are honest, particularly because North and West are within INR 4019.13 of each other, so direct value labels on the bars help. One series means no legend, and no 3D.
