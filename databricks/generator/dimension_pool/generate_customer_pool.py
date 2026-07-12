import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.scale_tiers import N_CUSTOMERS

import pandas as pd
from faker import Faker
from pyspark.sql import SparkSession
from pyspark.sql.types import LongType, StringType, StructField, StructType

spark = SparkSession.builder.getOrCreate()

SCHEMA = StructType(
    [
        StructField("customer_idx", LongType()),
        StructField("customer_unique_id", StringType()),
        StructField("customer_zip_code_prefix", StringType()),
        StructField("customer_city", StringType()),
        StructField("customer_state", StringType()),
    ]
)


def generate_batch(pdf_iter):
    fake = Faker("pt_BR")
    for pdf in pdf_iter:
        n = len(pdf)
        yield pd.DataFrame(
            {
                "customer_idx": pdf["id"].values,
                "customer_unique_id": [fake.uuid4() for _ in range(n)],
                "customer_zip_code_prefix": [fake.postcode()[:5] for _ in range(n)],
                "customer_city": [fake.city() for _ in range(n)],
                "customer_state": [fake.estado_sigla() for _ in range(n)],
            }
        )


dim_customer_pool = spark.range(N_CUSTOMERS, numPartitions=200).mapInPandas(
    generate_batch, schema=SCHEMA
)

dim_customer_pool.write.format("delta").mode("overwrite").saveAsTable(
    "retail_lakehouse.bronze.dim_customer_pool"
)
