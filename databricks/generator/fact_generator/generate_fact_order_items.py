import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.scale_tiers import N_PRODUCTS, N_SELLERS

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()

GENERATOR_RUN_ID = str(uuid.uuid4())
LOOKUP_PATH = "gs://lakehouse-analytics-raw-bronze/lookup"

category_price_stats = (
    spark.read.option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{LOOKUP_PATH}/category_price_stats.csv")
)

orders = spark.table("retail_lakehouse.bronze.fact_orders").select("order_id")

items = (
    orders.withColumn("n_items", (F.rand(seed=21) < F.lit(0.13)).cast("int") + 1)
    .withColumn("order_item_id", F.explode(F.expr("sequence(1, n_items)")))
    .drop("n_items")
    .withColumn("product_idx", (F.rand(seed=11) * N_PRODUCTS).cast("long"))
    .withColumn("seller_idx", (F.rand(seed=13) * N_SELLERS).cast("long"))
)

product_pool = spark.table("retail_lakehouse.bronze.dim_product_pool")
seller_pool = spark.table("retail_lakehouse.bronze.dim_seller_pool")

items = (
    items.join(
        product_pool.select("product_idx", "product_id", "product_category_name"),
        on="product_idx",
        how="left",
    )
    .join(seller_pool.select("seller_idx", "seller_id"), on="seller_idx", how="left")
    .join(category_price_stats, on="product_category_name", how="left")
)

fact_order_items = (
    items.withColumn(
        "price",
        F.greatest(F.lit(1.0), F.col("avg_price") + F.randn(seed=5) * F.col("stddev_price")),
    )
    .withColumn("_generated_at", F.current_timestamp())
    .withColumn("_generator_run_id", F.lit(GENERATOR_RUN_ID))
    .drop("product_idx", "seller_idx", "product_category_name", "avg_price", "stddev_price")
)

fact_order_items.write.format("delta").mode("overwrite").saveAsTable(
    "retail_lakehouse.bronze.fact_order_items"
)
