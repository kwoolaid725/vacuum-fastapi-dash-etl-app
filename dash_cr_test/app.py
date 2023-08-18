# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input, MATCH, ctx, ALL, ALLSMALLER

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

from dotenv import load_dotenv
import os

load_dotenv()

# from dash_iconify import DashIconify


# Postgres connection
conn = psycopg2.connect(database=os.getenv("DATABASE_NAME"),
                        user=os.getenv("DATABASE_USERNAME"),
                        password=os.getenv("DATABASE_PASSWORD"),
                        host=os.getenv("DATABASE_HOSTNAME"),
                        port=os.getenv("DATABASE_PORT")
                        )
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
                                          'INV_NO', 'BRUSH_TYPE', 'POWER_SETTING', 'TEST_MEASURE', 'VALUE', 'UNITS',
                                          'RUN',
                                          'RUN_DATE', 'NOTES', 'IMAGE', 'OWNER_ID', 'BRAND', 'MODEL_NAME',
                                          'DUAL_NOZZLE',
                                          'FLUFFY_NOZZLE', 'TESTER_NAME'])

# cordless_df = cordless_df.dropna(axis='columns', how='all')
# drop image column
cordless_df = cordless_df.drop(columns=['IMAGE'])

cordless_df['VALUE'] = pd.to_numeric(cordless_df['VALUE'], errors='coerce')
cordless_df['VALUE'] = cordless_df['VALUE'].round(2)

cordless_df['RUN_DATE'] = pd.to_datetime(cordless_df['RUN_DATE'], utc=True)
cordless_df['RUN_DATE'] = cordless_df['RUN_DATE'].dt.strftime('%Y/%m/%d')


# bare floor
bare_df = cordless_df[cordless_df['TEST_TARGET'] == 'BARE']
bare_df = bare_df[bare_df['TEST_MEASURE'] == 'pickup']

# carpet
carpet_df = cordless_df[cordless_df['TEST_TARGET'] == 'CARPET']
carpet_df = carpet_df[carpet_df['TEST_MEASURE'].isin(['pickup', 'r_temp', 'r_humidity'])]


# edge
edge_df = cordless_df[cordless_df['TEST_TARGET'] == 'EDGE']
edge_df = edge_df[edge_df['TEST_MEASURE'].isin(['e_favg', 'e_lavg', 'e_ravg', 'e_pickupL', 'e_pickupR'])]

# transform dataframes to pivot tables
pivot_bare_df = bare_df.pivot_table(
    index=['TEST_ID', 'RUN_DATE', 'TESTER_NAME', 'BRAND', 'MODEL_NAME', 'INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN'],
    columns='TEST_MEASURE', values='VALUE', aggfunc='first')
pivot_bare_df.reset_index(inplace=True)

pivot_carpet_df = carpet_df.pivot_table(
    index=['TEST_ID', 'RUN_DATE', 'TESTER_NAME', 'BRAND', 'MODEL_NAME', 'INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN'],
    columns='TEST_MEASURE', values='VALUE', aggfunc='first')
pivot_carpet_df.reset_index(inplace=True)

pivot_edge_df = edge_df.pivot_table(
    index=['TEST_ID', 'RUN_DATE', 'TESTER_NAME', 'BRAND', 'MODEL_NAME', 'INV_NO', 'BRUSH_TYPE', 'TEST_GROUP', 'RUN'],
    columns='TEST_MEASURE', values='VALUE', aggfunc='first')
pivot_edge_df.reset_index(inplace=True)


def create_panel(idx, test_id):
    return dmc.AccordionPanel(
        [
            dbc.Checklist(
                options=[{"label": test_id, "value": test_id}],
                value=[],
                style={'fontSize': 20},
                id={'type': 'checklist-input', 'index': idx},

            ),
            html.Div(id={'type': 'brand', 'index': idx}),

        ]
    )


