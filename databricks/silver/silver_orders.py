from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

silver_orders = (
    spark.table("retail_lakehouse.bronze.fact_orders")
    .dropDuplicates(["order_id"])
    .select(
        F.col("order_id").cast("string"),
        F.col("customer_unique_id").cast("string"),
        F.col("order_status").cast("string"),
        F.col("order_purchase_timestamp").cast("timestamp"),
        F.col("order_purchase_date").cast("date"),
        # order_approved_at null hợp lệ khi status = created (chưa duyệt)
        F.col("order_approved_at").cast("timestamp"),
        # order_delivered_carrier_date null hợp lệ khi đơn chưa được giao cho vận chuyển
        F.col("order_delivered_carrier_date").cast("timestamp"),
        # order_delivered_customer_date null hợp lệ khi đơn chưa giao tới khách (status != delivered)
        F.col("order_delivered_customer_date").cast("timestamp"),
        F.col("order_estimated_delivery_date").cast("timestamp"),
        F.col("_generated_at"),
        F.col("_generator_run_id"),
    )
)

(
    silver_orders.write.format("delta")
    .mode("overwrite")
    .clusterBy("customer_unique_id", "order_purchase_date")
    .option("path", "gs://lakehouse-analytics-raw-bronze/silver/orders")
    .saveAsTable("retail_lakehouse.silver.orders")
)
