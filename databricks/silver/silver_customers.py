from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

silver_customers = (
    spark.table("retail_lakehouse.bronze.dim_customer_pool")
    .dropDuplicates(["customer_unique_id"])
    .select(
        F.col("customer_unique_id").cast("string"),
        F.col("customer_zip_code_prefix").cast("string"),
        F.col("customer_city").cast("string"),
        F.col("customer_state").cast("string"),
    )
)

(
    silver_customers.write.format("delta")
    .mode("overwrite")
    .clusterBy("customer_unique_id")
    .option("path", "gs://lakehouse-analytics-raw-bronze/silver/customers")
    .saveAsTable("retail_lakehouse.silver.customers")
)
