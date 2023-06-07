import dash
import mysql.connector
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import datetime
from threading import Lock


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Establish MySQL database connection

conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin123',
        database='nic2'
)

cur = conn.cursor()

# Query to retrieve dropdown options
query = "SELECT plant_nm FROM stn_info"
df = pd.read_sql_query(query, conn)

options = [{'label': plant_nm, 'value': plant_nm} for plant_nm in df['plant_nm']]


# Add navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row([
                dbc.Col([
                    html.Img(src=app.get_asset_url("logo.jpg"), height="70px"),
                ], width={"size": "auto"})
            ],
                align="cover",
                className="g-0"),
            dbc.Row([
                dbc.Col([
                    html.H1("Water Services, Water Resource Department of Odisha",
                            style={"textAlign": "center", "color": "white"}),
                ])
            ]),
            dbc.Row([
            ]),

        ], fluid=True),
    color="primary",
    dark=True,
    sticky='top',

)
app.layout = html.Div([
    navbar,
    html.Div([
        dbc.Row([
            dbc.Col([html.Div(className="border-bold mt-2", children=[
                html.H4("Allocation vs Consumption"),
                html.Hr(style={'border-top': '3px solid bold'}),
                dbc.Row([
                    dbc.Col([dbc.Row([
                        dbc.Col([html.H5("Industry")]),
                        dbc.Col([dcc.Dropdown(id='industry-dropdown1',
                                              options = options,
                                              )

                                 ])
                    ])]),
                    dbc.Col([dbc.Row([
                        dbc.Col([html.H6("Date")]),
                        dbc.Col([dcc.DatePickerSingle(id='date-dropdown1')])
                    ])]),
                ]),
                dcc.Graph(id='line-fig1'),

            ])], width=6),
            dbc.Col([html.Div(className="border-bold mt-2", children=[
                html.H4("IOT Meter Reading Data"),
                html.Hr(style={'border-top': '3px solid bold'}),
                dbc.Row([
                    dbc.Col([dbc.Row([
                        dbc.Col([html.H6("Industry")]),
                        dbc.Col([dcc.Dropdown(id='dropdown',options = options)

                                 ])
                    ])]),
                    dbc.Col([dbc.Row([
                        dbc.Col([html.H6("Date")]),
                        dbc.Col([dcc.DatePickerSingle(id='date-dropdown2',
                                                      min_date_allowed=datetime.datetime(2000, 1, 1),
                                                      max_date_allowed=datetime.datetime.today(),
                                                      initial_visible_month=datetime.datetime.today(),
                                                      date=datetime.datetime.today())])
                    ])]),
                ]),

                dcc.Graph(id='graph'),
            ])], width=6),
        ]),
        dbc.Row([dbc.Col([html.Div(className="border-bold mt-2", children=[
            html.H4("Allocation vs MAX vs MIN vs AVG"),
            html.Hr(style={'border-top': '3px solid bold'}),
            dbc.Row([
                dbc.Col([dbc.Row([
                    dbc.Col([html.H6("Industry")]),
                    dbc.Col([dcc.Dropdown(id='industry-dropdown3', options = options)

                             ])
                ])]),
                dbc.Col([dbc.Row([
                    dbc.Col([html.H6("Date")]),
                    dbc.Col([dcc.DatePickerSingle(id='date-dropdown3')])
                ])]),

            ]),
            dcc.Graph(id='line-fig3'),
        ])], width=6),

                 dbc.Col([html.Div(className="border-bold mt-2", children=[
                     html.H4("Real-Time Flow Data"),
                     html.Hr(style={'border-top': '3px solid bold'}),
                     dcc.Dropdown(
                         id="my-dropdown", options = options
                     ),
                     html.Div(id="output-div"),

                     dcc.Graph(id='line-fig4'),
                     dcc.Interval(
                         id='interval-component',
                         interval=60 * 1000,  # 1 minute
                         n_intervals=0
                     )
                 ])], width=6)

                 ])
    ])
])


