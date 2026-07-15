from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", "8")

PRODUCTS_PATH = "gs://lakehouse-analytics-raw-bronze/seed/olist_products_dataset.csv"
TRANSLATION_PATH = "gs://lakehouse-analytics-raw-bronze/seed/product_category_name_translation.csv"

category_translation = (
    spark.read.option("header", "true")
    .option("inferSchema", "true")
    .csv(TRANSLATION_PATH)
)

silver_products_seed = (
    spark.read.option("header", "true").option("inferSchema", "true").csv(PRODUCTS_PATH)
    .dropDuplicates(["product_id"])
    .join(F.broadcast(category_translation), on="product_category_name", how="left")
    .select(
        F.col("product_id").cast("string"),
        F.col("product_category_name").cast("string"),
        F.col("product_category_name_english").cast("string"),
    )
)

(
    silver_products_seed.write.format("delta")
    .mode("overwrite")
    .clusterBy("product_id")
    .option("path", "gs://lakehouse-analytics-raw-bronze/silver/products_seed")
    .saveAsTable("retail_lakehouse.silver.products_seed")
)
