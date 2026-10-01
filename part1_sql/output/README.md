# Part 1 output notes

All CSVs here are produced by `python part1_sql/run_queries.py` from `part1_sql/queries.sql`.

| File | Business question |
|---|---|
| `monthly_category_revenue.csv` | Q1 - revenue and order count by month x category (feeds Part 2 and Part 4) |
| `region_revenue.csv` | Q2 - total revenue and orders per region |
| `top_resellers.csv` | Q3 - resellers with total spend > 50000, top 5 |
| `resellers_never_ordered.csv` | Q4a - resellers with zero orders (RS024 only) |
| `count_star_vs_count_order_id.csv` | Q4b - COUNT(*) vs COUNT(order_id) demo for RS024 |
| `aov_june_delivered.csv` | Q5 - June Delivered AOV = INR 1267.69 |
| `grand_total.csv` | sanity check: INR 1262066.92 over 900 orders (= sum of the 4 regions) |

## Why COUNT(*) is the wrong way to detect a zero-match LEFT JOIN row

A `LEFT JOIN` keeps every reseller. When a reseller (RS024, "Ahmedabad Reseller 6") has no
orders, SQL still emits **one** joined row for it, with every `orders` column set to NULL.

* `COUNT(*)` counts rows, so it counts that single all-NULL row and returns **1**.
* `COUNT(order_id)` counts only non-NULL values, so it returns **0**.

`count_star_vs_count_order_id.csv` shows both in the same row: `RS024, count_star = 1, count_order_id = 0`.
So `COUNT(*) = 0` can never be true after a LEFT JOIN + GROUP BY, and a check built on it would
silently miss every reseller who has never ordered. Use `COUNT(o.order_id) = 0`
(or `WHERE o.order_id IS NULL`) instead.
