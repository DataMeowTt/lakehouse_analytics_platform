// Best-selling products that are always bought alone (no co-purchase connections).
// Inverse insight: a strong seller with no accessory/companion-purchase demand.
MATCH (p:Product)
WHERE NOT (p)-[:CO_PURCHASED_WITH]-()
RETURN p.product_id, p.category, p.order_count
ORDER BY p.order_count DESC
LIMIT 10
