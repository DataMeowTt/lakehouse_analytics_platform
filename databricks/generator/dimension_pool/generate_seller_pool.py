N_SELLERS = 5_000

import pandas as pd
from faker import Faker
from pyspark.sql import SparkSession
from pyspark.sql.types import LongType, StringType, StructField, StructType

spark = SparkSession.builder.getOrCreate()

SCHEMA = StructType(
    [
        StructField("seller_idx", LongType()),
        StructField("seller_id", StringType()),
        StructField("seller_zip_code_prefix", StringType()),
        StructField("seller_city", StringType()),
        StructField("seller_state", StringType()),
    ]
)


def generate_batch(pdf_iter):
    fake = Faker("pt_BR")
    for pdf in pdf_iter:
        n = len(pdf)
        yield pd.DataFrame(
            {
                "seller_idx": pdf["id"].values,
                "seller_id": [fake.uuid4() for _ in range(n)],
                "seller_zip_code_prefix": [fake.postcode()[:5] for _ in range(n)],
                "seller_city": [fake.city() for _ in range(n)],
                "seller_state": [fake.estado_sigla() for _ in range(n)],
            }
        )


dim_seller_pool = spark.range(N_SELLERS, numPartitions=2).mapInPandas(
    generate_batch, schema=SCHEMA
)

dim_seller_pool.write.format("delta").mode("overwrite").option(
    "path", "gs://lakehouse-analytics-raw-bronze/bronze/dim_seller_pool"
).saveAsTable("retail_lakehouse.bronze.dim_seller_pool")
