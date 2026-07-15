# Neo4j — Product Co-purchase Graph

Optional extension, outside the 5-week core roadmap in `step-to-step.md`. Builds a
"customers who bought X also bought Y" graph from real Olist order data, loaded into
Neo4j AuraDB, and explores it with a set of ready-made Cypher queries.

## Architecture

```
Silver (Databricks)                 Local (this machine)                 Neo4j AuraDB
silver.order_items_seed   ─┐
silver.products_seed      ─┘
        │
        ▼ export_copurchase_pairs.py (Spark, on Databricks)
gs://.../neo4j/top_products/
gs://.../neo4j/copurchase_edges/
        │
        ▼ download CSVs
data/neo4j/top_products.csv
data/neo4j/copurchase_edges.csv
        │
        ▼ load_copurchase_graph.py (Python, local)
                                                                    (:Product)-[:CO_PURCHASED_WITH]->(:Product)
```

`silver.order_items_seed` / `silver.products_seed` are built from the **real** Olist
seed CSVs (not the synthetic generator output) — see
`databricks/silver/silver_order_items_seed.py` and `silver_products_seed.py`. Using
real transaction data means the co-purchase signal is genuine, not random noise (the
synthetic generator assigns products to orders uniformly at random, so a graph built
from `silver.order_items`/`silver.products` would show no real pattern).

## Step 1 — Run the export (on Databricks)

Run `databricks/silver/silver_order_items_seed.py` and `silver_products_seed.py` once
(if not already done), then run this repo's `export_copurchase_pairs.py` on Databricks
(it uses PySpark — it will not run locally). This reads `silver.order_items_seed` /
`silver.products_seed`, keeps only the top 500 best-selling products (to stay within
Neo4j AuraDB Free tier limits — ~200K nodes / ~400K relationships), computes
co-purchase pairs, and writes two CSV folders to:

```
gs://lakehouse-analytics-raw-bronze/neo4j/top_products/
gs://lakehouse-analytics-raw-bronze/neo4j/copurchase_edges/
```

Download the two part files to this machine:

```bash
mkdir -p ../data/neo4j
gsutil cp gs://lakehouse-analytics-raw-bronze/neo4j/top_products/part-*.csv ../data/neo4j/top_products.csv
gsutil cp gs://lakehouse-analytics-raw-bronze/neo4j/copurchase_edges/part-*.csv ../data/neo4j/copurchase_edges.csv
```

## Step 2 — Run the load (locally)

1. Create a Neo4j AuraDB Free instance at https://console.neo4j.io
2. Copy `.env.example` to `.env` and fill in the connection details shown when the
   instance is created (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`). `.env` is
   gitignored — never commit it.
3. Install dependencies and run the loader:

```bash
conda activate dbt_prj_env
pip install -r ../requirements.txt
python load_copurchase_graph.py
```

Expected output: `Loaded 500 products, <N> co-purchase relationships`.

## Step 3 — Explore the graph

Open the Neo4j Aura **Query** tab and run the queries in `sql/` **in order** — paste
each file's contents into the query editor:

| File | What it shows |
|---|---|
| `sql/01_top_copurchase_pairs.sql` | The strongest product pairs — highest co-purchase count |
| `sql/02_same_vs_different_category.sql` | Whether co-purchases happen mostly within one category or across categories — signals whether cross-category cross-sell is worth pursuing |
| `sql/03_most_connected_products.sql` | "Hub" products connected to many others — good candidates for a "Frequently bought with..." widget |
| `sql/04_isolated_bestsellers.sql` | Best-sellers with zero co-purchase connections — products bought standalone, no accessory demand |
| `sql/05_visualize_full_graph.sql` | Renders the whole graph at once (small enough with only ~500 nodes) — look for disconnected clusters |

By default, node captions show the `category` property (multiple distinct products
share the same category, so several nodes will show identical text — that's expected,
not a bug: `product_id` distinguishes them). To change the caption, click the
`Product` badge in the results legend and switch the caption field to `product_id`.
There is no real product name field in the Olist dataset (only `product_name_lenght`,
a character count) — a text product name cannot be reconstructed from this data.

## Known limitation

The graph is intentionally capped at the top 500 products to fit Neo4j AuraDB's Free
tier limits (~200K nodes / ~400K relationships). Expanding coverage would require a
paid Aura tier or further sampling logic.
