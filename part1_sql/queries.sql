-- Part 1: SQL Business Query Engine (SQLite).
-- Each block starts with "-- name: <output_file_stem>"; run_queries.py executes
-- every block and writes part1_sql/output/<name>.csv

-- name: monthly_category_revenue
-- Q1. Monthly revenue by category (also the direct input to Part 2 and Part 4).
SELECT month,
       category,
       ROUND(SUM(quantity * unit_price), 2) AS revenue,
       COUNT(*)                             AS n_orders
FROM orders
GROUP BY month, category
ORDER BY CASE month WHEN 'April' THEN 1 WHEN 'May' THEN 2 WHEN 'June' THEN 3 END,
         CASE category WHEN 'Ethnic Wear' THEN 1 WHEN 'Western Wear' THEN 2
                       WHEN 'Kids Wear' THEN 3 WHEN 'Home & Kitchen' THEN 4
                       WHEN 'Beauty & Personal Care' THEN 5 END;

-- name: region_revenue
-- Q2. Region-wise total revenue and order count.
SELECT r.region,
       ROUND(SUM(o.quantity * o.unit_price), 2) AS total_revenue,
       COUNT(*)                                 AS n_orders
FROM orders o
JOIN resellers r ON r.reseller_id = o.reseller_id
GROUP BY r.region
ORDER BY total_revenue DESC;

-- name: top_resellers
-- Q3. Top resellers by total spend (> 50000), highest first, max 5.
SELECT r.reseller_id,
       r.reseller_name,
       r.region,
       ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend
FROM orders o
JOIN resellers r ON r.reseller_id = o.reseller_id
GROUP BY r.reseller_id
HAVING total_spend > 50000
ORDER BY total_spend DESC
LIMIT 5;

-- name: resellers_never_ordered
-- Q4a. Resellers with zero matching order rows: LEFT JOIN + IS NULL on the right-side key.
SELECT r.reseller_id, r.reseller_name, r.region
FROM resellers r
LEFT JOIN orders o ON o.reseller_id = r.reseller_id
WHERE o.order_id IS NULL;

-- name: count_star_vs_count_order_id
-- Q4b. Why COUNT(*) cannot detect the zero-match case:
-- for an unmatched reseller the LEFT JOIN still emits ONE row whose order columns are all NULL.
--   COUNT(*)        counts that row            -> 1 (wrong: the reseller has 0 orders)
--   COUNT(order_id) skips NULLs, counts 0 rows -> 0 (correct)
SELECT r.reseller_id,
       COUNT(*)          AS count_star,
       COUNT(o.order_id) AS count_order_id
FROM resellers r
LEFT JOIN orders o ON o.reseller_id = r.reseller_id
GROUP BY r.reseller_id
HAVING COUNT(o.order_id) = 0;

-- name: aov_june_delivered
-- Q5. Average Order Value, June, Delivered orders only.
SELECT ROUND(SUM(quantity * unit_price) / COUNT(*), 2) AS aov_june_delivered
FROM orders
WHERE month = 'June' AND status = 'Delivered';

-- name: grand_total
-- Sanity check: grand total across all 900 orders (equals the sum of the four regions).
SELECT ROUND(SUM(quantity * unit_price), 2) AS grand_total_revenue, COUNT(*) AS n_orders
FROM orders;
