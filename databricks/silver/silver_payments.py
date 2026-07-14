from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

silver_payments = (
    spark.table("retail_lakehouse.bronze.fact_payments")
    .dropDuplicates(["order_id", "payment_sequential"])
    .select(
        F.col("order_id").cast("string"),
        F.col("payment_sequential").cast("int"),
        F.col("payment_type").cast("string"),
        F.col("payment_installments").cast("int"),
        F.col("payment_value").cast("double"),
        F.col("_generated_at"),
        F.col("_generator_run_id"),
    )
)

(
    silver_payments.write.format("delta")
    .mode("overwrite")
    .clusterBy("order_id")
    .option("path", "gs://lakehouse-analytics-raw-bronze/silver/payments")
    .saveAsTable("retail_lakehouse.silver.payments")
)
