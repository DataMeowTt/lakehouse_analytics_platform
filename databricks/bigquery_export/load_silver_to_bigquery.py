from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

PROJECT_ID = "lakehouse-analytics"
BQ_DATASET = "staging_raw"

SILVER_TABLES = [
    "orders",
    "customers",
    "products",
    "sellers",
    "order_items",
    "payments",
    "reviews",
]

for table_name in SILVER_TABLES:
    df = spark.table(f"retail_lakehouse.silver.{table_name}")
    (
        df.write.format("bigquery")
        .option("table", f"{PROJECT_ID}.{BQ_DATASET}.{table_name}")
        .option("writeMethod", "direct")
        .mode("overwrite")
        .save()
    )
