// Visualize the full co-purchase graph (small enough to render all at once).
MATCH (p1:Product)-[r:CO_PURCHASED_WITH]-(p2:Product)
RETURN p1, r, p2
