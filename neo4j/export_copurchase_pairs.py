from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()

TOP_N = 500
OUTPUT_PATH = "gs://lakehouse-analytics-raw-bronze/neo4j"

order_items = spark.table("retail_lakehouse.silver.order_items_seed")
products = spark.table("retail_lakehouse.silver.products_seed")

top_products = (
    order_items.groupBy("product_id")
    .count()
    .orderBy(F.desc("count"))
    .limit(TOP_N)
    .join(products, on="product_id", how="left")
    .select(
        "product_id",
        F.col("product_category_name_english").alias("category"),
        F.col("count").alias("order_count"),
    )
)

(
    top_products.coalesce(1)
    .write.mode("overwrite")
    .option("header", "true")
    .csv(f"{OUTPUT_PATH}/top_products")
)

filtered_items = order_items.join(
    F.broadcast(top_products.select("product_id")), on="product_id", how="inner"
).select("order_id", "product_id")

copurchase_pairs = (
    filtered_items.alias("a")
    .join(filtered_items.alias("b"), on="order_id")
    .where(F.col("a.product_id") < F.col("b.product_id"))
    .groupBy(
        F.col("a.product_id").alias("product_id_1"),
        F.col("b.product_id").alias("product_id_2"),
    )
    .count()
    .withColumnRenamed("count", "weight")
)

(
    copurchase_pairs.coalesce(1)
    .write.mode("overwrite")
    .option("header", "true")
    .csv(f"{OUTPUT_PATH}/copurchase_edges")
)
