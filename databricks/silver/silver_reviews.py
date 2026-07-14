from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

silver_reviews = (
    spark.table("retail_lakehouse.bronze.fact_reviews")
    .dropDuplicates(["review_id"])
    .select(
        F.col("review_id").cast("string"),
        F.col("order_id").cast("string"),
        F.col("review_score").cast("int"),
        F.col("_generated_at"),
        F.col("_generator_run_id"),
    )
)

(
    silver_reviews.write.format("delta")
    .mode("overwrite")
    .clusterBy("order_id")
    .option("path", "gs://lakehouse-analytics-raw-bronze/silver/reviews")
    .saveAsTable("retail_lakehouse.silver.reviews")
)