def create_boxplot(df, title):
    fig = go.Figure()

    df_ordered = df.sort_values(by='BRAND', ascending=False, kind='mergesort')

    for r, c in zip(df_ordered.BRAND.unique(), px.colors.qualitative.G10):
        plot_df = df_ordered[df_ordered.BRAND == r]
        fig.add_trace(go.Box(y=[plot_df.MODEL_NAME, plot_df.BRUSH_TYPE], x=plot_df.pickup, name=r, marker_color=c))
        fig.layout.title = title
        fig.update_traces(
        orientation='h',
        width=0.8,
        boxpoints='all',
        jitter=0.3,
        pointpos=0,
        marker=dict(

            size=4,

        )
    )
    fig.update_layout(
        template="plotly_white",
        # data = data,
        title = {
            'text': '<b>'+title +'<br>'+'-'*(len(title)+2),
            'font': {
                'size': 20,

            },
            'x':0.5,


        },
        boxmode='group',
        autosize=False,
        width=1000,
        height=800,
        xaxis=dict(
            title='<b>Pickup % </b>',
            titlefont_size=14,
            autorange=True,
            # showgrid=True,
            zeroline=True,
            showline=True,
        ),
        yaxis=dict(
            title="<b>Model Names / Brush Type<b>",
            titlefont_size=14,
        ),
        legend = {
            'traceorder': 'reversed',
        }

    )


    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', ticks='inside', tickcolor='crimson', ticklen=10)
    fig.update_yaxes(automargin=True, showline=True, linewidth=2, linecolor='black', ticks='inside', tickcolor='black', ticklen=10, tickmode='linear')

    return fig

def create_table(df):

    table = dash_table.DataTable(
        df.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in df.columns],

    )

    return table

def create_edge_plots(df):
    list=[]
    # append df['e_pickupL'] and df['e_pickupR'] to df['e_pickupAvg']
    df['e_pickupAvg'] = df[['e_pickupL', 'e_pickupR']].mean(axis=1).round(2)
    # max e_lavg, e_ravg, e_favg
    df['e_max'] = df[['e_lavg', 'e_ravg', 'e_favg']].max(axis=1)
    #group by brand and model name and nozzle type and get max of e_max
    df['e_max'] = df.groupby(['BRAND', 'MODEL_NAME', 'BRUSH_TYPE'])['e_max'].transform('max')



    fig1 = go.Figure()
    fig2 = go.Figure()
    fig3 = go.Figure()
    fig4 = go.Figure()



    df_ordered = df.sort_values(by='BRAND', ascending=False, kind='mergesort')

    for r, c in zip(df_ordered.BRAND.unique(), px.colors.qualitative.G10):
        plot_df = df_ordered[df_ordered.BRAND == r]

        fig1.add_trace(go.Box(y=[plot_df.MODEL_NAME, plot_df.BRUSH_TYPE], x=plot_df.e_pickupAvg, name=r, marker_color=c))
        fig1.update_layout(title='<b>Average of Left and Right Side Pickup %</b>' + '<br>' + '-' * 50)

        fig2.add_trace(go.Box(y=[plot_df.MODEL_NAME, plot_df.BRUSH_TYPE], x=plot_df.e_pickupL, name=r, marker_color=c))
        fig2.update_layout(title='<b>Left Side of T Jig - Pickup %</b>' + '<br>' + '-' * 50)

        fig3.add_trace(go.Box(y=[plot_df.MODEL_NAME, plot_df.BRUSH_TYPE], x=plot_df.e_pickupR, name=r, marker_color=c))
        fig3.update_layout(title='<b>Right of T Jig - Pickup %</b>' + '<br>' + '-' * 50 )

        fig4.add_trace(go.Scatter(x=plot_df.e_max, y=[plot_df.MODEL_NAME, plot_df.BRUSH_TYPE], mode='markers', name=r, marker_color=c))


    for fig in fig1, fig2, fig3:
        fig.update_traces(
        orientation='h',
        width=0.8,
        boxpoints='all',
        jitter=0.3,
        pointpos=0,
        marker=dict(

            size=4,

            )
        )
        fig.update_layout(
        template="plotly_white",
        title={

            'font': {
                'size': 20,

            },
            'x': 0.5,

        },
        # data = data,
        boxmode='group',
        autosize=False,
        width=1000,
        height=800,
        xaxis=dict(
            title='<b>Pickup % </b>',
            autorange=True,
            # showgrid=True,
            zeroline=True,
            showline=True,
            ),
        legend = {
            'traceorder': 'reversed',
        }
        )
        fig.update_xaxes(showline=True, linewidth=2, linecolor='black', ticks='inside', tickcolor='crimson', ticklen=10)
        fig.update_yaxes(automargin=True,showline=True, linewidth=2, linecolor='black', ticks='inside', tickcolor='black', ticklen=10)

        list.append(html.Div(dcc.Graph(
            figure=fig)))


    fig4.update_layout(
        template="plotly_white",
        boxmode='group',
        autosize=False,
        width=1000,
        height=800,
        title = {
            'text': '<b>Max Remaining Distance (in) of All 3 Sides </b>' + '<br>' + '-' * 50,
            'font': {
                'size': 20,
            },
            'x': 0.5,
        },


        xaxis=dict(
            title='<b>Distance (in) </b>',
            autorange=True,
            # showgrid=True,
            zeroline=True,
            showline=True,

        ),
        legend={
            'traceorder': 'reversed',
        }
    )
    fig4.update_traces(
        marker_size=12,
        marker_line=dict(width=2, color='DarkSlateGrey'),
        selector=dict(mode='markers'))
    fig4.update_xaxes(showline=True, linewidth=2, linecolor='black', ticks='inside', tickcolor='crimson', ticklen=10)
    fig4.update_yaxes(automargin=True, showline=True, linewidth=2, linecolor='black', ticks='inside', tickcolor='black', ticklen=10)

    list.append(html.Div(dcc.Graph(figure=fig4)))
    return list

