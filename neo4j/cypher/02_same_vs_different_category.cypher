// Are co-purchases mostly within the same category or across different categories?
// If "Different category" dominates, cross-sell across categories is worth pursuing,
// not just similar-item recommendations.
MATCH (p1:Product)-[r:CO_PURCHASED_WITH]->(p2:Product)
RETURN
  CASE WHEN p1.category = p2.category THEN 'Same category' ELSE 'Different category' END AS pair_type,
  count(r) AS num_pairs,
  sum(r.weight) AS total_co_purchases
