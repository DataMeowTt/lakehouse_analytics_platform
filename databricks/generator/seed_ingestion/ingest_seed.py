from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

SEED_PATH = "gs://lakehouse-analytics-raw-bronze/seed"
BRONZE_PATH = "gs://lakehouse-analytics-raw-bronze/bronze"
CATALOG = "retail_lakehouse"
SCHEMA = "bronze"

SEED_FILES = {
    "seed_customers": "olist_customers_dataset.csv",
    "seed_orders": "olist_orders_dataset.csv",
    "seed_order_items": "olist_order_items_dataset.csv",
    "seed_payments": "olist_order_payments_dataset.csv",
    "seed_reviews": "olist_order_reviews_dataset.csv",
    "seed_products": "olist_products_dataset.csv",
    "seed_sellers": "olist_sellers_dataset.csv",
    "seed_geolocation": "olist_geolocation_dataset.csv",
    "seed_category_translation": "product_category_name_translation.csv",
}

for table_name, file_name in SEED_FILES.items():
    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(f"{SEED_PATH}/{file_name}")
    )
    df.write.format("delta").mode("overwrite").option(
        "path", f"{BRONZE_PATH}/{table_name}"
    ).saveAsTable(f"{CATALOG}.{SCHEMA}.{table_name}")
