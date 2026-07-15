from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

SEED_PATH = "gs://lakehouse-analytics-raw-bronze/seed/olist_order_items_dataset.csv"

silver_order_items_seed = (
    spark.read.option("header", "true").option("inferSchema", "true").csv(SEED_PATH)
    .dropDuplicates(["order_id", "order_item_id"])
    .select(
        F.col("order_id").cast("string"),
        F.col("order_item_id").cast("int"),
        F.col("product_id").cast("string"),
        F.col("seller_id").cast("string"),
        F.col("price").cast("double"),
    )
)

(
    silver_order_items_seed.write.format("delta")
    .mode("overwrite")
    .clusterBy("order_id")
    .option("path", "gs://lakehouse-analytics-raw-bronze/silver/order_items_seed")
    .saveAsTable("retail_lakehouse.silver.order_items_seed")
)
