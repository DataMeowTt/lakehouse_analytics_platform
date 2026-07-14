from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

fact_orders = spark.table("retail_lakehouse.bronze.fact_orders")
approved_offset_sec = (
    F.when(F.rand(seed=201) < 0.75, F.rand(seed=202) * 2).otherwise(F.rand(seed=203) * 72) * 3600
).cast("long")

carrier_offset_sec = (-F.log(1 - F.rand(seed=211)) * F.lit(2.8) * 86400).cast("long")
transit_offset_sec = (-F.log(1 - F.rand(seed=212)) * F.lit(9.33) * 86400).cast("long")
estimated_offset_sec = (
    F.greatest(F.lit(3.0), F.randn(seed=213) * F.lit(8.76) + F.lit(23.74)) * 86400
).cast("long")

purchase_epoch = F.unix_timestamp("order_purchase_timestamp")
approved_epoch = purchase_epoch + approved_offset_sec
carrier_epoch = approved_epoch + carrier_offset_sec
customer_epoch = carrier_epoch + transit_offset_sec
estimated_epoch = purchase_epoch + estimated_offset_sec

fact_orders_enriched = fact_orders.select(
    "*",
    F.when(F.col("order_status") == "created", F.lit(None).cast("timestamp"))
    .otherwise(F.timestamp_seconds(approved_epoch))
    .alias("order_approved_at"),
    F.when(
        F.col("order_status").isin("delivered", "shipped"),
        F.timestamp_seconds(carrier_epoch),
    )
    .otherwise(F.lit(None).cast("timestamp"))
    .alias("order_delivered_carrier_date"),
    F.when(F.col("order_status") == "delivered", F.timestamp_seconds(customer_epoch))
    .otherwise(F.lit(None).cast("timestamp"))
    .alias("order_delivered_customer_date"),
    F.timestamp_seconds(estimated_epoch).alias("order_estimated_delivery_date"),
)

(
    fact_orders_enriched.repartition("order_purchase_month")
    .write.format("delta")
    .partitionBy("order_purchase_month")
    .mode("overwrite")
    .option("mergeSchema", "true")
    .option("path", "gs://lakehouse-analytics-raw-bronze/bronze/fact_orders")
    .saveAsTable("retail_lakehouse.bronze.fact_orders")
)