@app.callback(Output('line-fig1', 'figure'), [Input('industry-dropdown1', 'value'), Input('date-dropdown1', 'date')])
def update_line_fig1(selected_industry, selected_date):
    if selected_industry is None or selected_date is None:
        return go.Figure()  # Return an empty graph if any input is not selected

    # Filter the data based on the selected industry and date
    query1 = "SELECT allocation, consumption, datetime FROM minute_flow_table WHERE plant_nm = '{}' AND DATE(datetime) = '{}' ORDER BY datetime DESC LIMIT 10".format(
        selected_industry, selected_date)

    data1 = pd.read_sql_query(query1, conn)
    print(data1)

    # Update the first graph
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=data1['datetime'], y=data1['allocation'], mode='lines+markers', name='allocation'))
    fig1.add_trace(go.Scatter(x=data1['datetime'], y=data1['consumption'], mode='lines+markers', name='consumption'))
    fig1.update_layout(title='Allocation VS Consumption', xaxis_title='Time', yaxis_title='Figures(in cusec)')

    return fig1


@app.callback(Output('graph', 'figure'), [Input('dropdown', 'value'), Input('date-dropdown2', 'date')])
def update_timeseries(selected_dropdown_value, selected_date):
    if selected_dropdown_value is None or selected_date is None:
        return go.Figure()  # Return an empty graph if any input is not selected

    # Filter the data based on the selected industry and date
    query2 = "SELECT allocation, hr_flow , datetime FROM hourly_flow_table WHERE plant_nm = '{}' AND DATE(datetime)  = '{}' ORDER BY datetime DESC LIMIT 10".format(
        selected_dropdown_value, selected_date)
    data2 = pd.read_sql_query(query2, conn)

    # Update the first graph
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=data2['datetime'], y=data2['allocation'], mode='lines+markers', name='allocation'))
    fig2.add_trace(go.Scatter(x=data2['datetime'], y=data2['hr_flow'], mode='lines+markers', name='flow'))
    fig2.update_layout(title='IOT DATA', xaxis_title='Time', yaxis_title='Figures(in cusec)')

    return fig2


@app.callback(Output('line-fig3', 'figure'), [Input('industry-dropdown3', 'value'), Input('date-dropdown3', 'date')])
def update_line_graph3(selected_industry, selected_date):
    if selected_industry is None or selected_date is None:
        return go.Figure()  # Return an empty graph if any input is not selected

    # Filter the data based on the selected industry and date
    query3 = "SELECT allocation, max_flow, min_flow, avg_flow, datetime FROM oneday_flow_table WHERE plant_nm = '{}' AND DATE(datetime) = '{}' ORDER BY datetime DESC LIMIT 10".format(
        selected_industry, selected_date)
    data3 = pd.read_sql_query(query3, conn)

    # Update the Third graph
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=data3['datetime'], y=data3['allocation'], mode='lines+markers', name='allocation'))
    fig3.add_trace(go.Scatter(x=data3['datetime'], y=data3['max_flow'], mode='lines+markers', name='max_flow'))
    fig3.add_trace(go.Scatter(x=data3['datetime'], y=data3['min_flow'], mode='lines+markers', name='min_flow'))
    fig3.add_trace(go.Scatter(x=data3['datetime'], y=data3['avg_flow'], mode='lines+markers', name='avg_flow'))
    fig3.update_layout(title='Allocation VS MAX VS MIN VS AVG', xaxis_title='Time', yaxis_title='Figures(in cusec)')

    return fig3


lock = Lock()
graph_data = []

@app.callback(
    [Output("output-div", "children"), Output("line-fig4", "figure")],
    [Input("my-dropdown", "value"),
     Input('interval-component', 'n_intervals')]
)
def update_output(value, n_intervals):
    global graph_data
    # Perform actions based on dropdown value
    if value:
        # Fetch data based on the selected value from the dropdown
        conn1 = mysql.connector.connect(user='root', password='admin123', host='localhost', database='nic2',
                                       auth_plugin='mysql_native_password')
        cur1 = conn1.cursor()
        query = "SELECT datetime, minute_flow FROM minute_flow_table WHERE plant_nm = %s ORDER BY datetime DESC LIMIT 10"
        cur1.execute(query, (value,))

        fetched_data = cur1.fetchall()
        print(fetched_data)
        cur1.close()
        conn1.close()

        with lock:
            graph_data = fetched_data

        # Create the figure based on the fetched data
        fig = create_figure(graph_data)

        return f"You selected: {value}", fig
    else:
        return "Please select an industry", {}


def create_figure(data):
    # Extract x and y values from the data
    x_values = [row[0] for row in data]
    y_values = [row[1] for row in data]

    # Create the Plotly figure based on the extracted data
    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode='lines+markers'))

    # Customize the figure based on your requirements
    fig.update_layout(
        title='Data Visualization',
        xaxis_title='RecordedTime',
        yaxis_title='Flow'
    )

    return fig
if __name__ == '__main__':
    app.run_server(debug=True)



