from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace
from pyspark.sql.functions import filter, col, first, round, concat, lit, when, to_date, trim
from pyspark.conf import SparkConf
from pyspark.context import SparkContext


spark = SparkSession.builder \
    .appName('crdi-transform') \
    .config("spark.driver.extraClassPath", "C:/Users/aiden2.kim/Desktop/Aiden-Projects/vacuum-fastapi-dash-etl-app/postgresql-42.6.0.jar") \
    .getOrCreate()


df_input = spark.read.csv('CRDI Appliances Test Insights Stick Vacuums Data.csv', header=True, inferSchema=True)
ver_date = '2023-07-18'
# create a new column as category_id
df_input = df_input.withColumn('ver_date', lit(ver_date))\
                    .withColumn('test_category_id', lit(4))\
                    .withColumn('vac_type_id', when(col('category_name').like('%Cordless%'), 1).when(col('category_name').like('%Corded%'), 3))\
                    .withColumn('test_target_id', col('another_column') + 10)\
                    .withColumn('test_group_id', col('another_column') + 10)\
                    .withColumn('test_measure_id', col('another_column') + 10)\



# connect to db
df_vacuum = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/vacuum_api") \
    .option("dbtable", "vacuums") \
    .option("user", "postgres") \
    .option("password", "password") \
    .option("driver", "org.postgresql.Driver") \
    .load()

df_test = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/vacuum_api") \
    .option("dbtable", "tests") \
    .option("user", "postgres") \
    .option("password", "password") \
    .option("driver", "org.postgresql.Driver") \
    .load()


df_test_vacuums = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/vacuum_api") \
    .option("dbtable", "test_vacuums") \
    .option("user", "postgres") \
    .option("password", "password") \
    .option("driver", "org.postgresql.Driver") \
    .load()



df_crdi = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/vacuum_api") \
    .option("dbtable", "crdi") \
    .option("user", "postgres") \
    .option("password", "password") \
    .option("driver", "org.postgresql.Driver") \
    .load()

df_crdi.printSchema()

# register temp tables
df_input.createOrReplaceTempView("input")
df_vacuum.createOrReplaceTempView("vacuum")
df_test.createOrReplaceTempView("test")
df_test_vacuums.createOrReplaceTempView("test_vacuums")
df_crdi.createOrReplaceTempView("crdi")

# show input table
spark.sql("""
    SELECT *
    FROM input
    LIMIT 10
    """).show()

# manipulate input table
df_input = spark.sql("""
    SELECT * FROM input
    """)


spark.sql("""
    SELECT DISTINCT
        test_group,
        test_measure
    FROM input

    """).show(1000)



        



spark.sql("""
    SELECT

""")

# extract brand and model from input and put into df_vacuum
input_data = spark.sql("""
    SELECT DISTINCT
        brand,
        model
    FROM input
    WHERE brand IS NOT NULL
    AND model IS NOT NULL
    """)

