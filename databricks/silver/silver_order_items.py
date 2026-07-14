from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

silver_order_items = (
    spark.table("retail_lakehouse.bronze.fact_order_items")
    .dropDuplicates(["order_id", "order_item_id"])
    .select(
        F.col("order_id").cast("string"),
        F.col("order_item_id").cast("int"),
        F.col("product_id").cast("string"),
        F.col("seller_id").cast("string"),
        F.col("price").cast("double"),
        F.col("_generated_at"),
        F.col("_generator_run_id"),
    )
)

(
    silver_order_items.write.format("delta")
    .mode("overwrite")
    .clusterBy("order_id")
    .option("path", "gs://lakehouse-analytics-raw-bronze/silver/order_items")
    .saveAsTable("retail_lakehouse.silver.order_items")
)
