# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import filter, col, first, round


# Postgres connection
conn = psycopg2.connect(database='vacuums', user='postgres', password='sozjavbxj', host='localhost', port='5432')
cur = conn.cursor()
cur.execute("SELECT "
                "c.*, "
                "v.brand, v.model_name, v.dual_nozzle, v.fluffy_nozzle,"
                "u.full_name as tester"
            " FROM cr_cordless as c "
            " left join vacuums as v on c.inv_no = v.inv_no"
            " left join users as u on c.tester = u.id")


rows = cur.fetchall()

# Create dataframe
cordless_df = pd.DataFrame(rows, columns=['ROW_ID', 'TEST_ID', 'TEST_TARGET', 'TEST_GROUP', 'TEST_CASE', 'TESTER_ID',
                                 'INV_NO', 'BRUSH_TYPE', 'POWER_SETTING', 'TEST_MEASURE', 'VALUE', 'UNITS', 'RUN',
                                 'RUN_DATE', 'NOTES', 'IMAGE', 'OWNER_ID', 'BRAND', 'MODEL_NAME', 'DUAL_NOZZLE',
                                 'FLUFFY_NOZZLE','TESTER_NAME'])


cordless_df = cordless_df.dropna(axis='columns', how='all')

#cordless_df to spark
spark = SparkSession.builder.appName('vacuums_cr').getOrCreate()
spark_df = spark.createDataFrame(cordless_df)

spark_df.createOrReplaceTempView("dataset_view")

sdf = spark.sql("SELECT * FROM dataset_view")

#_value to numeric
sdf = sdf.withColumn("VALUE", sdf["VALUE"].cast("double"))

# filter by test_target and test_measure
sdf_bare = spark.sql("SELECT * FROM dataset_view WHERE TEST_TARGET=='BARE'")
sdf_bare = sdf_bare.withColumn("VALUE", sdf_bare["VALUE"].cast("double"))
sdf_bare = sdf_bare.filter((sdf_bare.TEST_MEASURE == 'pickup'))

sdf_carpet = spark.sql("SELECT * FROM dataset_view WHERE TEST_TARGET=='CARPET'")
sdf_carpet = sdf_carpet.withColumn("VALUE", sdf_carpet["VALUE"].cast("double"))
sdf_carpet = sdf_carpet.filter((sdf_carpet.TEST_MEASURE == 'pickup') | (sdf_carpet.TEST_MEASURE =='r_temp') | (sdf_carpet.TEST_MEASURE =='r_humidity'))

sdf_edge = spark.sql("SELECT * FROM dataset_view WHERE TEST_TARGET=='EDGE'")
sdf_edge = sdf_edge.withColumn("VALUE", round(sdf_edge["VALUE"].cast("double"),2))
sdf_edge = sdf_edge.filter((sdf_edge.TEST_MEASURE == 'e_favg') | (sdf_edge.TEST_MEASURE =='e_lavg') | (sdf_edge.TEST_MEASURE =='e_ravg') |
                           (sdf_edge.TEST_MEASURE == 'e_pickupL') | (sdf_edge.TEST_MEASURE =='e_pickupR'))

# Bare Floor Transformed Dataframe
pivotBareDF = sdf_bare.groupBy('TEST_ID', 'TESTER_NAME', 'BRAND', 'MODEL_NAME', 'INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN')\
                        .pivot('TEST_MEASURE')\
                        .agg(first(col('VALUE')))\
                        .sort('TEST_ID', 'INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN')



pivotCarpetDF = sdf_carpet.groupBy('TEST_ID', 'TESTER_NAME', 'BRAND', 'MODEL_NAME','INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN')\
                            .pivot('TEST_MEASURE')\
                            .agg(first(col('VALUE')))\
                            .sort('TEST_ID', 'INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN')

pivotEdgeDF = sdf_edge.groupBy('TEST_ID', 'TESTER_NAME', 'BRAND', 'MODEL_NAME','INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN')\
                        .pivot('TEST_MEASURE')\
                        .agg(first(col('VALUE')))\
                        .sort('TEST_ID', 'INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN')


# convert spark df to pandas df
bare_df = pivotBareDF.toPandas()
carpet_df = pivotCarpetDF.toPandas()
edge_df = pivotEdgeDF.toPandas()




# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    # html.Label("Test ID:", style={'fontSize': 30, 'textAlign': 'center'}),
    # dcc.Dropdown(
    #     id='dropdown_test_id',
    #     options=[{'label': i, 'value': i} for i in sorted(carpet_df.TEST_ID.unique())],
    #     value=None,
    #     multi=True
    # ),
    # dcc.Dropdown(
    #     id='dropdown_test_group',
    #     options=[{'label': i, 'value': i} for i in sorted(carpet_df.TEST_GROUP.unique())],
    #     value=all,
    #     multi=False),
    #
    # dcc.Dropdown(
    #     id='dropdown_brand',
    #     options=[{'label': i, 'value': i} for i in sorted(carpet_df.BRAND.unique())],
    #     value=all,
    #     multi=True),
    #
    # dcc.Dropdown(
    #     id='dropdown_model_name',
    #     options=[{'label': i, 'value': i} for i in sorted(carpet_df.MODEL_NAME.unique())],
    #     value=all,
    #     multi=True),
    #
    # dcc.Dropdown(
    #     id='dropdown_inv_no',
    #     options=[{'label': i, 'value': i} for i in sorted(carpet_df.INV_NO.unique())],
    #     value=all,
    #     multi=True),
    #
    # dcc.Dropdown(
    #     id='dropdown_brush_type',
    #     options=[{'label': i, 'value': i} for i in sorted(carpet_df.BRUSH_TYPE.unique())],
    #     value=all,
    #     multi=True),

    # html.Div(id='plot1')



    dash_table.DataTable(data=carpet_df.to_dict('records'), page_size=10),

    # dcc.Graph(
    #     figure=go.Box(carpet_df, x='model_name', y='pickup'))
])



# @app.callback([Output(component_id='plot1', component_property='children')],
#               Input('dropdown_test_id', 'value')
#               # Input('dropdown_test_group', 'value'),
#               # Input('dropdown_brand', 'value'),
#               # Input('dropdown_model_name', 'value'),
#               # Input('dropdown_inv_no', 'value'),
#               # Input('dropdown_brush_type', 'value')
#     # prevent_initial_call=True
# )

# def update_graph(selected_TestID):
#     # , selected_TestGroup, selected_Brand, selected_ModelName, selected_InvNo, selected_BrushType):
#     # Volume Share
#     dff = carpet_df[(carpet_df.TEST_ID == selected_TestID)]
#                     # (carpet_df.TEST_GROUP == selected_TestGroup) &
#                     # (carpet_df.BRAND == selected_Brand) &
#                     # (carpet_df.MODEL_NAME == selected_ModelName) &
#                     # (carpet_df.INV_NO == selected_InvNo) &
#                     # (carpet_df.BRUSH_TYPE == selected_BrushType)]
#
#
#     fig1 = px.box(dff, x='MODEL_NAME', y='pickup')
#
#
#     return dcc.Graph(figure=fig1)

# def update_graph(col_chosen):
#     fig = go.figure()
#     fig.add_trace(go.Box(x=carpet_df['model_name'], y=carpet_df['pickup']))
#
#     return fig



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
