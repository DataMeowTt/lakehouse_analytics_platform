import uuid

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

GENERATOR_RUN_ID = str(uuid.uuid4())
LOOKUP_PATH = "gs://lakehouse-analytics-raw-bronze/lookup"

payment_type_dist = (
    spark.read.option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{LOOKUP_PATH}/payment_type_distribution.csv")
    .orderBy(F.desc("pct"))
    .collect()
)

type_ranges = []
cum = 0.0
for row in payment_type_dist:
    lo = cum
    cum += row["pct"]
    type_ranges.append((row["payment_type"], lo, cum))

rand_type = F.rand(seed=31)
payment_type_expr = F.lit(type_ranges[-1][0])
for ptype, lo, hi in type_ranges:
    payment_type_expr = F.when(
        (rand_type >= lo) & (rand_type < hi), F.lit(ptype)
    ).otherwise(payment_type_expr)

order_totals = (
    spark.table("retail_lakehouse.bronze.fact_order_items")
    .groupBy("order_id")
    .agg(F.sum("price").alias("payment_value"))
)

fact_payments = (
    order_totals.withColumn("payment_sequential", F.lit(1))
    .withColumn("payment_type", payment_type_expr)
    .withColumn("payment_installments", (F.rand(seed=41) * 12).cast("int") + 1)
    .withColumn("_generated_at", F.current_timestamp())
    .withColumn("_generator_run_id", F.lit(GENERATOR_RUN_ID))
)

fact_payments.write.format("delta").mode("overwrite").option(
    "path", "gs://lakehouse-analytics-raw-bronze/bronze/fact_payments"
).saveAsTable("retail_lakehouse.bronze.fact_payments")
