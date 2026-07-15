// "Hub" products — connected to the most other distinct products.
// Good candidates for a "Frequently bought with..." section on the product page.
MATCH (p:Product)-[r:CO_PURCHASED_WITH]-()
RETURN p.product_id AS product_id, p.category AS category, p.order_count AS total_orders, count(r) AS num_connections
ORDER BY num_connections DESC
LIMIT 10
