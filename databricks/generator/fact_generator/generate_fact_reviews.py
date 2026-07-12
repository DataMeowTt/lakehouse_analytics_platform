import uuid

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()

GENERATOR_RUN_ID = str(uuid.uuid4())
LOOKUP_PATH = "gs://lakehouse-analytics-raw-bronze/lookup"

review_score_dist = (
    spark.read.option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{LOOKUP_PATH}/review_score_distribution.csv")
    .orderBy(F.desc("pct"))
    .collect()
)

score_ranges = []
cum = 0.0
for row in review_score_dist:
    lo = cum
    cum += row["pct"]
    score_ranges.append((row["review_score"], lo, cum))

rand_score = F.rand(seed=51)
review_score_expr = F.lit(score_ranges[-1][0])
for score, lo, hi in score_ranges:
    review_score_expr = F.when(
        (rand_score >= lo) & (rand_score < hi), F.lit(score)
    ).otherwise(review_score_expr)

fact_reviews = (
    spark.table("retail_lakehouse.bronze.fact_orders")
    .select("order_id")
    .withColumn("review_id", F.expr("uuid()"))
    .withColumn("review_score", review_score_expr)
    .withColumn("_generated_at", F.current_timestamp())
    .withColumn("_generator_run_id", F.lit(GENERATOR_RUN_ID))
)

fact_reviews.write.format("delta").mode("overwrite").option(
    "path", "gs://lakehouse-analytics-raw-bronze/bronze/fact_reviews"
).saveAsTable("retail_lakehouse.bronze.fact_reviews")
