from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

silver_sellers = (
    spark.table("retail_lakehouse.bronze.dim_seller_pool")
    .dropDuplicates(["seller_id"])
    .select(
        F.col("seller_id").cast("string"),
        F.col("seller_zip_code_prefix").cast("string"),
        F.col("seller_city").cast("string"),
        F.col("seller_state").cast("string"),
    )
)

(
    silver_sellers.write.format("delta")
    .mode("overwrite")
    .clusterBy("seller_id")
    .option("path", "gs://lakehouse-analytics-raw-bronze/silver/sellers")
    .saveAsTable("retail_lakehouse.silver.sellers")
)
