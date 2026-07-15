// Top product pairs most frequently bought together
MATCH (p1:Product)-[r:CO_PURCHASED_WITH]->(p2:Product)
RETURN p1.product_id AS product_1, p1.category AS category_1,
       p2.product_id AS product_2, p2.category AS category_2,
       r.weight AS times_bought_together
ORDER BY r.weight DESC
LIMIT 20
