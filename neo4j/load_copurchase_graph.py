import csv
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USER = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

PRODUCTS_CSV = "../data/neo4j/top_products.csv"
EDGES_CSV = "../data/neo4j/copurchase_edges.csv"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def load_products(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (p:Product {product_id: row.product_id})
        SET p.category = row.category, p.order_count = toInteger(row.order_count)
        """,
        rows=rows,
    )


def load_edges(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (p1:Product {product_id: row.product_id_1})
        MATCH (p2:Product {product_id: row.product_id_2})
        MERGE (p1)-[r:CO_PURCHASED_WITH]->(p2)
        SET r.weight = toInteger(row.weight)
        """,
        rows=rows,
    )


with open(PRODUCTS_CSV) as f:
    products = list(csv.DictReader(f))

with open(EDGES_CSV) as f:
    edges = list(csv.DictReader(f))

with driver.session() as session:
    session.execute_write(load_products, products)
    session.execute_write(load_edges, edges)

driver.close()
print(f"Loaded {len(products)} products, {len(edges)} co-purchase relationships")