def create_bare_scatter(df):

    df['MM'] = df['MODEL_NAME'].map(str) + " / " + df['BRUSH_TYPE'].map(str)
    fig = px.scatter(df,
                      x='pickup',
                      y='MM', color='BRAND', hover_data=['BRAND', 'TEST_GROUP'],
                      symbol=df['TEST_GROUP'], symbol_sequence=['circle-open', 'diamond-tall-open', 'x'],
                      width=1080, height=800,
                      )
    fig.update_layout(

        xaxis=dict(title_text="<b>Pickup % </b>"),
        yaxis=dict(autorange="reversed", title_text="<b>Model Names / Brush Type<b>"),
        template="plotly_white",
        title={'text': "<b> Pickup % Scatter Plot for All Soil Types</b>" + '<br>' + '-' * 45,
                'font': {
                    'size': 20,
                },
               'x': 0.5,

               },

    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', ticks='inside', tickcolor='crimson', ticklen=10)
    fig.update_yaxes(automargin=True, showline=True, linewidth=2, linecolor='black', ticks='inside', tickcolor='black',
                      ticklen=10)
    return fig


# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = dmc.Container([
    dmc.Tabs([
        dmc.TabsList(
            [
                dmc.Tab('Bare Floor', value='bare', styles = {
                    "input": {"borderColor": dmc.theme.DEFAULT_COLORS["violet"][4]}
                }),
                dmc.Tab('Carpet', value='carpet'),
                dmc.Tab('Edge', value='edge'),
            ]
        ),

    ],
        className="mantine-Tabs-tab",
        id='tabs',
        value='bare',


    ),
    dmc.Grid([

            dmc.Col([
                dmc.Accordion(
                    children=[
                        dmc.AccordionItem(
                            [dmc.AccordionControl("TEST ID", className='accordion-control-header')] +
                            [create_panel(idx, test_id) for idx, test_id in enumerate(cordless_df['TEST_ID'].sort_values().unique())],
                            value='customization',

                        ),
                    ]

                )
            ],
                span=2

            ),

            dmc.Col([

                  html.Div(
                        [(dcc.Graph(figure=create_bare_scatter(pivot_bare_df)))] +
                        [(dcc.Graph(figure=create_boxplot(pivot_bare_df[pivot_bare_df.TEST_GROUP == i], i)))
                         for i in pivot_bare_df['TEST_GROUP'].unique()])
                ],
                id = 'graph',
                span=7,

            ),

            dmc.Col(
               [create_table(pivot_bare_df)],
                id = 'table-placeholder',
                span = 3
            ),
    ],
    justify="center",
    align='flex-start',
    gutter="xl",
    ),

], fluid=True)


