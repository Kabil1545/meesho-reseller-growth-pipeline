"""Part 2 - Guardrail & growth-detection engine.

Turns "significant change" into an explicit, testable rule:
  * mom_growth   - Month-on-Month growth percentage
  * is_flagged   - three-way decision (never a bare boolean)
  * validate_feed - input guardrail over a month,category,revenue,n_orders CSV
Standard library only. Reused unmodified by Part 4.
"""
import csv
import math

DEFAULT_THRESHOLD = 8.0


def mom_growth(previous: float, current: float) -> float:
    """Month-on-Month growth in percent, rounded to 2 decimals."""
    if previous == 0:
        raise ValueError("previous revenue is 0; MoM growth is undefined")
    return round((current - previous) / previous * 100, 2)


def is_flagged(mom_pct: float, threshold: float = DEFAULT_THRESHOLD) -> str:
    """'flagged' | 'not_flagged' | 'escalate_exact_boundary' (held for human review)."""
    size = abs(mom_pct)
    if size > threshold:
        return "flagged"
    if size < threshold:
        return "not_flagged"
    return "escalate_exact_boundary"


def validate_feed(csv_path: str) -> "tuple[bool, list[str]]":
    """Validate a month,category,revenue,n_orders CSV. Line 1 is the header."""
    errors = []
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header = line 1
        for line_no, row in enumerate(reader, start=2):
            if not any(cell.strip() for cell in row):
                continue  # fully blank line
            row = (row + ["", "", "", ""])[:4]
            month, category, revenue, _n_orders = (c.strip() for c in row)

            if category == "":
                errors.append(f"line {line_no}: missing category (month={month})")
            if revenue == "":
                errors.append(f"line {line_no}: missing revenue (category={category})")
                continue
            try:
                value = float(revenue)
                if not math.isfinite(value):
                    raise ValueError
            except ValueError:
                errors.append(f"line {line_no}: revenue not numeric: {revenue!r}")
                continue
            if value < 0:
                errors.append(f"line {line_no}: negative revenue ({value}) for category={category}")
    return (len(errors) == 0, errors)
