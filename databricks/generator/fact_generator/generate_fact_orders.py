import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.scale_tiers import N_CUSTOMERS, N_ORDERS

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()

GENERATOR_RUN_ID = str(uuid.uuid4())
LOOKUP_PATH = "gs://lakehouse-analytics-raw-bronze/lookup"

order_status_dist = (
    spark.read.option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{LOOKUP_PATH}/order_status_distribution.csv")
    .orderBy("order_status")
    .collect()
)

status_ranges = []
cum = 0.0
for row in order_status_dist:
    lo = cum
    cum += row["pct"]
    status_ranges.append((row["order_status"], lo, cum))

rand_status = F.rand(seed=99)
order_status_expr = F.lit(status_ranges[-1][0])
for status, lo, hi in status_ranges:
    order_status_expr = F.when(
        (rand_status >= lo) & (rand_status < hi), F.lit(status)
    ).otherwise(order_status_expr)

orders_df = (
    spark.range(0, N_ORDERS, numPartitions=400)
    .withColumn("order_id", F.expr("uuid()"))
    .withColumn("customer_idx", (F.pow(F.rand(seed=42), 2) * N_CUSTOMERS).cast("long"))
    .withColumn(
        "order_purchase_timestamp",
        F.expr(
            """
            timestamp_seconds(
                unix_timestamp('2019-01-01') +
                cast(rand(3) * (unix_timestamp('2027-01-01') - unix_timestamp('2019-01-01')) as bigint)
            )
            """
        ),
    )
    .withColumn("order_purchase_date", F.to_date("order_purchase_timestamp"))
    .withColumn("order_status", order_status_expr)
    .withColumn("_generated_at", F.current_timestamp())
    .withColumn("_generator_run_id", F.lit(GENERATOR_RUN_ID))
    .drop("id")
)

customer_pool = spark.table("retail_lakehouse.bronze.dim_customer_pool")

fact_orders = orders_df.join(
    customer_pool.select("customer_idx", "customer_unique_id"),
    on="customer_idx",
    how="left",
).drop("customer_idx")

(
    fact_orders.write.format("delta")
    .partitionBy("order_purchase_date")
    .mode("overwrite")
    .saveAsTable("retail_lakehouse.bronze.fact_orders")
)
