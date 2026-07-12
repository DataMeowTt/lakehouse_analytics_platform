N_PRODUCTS = 50_000

import numpy as np
import pandas as pd
from faker import Faker
from pyspark.sql import SparkSession
from pyspark.sql.types import LongType, StringType, StructField, StructType

spark = SparkSession.builder.getOrCreate()

category_counts = (
    spark.table("retail_lakehouse.bronze.seed_products")
    .groupBy("product_category_name")
    .count()
    .dropna()
    .toPandas()
)
CATEGORIES = category_counts["product_category_name"].tolist()
PROBS = (category_counts["count"] / category_counts["count"].sum()).tolist()

categories_bc = spark.sparkContext.broadcast(CATEGORIES)
probs_bc = spark.sparkContext.broadcast(PROBS)

SCHEMA = StructType(
    [
        StructField("product_idx", LongType()),
        StructField("product_id", StringType()),
        StructField("product_category_name", StringType()),
    ]
)


def generate_batch(pdf_iter):
    fake = Faker()
    cats = categories_bc.value
    probs = probs_bc.value
    for pdf in pdf_iter:
        n = len(pdf)
        yield pd.DataFrame(
            {
                "product_idx": pdf["id"].values,
                "product_id": [fake.uuid4() for _ in range(n)],
                "product_category_name": np.random.choice(cats, size=n, p=probs),
            }
        )


dim_product_pool = spark.range(N_PRODUCTS, numPartitions=4).mapInPandas(
    generate_batch, schema=SCHEMA
)

dim_product_pool.write.format("delta").mode("overwrite").option(
    "path", "gs://lakehouse-analytics-raw-bronze/bronze/dim_product_pool"
).saveAsTable("retail_lakehouse.bronze.dim_product_pool")