@app.callback(
    Output({'type': 'brand', 'index': MATCH}, 'children'),
    Input({'type': 'checklist-input', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def update_table(checklist):
    idx = ctx.triggered_id['index']

    dff = cordless_df[cordless_df['TEST_ID'].isin(checklist)]
    # get rid of DUMMY brand
    dff = dff[dff['BRAND'] != 'DUMMY']
    return dmc.Accordion(
        children=[
            dmc.AccordionItem([
                dmc.AccordionControl("BRAND", className='accordion-control-header'),
                dmc.AccordionPanel([
                    dbc.Checklist(
                        options=[
                            {'label': i, 'value': i} for i in dff['BRAND'].unique()
                        ],
                        value=[],
                        style={'fontSize': 20},
                        id={'type': 'checklist-input-2', 'index': idx}),
                    html.Div(id={'type': 'model_name', 'index': idx}),
                ])
            ],
                value='customization2')
        ])


@app.callback(
    Output({'type': 'model_name', 'index': MATCH}, 'children'),
    Input({'type': 'checklist-input', 'index': MATCH}, 'value'),
    Input({'type': 'checklist-input-2', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def update_table(checklist, checklist2):
    idx = ctx.triggered_id['index']

    dff = cordless_df[cordless_df['TEST_ID'].isin(checklist) & cordless_df['BRAND'].isin(checklist2)]

    return dmc.Accordion(
        children=[
            dmc.AccordionItem([
                dmc.AccordionControl("MODEL", className='accordion-control-header'),
                dmc.AccordionPanel([
                    dbc.Checklist(
                        options=[
                            {'label': i, 'value': i} for i in dff['MODEL_NAME'].unique()
                        ],
                        value=[],
                        style={'fontSize': 20},
                        id={'type': 'checklist-input-3', 'index': idx}),

                ]),
                html.Div(id={'type': 'sample', 'index': idx})
            ],
                value='customization3'),

        ])


@app.callback(
    Output({'type': 'sample', 'index': MATCH}, 'children'),
    Input({'type': 'checklist-input', 'index': MATCH}, 'value'),
    Input({'type': 'checklist-input-2', 'index': MATCH}, 'value'),
    Input({'type': 'checklist-input-3', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def update_table(checklist, checklist2, checklist3):
    idx = ctx.triggered_id['index']

    dff = cordless_df[cordless_df['TEST_ID'].isin(checklist) &
                          cordless_df['BRAND'].isin(checklist2) &
                          cordless_df['MODEL_NAME'].isin(checklist3)]

    return dmc.MultiSelect(
        label='SAMPLES',
        placeholder='Select Samples',
        id={'type': 'multiselect-input', 'index': idx},
        value=[],
        data=[
            {'label': i, 'value': i} for i in dff['INV_NO'].unique()
        ],
        className='multiselect-input'
    )


@app.callback(
    # Output({'type': 'table-placeholder', 'index': ALL}, 'data'),
    Output('table-placeholder', 'children'),
    Input({'type': 'checklist-input', 'index': ALL}, 'value'),
    Input({'type': 'checklist-input-2', 'index': ALL}, 'value'),
    Input({'type': 'checklist-input-3', 'index': ALL}, 'value'),
    Input({'type': 'multiselect-input', 'index': ALL}, 'value'),
    Input('tabs', 'value'),
    prevent_initial_call=True
)

def update_table(checklist, checklist2, checklist3, multiselect, tab):
    cl = [item for sublist in checklist for item in sublist]
    cl2 = [item for sublist in checklist2 for item in sublist]
    cl3 = [item for sublist in checklist3 for item in sublist]
    ms = [item for sublist in multiselect for item in sublist]

    if tab == "bare":
        if cl != [] and cl2 != [] and cl3 != [] and ms != []:
            dff = pivot_bare_df[pivot_bare_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]
            dff = dff[dff['MODEL_NAME'].isin(cl3)]
            dff = dff[dff['INV_NO'].isin(ms)]

            return [create_table(dff)]

        elif cl != [] and cl2 != [] and cl3 != [] and ms == []:
            dff = pivot_bare_df[pivot_bare_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]
            dff = dff[dff['MODEL_NAME'].isin(cl3)]

            return [create_table(dff)]

        elif cl != [] and cl2 != [] and cl3 == [] and ms == []:
            dff = pivot_bare_df[pivot_bare_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]

            return [create_table(dff)]

        elif cl != [] and cl2 == [] and cl3 == [] and ms == []:
            dff = pivot_bare_df[pivot_bare_df['TEST_ID'].isin(cl)]


            return [create_table(dff)]

        else:

            return [create_table(pivot_bare_df)]

    elif tab == "carpet":
        if cl != [] and cl2 != [] and cl3 != [] and ms != []:
            dff = pivot_carpet_df[pivot_carpet_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]
            dff = dff[dff['MODEL_NAME'].isin(cl3)]
            dff = dff[dff['INV_NO'].isin(ms)]

            return [create_table(dff)]

        elif cl != [] and cl2 != [] and cl3 != [] and ms == []:
            dff = pivot_carpet_df[pivot_carpet_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]
            dff = dff[dff['MODEL_NAME'].isin(cl3)]

            return [create_table(dff)]

        elif cl != [] and cl2 != [] and cl3 == [] and ms == []:
            dff = pivot_carpet_df[pivot_carpet_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]

            return [create_table(dff)]

        elif cl != [] and cl2 == [] and cl3 == [] and ms == []:
            dff = pivot_carpet_df[pivot_carpet_df['TEST_ID'].isin(cl)]

            return [create_table(dff)]

        else:
            return [create_table(pivot_carpet_df)]

    elif tab == "edge":
        if cl != [] and cl2 != [] and cl3 != [] and ms != []:
            dff = pivot_edge_df[pivot_edge_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]
            dff = dff[dff['MODEL_NAME'].isin(cl3)]
            dff = dff[dff['INV_NO'].isin(ms)]

            return [create_table(dff)]

        elif cl != [] and cl2 != [] and cl3 != [] and ms == []:
            dff = pivot_edge_df[pivot_edge_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]
            dff = dff[dff['MODEL_NAME'].isin(cl3)]

            return [create_table(dff)]

        elif cl != [] and cl2 != [] and cl3 == [] and ms == []:
            dff = pivot_edge_df[pivot_edge_df['TEST_ID'].isin(cl)]
            dff = dff[dff['BRAND'].isin(cl2)]

            return [create_table(dff)]

        elif cl != [] and cl2 == [] and cl3 == [] and ms == []:
            dff = pivot_edge_df[pivot_edge_df['TEST_ID'].isin(cl)]


            return [create_table(dff)]

        else:
            return [create_table(pivot_edge_df)]

    else:
        return [create_table(cordless_df)]
@app.callback(
    Output('graph', 'children'),
    Input({'type': 'checklist-input', 'index': ALL}, 'value'),
    Input({'type': 'checklist-input-2', 'index': ALL}, 'value'),
    Input({'type': 'checklist-input-3', 'index': ALL}, 'value'),
    Input({'type': 'multiselect-input', 'index': ALL}, 'value'),
    Input('tabs', 'value'),
    prevent_initial_call=True
)
def update_graph(checklist, checklist2, checklist3, multiselect, tab):

    cl = [item for sublist in checklist for item in sublist]
    cl2 = [item for sublist in checklist2 for item in sublist]
    cl3 = [item for sublist in checklist3 for item in sublist]
    ms = [item for sublist in multiselect for item in sublist]


    if tab == "bare":

        if cl != [] and cl2 != [] and cl3 != [] and ms != []:
            list = []

            dff = pivot_bare_df[pivot_bare_df.TEST_ID.isin(cl)]
            dff = dff[dff.BRAND.isin(cl2)]
            dff = dff[dff.MODEL_NAME.isin(cl3)]
            dff = dff[dff.INV_NO.isin(ms)]
            list.append(html.Div(dcc.Graph(
                figure=create_bare_scatter(dff))))


            for i in pivot_bare_df.TEST_GROUP.unique():

                dff = pivot_bare_df[pivot_bare_df.TEST_ID.isin(cl)]
                dff = dff[dff.BRAND.isin(cl2)]
                dff = dff[dff.MODEL_NAME.isin(cl3)]
                dff = dff[dff.INV_NO.isin(ms)]
                dff = dff[dff.TEST_GROUP == i]

                list.append(html.Div(dcc.Graph(
                                    figure=create_boxplot(dff, i)))),

            return list

        elif cl != [] and cl2 != [] and cl3 != [] and ms == []:
            list = []

            dff = pivot_bare_df[pivot_bare_df.TEST_ID.isin(cl)]
            dff = dff[dff.BRAND.isin(cl2)]
            dff = dff[dff.MODEL_NAME.isin(cl3)]
            list.append(html.Div(dcc.Graph(
                figure=create_bare_scatter(dff))))

            for i in pivot_bare_df.TEST_GROUP.unique():
                dff = pivot_bare_df[pivot_bare_df.TEST_ID.isin(cl)]
                dff = dff[dff.BRAND.isin(cl2)]
                dff = dff[dff.MODEL_NAME.isin(cl3)]
                dff = dff[dff.TEST_GROUP == i]

                list.append(html.Div(dcc.Graph(
                    figure=create_boxplot(dff, i)))),

            return list

        elif cl != [] and cl2 != [] and cl3 == [] and ms == []:
            list = []

            dff = pivot_bare_df[pivot_bare_df.TEST_ID.isin(cl)]
            dff = dff[dff.BRAND.isin(cl2)]
            list.append(html.Div(dcc.Graph(
                figure=create_bare_scatter(dff))))

            for i in pivot_bare_df.TEST_GROUP.unique():

                dff = pivot_bare_df[pivot_bare_df.TEST_ID.isin(cl)]
                dff = dff[dff.BRAND.isin(cl2)]
                dff = dff[dff.TEST_GROUP == i]

                list.append(html.Div(dcc.Graph(
                    figure=create_boxplot(dff, i)))),

            return list

        elif cl != [] and cl2 == [] and cl3 == [] and ms == []:
            list = []

            dff = pivot_bare_df[pivot_bare_df.TEST_ID.isin(cl)]
            list.append(html.Div(dcc.Graph(
                figure=create_bare_scatter(dff))))

            for i in pivot_bare_df.TEST_GROUP.unique():

                dff = pivot_bare_df[pivot_bare_df.TEST_ID.isin(cl)]
                dff = dff[dff.TEST_GROUP == i]

                list.append(html.Div(dcc.Graph(
                    figure=create_boxplot(dff, i)))),


            return list

        else:
            list = []
            list.append(html.Div(dcc.Graph(
                figure=create_bare_scatter(pivot_bare_df))))

            for i in pivot_bare_df.TEST_GROUP.unique():

                dff = pivot_bare_df[pivot_bare_df.TEST_GROUP == i]

                list.append(html.Div(dcc.Graph(
                    figure=create_boxplot(dff, i)))),

            return list

    elif tab == "carpet":
        if cl != [] and cl2 != [] and cl3 != [] and ms != []:
            list = []

            for i in pivot_carpet_df.TEST_GROUP.unique():
                dff = pivot_carpet_df[pivot_carpet_df.TEST_ID.isin(cl)]
                dff = dff[dff.BRAND.isin(cl2)]
                dff = dff[dff.MODEL_NAME.isin(cl3)]
                dff = dff[dff.INV_NO.isin(ms)]
                dff = dff[dff.TEST_GROUP == i]
                list.append(html.Div(dcc.Graph(
                                    figure=create_boxplot(dff, i)))),

            return list

        elif cl != [] and cl2 != [] and cl3 != [] and ms == []:
            list = []

            for i in pivot_carpet_df.TEST_GROUP.unique():
                dff = pivot_carpet_df[pivot_carpet_df.TEST_ID.isin(cl)]
                dff = dff[dff.BRAND.isin(cl2)]
                dff = dff[dff.MODEL_NAME.isin(cl3)]
                dff = dff[dff.TEST_GROUP == i]
                list.append(html.Div(dcc.Graph(
                    figure=create_boxplot(dff, i)))),

            return list

        elif cl != [] and cl2 != [] and cl3 == [] and ms == []:
            list = []

            for i in pivot_carpet_df.TEST_GROUP.unique():
                dff = pivot_carpet_df[pivot_carpet_df.TEST_ID.isin(cl)]
                dff = dff[dff.BRAND.isin(cl2)]
                dff = dff[dff.TEST_GROUP == i]
                list.append(html.Div(dcc.Graph(
                    figure=create_boxplot(dff, i)))),

            return list

        elif cl != [] and cl2 == [] and cl3 == [] and ms == []:
            list = []

            for i in pivot_carpet_df.TEST_GROUP.unique():
                dff = pivot_carpet_df[pivot_carpet_df.TEST_ID.isin(cl)]
                dff = dff[dff.TEST_GROUP == i]
                list.append(html.Div(dcc.Graph(
                    figure=create_boxplot(dff, i)))),

            return list

        else:
            list = []
            for i in pivot_carpet_df.TEST_GROUP.unique():
                dff = pivot_carpet_df[pivot_carpet_df.TEST_GROUP == i]
                list.append(html.Div(dcc.Graph(
                    figure=create_boxplot(dff, i)))),

            return list

    elif tab == "edge":
        if cl != [] and cl2 != [] and cl3 != [] and ms != []:

            dff = pivot_edge_df[pivot_edge_df.TEST_ID.isin(cl)]
            dff = dff[dff.BRAND.isin(cl2)]
            dff = dff[dff.MODEL_NAME.isin(cl3)]
            dff = dff[dff.INV_NO.isin(ms)]

            return create_edge_plots(dff)

        elif cl != [] and cl2 != [] and cl3 != [] and ms == []:


            dff = pivot_edge_df[pivot_edge_df.TEST_ID.isin(cl)]
            dff = dff[dff.BRAND.isin(cl2)]
            dff = dff[dff.MODEL_NAME.isin(cl3)]

            return create_edge_plots(dff)

        elif cl != [] and cl2 != [] and cl3 == [] and ms == []:

            dff = pivot_edge_df[pivot_edge_df.TEST_ID.isin(cl)]
            dff = dff[dff.BRAND.isin(cl2)]

            return create_edge_plots(dff)

        elif cl != [] and cl2 == [] and cl3 == [] and ms == []:

            dff = pivot_edge_df[pivot_edge_df.TEST_ID.isin(cl)]

            return create_edge_plots(dff)

        else:

            return create_edge_plots(pivot_edge_df)

    else:
        list = []
        return list

#\
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

