# Databricks notebook source
# MAGIC %md
# MAGIC # Olympic Data Analytics — Transformation Notebook
# MAGIC
# MAGIC **Purpose:** Load raw Olympic CSV files (Athletes, Coaches, Teams, EntriesGender, Medals),
# MAGIC clean and transform them with PySpark, model them into fact/dimension tables, and write
# MAGIC the curated output for downstream loading into Azure Synapse Analytics.
# MAGIC
# MAGIC **Input:** Raw CSVs uploaded to Databricks (DBFS / local `/data` folder)
# MAGIC **Output:** Delta tables (curated layer) ready to be loaded into Synapse

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, trim, initcap, count, sum as _sum, row_number, current_timestamp
)
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("OlympicDataAnalytics").getOrCreate()

# COMMAND ----------

# MAGIC %md ## 1. Load raw data
# MAGIC Files were uploaded directly into the Databricks File System (DBFS) for this project
# MAGIC (no ADF/ADLS ingestion step — data loaded straight from local source files).

# COMMAND ----------

RAW_PATH = "/dbfs/FileStore/olympic_data"  # adjust to your DBFS upload path

athletes_raw = spark.read.csv(f"{RAW_PATH}/Athletes.csv", header=True, inferSchema=True)
coaches_raw = spark.read.csv(f"{RAW_PATH}/Coaches.csv", header=True, inferSchema=True)
teams_raw = spark.read.csv(f"{RAW_PATH}/Teams.csv", header=True, inferSchema=True)
entries_gender_raw = spark.read.csv(f"{RAW_PATH}/EntriesGender.csv", header=True, inferSchema=True)
medals_raw = spark.read.csv(f"{RAW_PATH}/Medals.csv", header=True, inferSchema=True)

print("Row counts (raw):")
for name, df in [("Athletes", athletes_raw), ("Coaches", coaches_raw), ("Teams", teams_raw),
                  ("EntriesGender", entries_gender_raw), ("Medals", medals_raw)]:
    print(f"  {name}: {df.count()}")

# COMMAND ----------

# MAGIC %md ## 2. Data cleaning
# MAGIC Handle nulls, duplicates, and formatting inconsistencies found in the raw source files.

# COMMAND ----------

# --- Athletes: drop exact duplicates, fill missing country, drop rows with no birth_year ---
athletes_clean = (
    athletes_raw
    .dropDuplicates(["athlete_id"])
    .withColumn("country", when(col("country").isNull(), "Unknown").otherwise(trim(col("country"))))
    .withColumn("name", initcap(trim(col("name"))))
    .filter(col("birth_year").isNotNull())
    .withColumn("age_at_games", (2021 - col("birth_year")))  # example derived metric
)

# --- Coaches: fill missing event type ---
coaches_clean = (
    coaches_raw
    .withColumn("event", when(col("event").isNull(), "Unspecified").otherwise(col("event")))
    .withColumn("name", initcap(trim(col("name"))))
)

# --- Teams: straightforward pass-through with trimming ---
teams_clean = teams_raw.withColumn("team_name", trim(col("team_name")))

# --- EntriesGender: validate total = male + female, recompute if mismatched ---
entries_gender_clean = entries_gender_raw.withColumn(
    "total_validated", col("male") + col("female")
)

# --- Medals: recompute total & rank to guarantee consistency ---
window_spec = Window.orderBy(
    col("gold").desc(), col("silver").desc(), col("bronze").desc()
)
medals_clean = (
    medals_raw
    .withColumn("total_validated", col("gold") + col("silver") + col("bronze"))
    .withColumn("rank_recomputed", row_number().over(window_spec))
)

print("Row counts (cleaned):")
for name, df in [("Athletes", athletes_clean), ("Coaches", coaches_clean),
                  ("Teams", teams_clean)]:
    print(f"  {name}: {df.count()}")

# COMMAND ----------

# MAGIC %md ## 3. Data modeling — dimension & fact tables
# MAGIC Structuring the cleaned data into a simple star schema for analytical querying in Synapse.

# COMMAND ----------

# Dimension: Country
dim_country = (
    athletes_clean.select("country_code", "country").distinct()
)

# Dimension: Discipline
dim_discipline = (
    athletes_clean.select("discipline").distinct()
    .withColumnRenamed("discipline", "discipline_name")
)

# Dimension: Athlete
dim_athlete = athletes_clean.select(
    "athlete_id", "name", "gender", "country_code", "discipline", "birth_year", "age_at_games"
)

# Fact: Medal counts by country
fact_medals = medals_clean.select(
    "country_code", "country", "gold", "silver", "bronze",
    "total_validated", "rank_recomputed"
).withColumnRenamed("total_validated", "total_medals") \
 .withColumnRenamed("rank_recomputed", "medal_rank")

# Fact: Gender participation by discipline
fact_gender_participation = entries_gender_clean.select(
    "discipline", "male", "female", "total_validated"
).withColumnRenamed("total_validated", "total_participants")

# Fact: Athlete count by country & discipline (aggregated)
fact_athlete_counts = (
    athletes_clean.groupBy("country_code", "country", "discipline")
    .agg(count("athlete_id").alias("athlete_count"))
)

# COMMAND ----------

# MAGIC %md ## 4. Write curated tables as Delta (ready for Synapse load)

# COMMAND ----------

OUTPUT_PATH = "/dbfs/FileStore/olympic_data/curated"

dim_country.write.format("delta").mode("overwrite").save(f"{OUTPUT_PATH}/dim_country")
dim_discipline.write.format("delta").mode("overwrite").save(f"{OUTPUT_PATH}/dim_discipline")
dim_athlete.write.format("delta").mode("overwrite").save(f"{OUTPUT_PATH}/dim_athlete")
fact_medals.write.format("delta").mode("overwrite").save(f"{OUTPUT_PATH}/fact_medals")
fact_gender_participation.write.format("delta").mode("overwrite").save(f"{OUTPUT_PATH}/fact_gender_participation")
fact_athlete_counts.write.format("delta").mode("overwrite").save(f"{OUTPUT_PATH}/fact_athlete_counts")

print("Curated Delta tables written to:", OUTPUT_PATH)

# COMMAND ----------

# MAGIC %md ## 5. (Optional) Export as Parquet/CSV for direct PolyBase/COPY INTO load into Synapse
# MAGIC If not using a Delta-to-Synapse connector, export flat files that can be loaded via
# MAGIC Synapse's `COPY INTO` statement (see `/sql/create_tables.sql`).

# COMMAND ----------

for name, df in [
    ("dim_country", dim_country), ("dim_discipline", dim_discipline),
    ("dim_athlete", dim_athlete), ("fact_medals", fact_medals),
    ("fact_gender_participation", fact_gender_participation),
    ("fact_athlete_counts", fact_athlete_counts),
]:
    df.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{OUTPUT_PATH}/csv/{name}")

print("CSV export complete — ready for Synapse COPY INTO")
