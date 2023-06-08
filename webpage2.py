import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import mysql.connector
from threading import Lock


# Establish database connection
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='admin',
    database='nic'
)

# Create Dash app
app = dash.Dash(__name__)

# Define options for industry dropdowns
options = [
    {"label": "Areceol Mittal", "value": "Arcelor Mittal"},
    {"label": "NTPC,Kaniha", "value": "NTPC_KANIHA"}
]

# Define layout
app.layout = html.Div([
    html.H1("Flow Data Analysis Dashboard"),

    # Dropdown and Date picker for Line Graph 1
    html.Div([
        html.Div([
            html.H2("Allocation VS Consumption"),
            dcc.Dropdown(
                id='industry-dropdown1',
                placeholder='Select Industry',
                options=options,
            ),
            dcc.DatePickerSingle(
                id='date-dropdown1',
                placeholder='Select Date',
                display_format='DD-MM-YYYY'
            ),
            dcc.Graph(id='line-fig1'),
        ], className="six columns"),

        # Dropdown and Date picker for Line Graph 2
        html.Div([
            html.H2("Allocation VS Flow"),
            dcc.Dropdown(
                id='industry-dropdown2',
                placeholder='Select Industry',
                options=options
            ),
            dcc.DatePickerSingle(
                id='date-dropdown2',
                placeholder='Select Date',
                display_format='DD-MM-YYYY'
            ),
            dcc.Graph(id='line-fig2'),
        ], className="six columns"),
    ], className="row"),

    # Dropdown and Date picker for Line Graph 3
    html.Div([
        html.Div([
            html.H2("Max VS Min VS Avg VS Allocation"),
            dcc.Dropdown(
                id='industry-dropdown3',
                placeholder='Select Industry',
                options=options,
            ),
            dcc.DatePickerSingle(
                id='date-dropdown3',
                placeholder='Select Date',
                display_format='DD-MM-YYYY'
            ),
            dcc.Graph(id='line-fig3'),
        ], className="six columns"),

        # Real-Time Flow Data
        html.Div([
            html.H2("Real-Time Flow Data"),
            dcc.Dropdown(
                id='my-dropdown',
                placeholder='Select Industry',
                options=options,
            ),
            html.Div(id="output-div"),
            dcc.Graph(id='line-fig4'),
            dcc.Interval(
                id='interval-component',
                interval=60 * 1000,  # 1 minute
                n_intervals=0
            )
        ], className="six columns"),
    ], className="row ")
])

@app.callback(Output('line-fig1', 'figure'), [Input('industry-dropdown1', 'value'), Input('date-dropdown1', 'date')])
def update_line_fig1(selected_industry, selected_date):
    if selected_industry is None or selected_date is None:
        return go.Figure()  # Return an empty graph if any input is not selected

    # Filter the data based on the selected industry and date
    query1 = "SELECT allocation, consumption, datetime FROM flow_minute_table WHERE plant_nm = '{}' AND DATE(datetime) = '{}' ORDER BY datetime DESC LIMIT 10".format(
        selected_industry, selected_date)

    data1 = pd.read_sql_query(query1, connection)
    #print(data1)

    # Update the first graph
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=data1['datetime'], y=data1['allocation'], mode='lines+markers', name='allocation'))
    fig1.add_trace(go.Scatter(x=data1['datetime'], y=data1['consumption'], mode='lines+markers', name='consumption'))
    fig1.update_layout(title='Allocation VS Consumption', xaxis_title='Time', yaxis_title='Figures(in cusec)')

    return fig1


@app.callback(Output('line-fig2', 'figure'), [Input('industry-dropdown2', 'value'), Input('date-dropdown2', 'date')])
def update_timeseries(selected_dropdown_value, selected_date):
    if selected_dropdown_value is None or selected_date is None:
        return go.Figure()  # Return an empty graph if any input is not selected

    # Filter the data based on the selected industry and date
    #print(selected_dropdown_value,selected_date)
    query2 = "SELECT allocation, hr_flow , datetime FROM hourly_flow_table WHERE plant_nm = '{}' AND DATE(datetime)  = '{}' ORDER BY datetime DESC LIMIT 10".format(
        selected_dropdown_value, selected_date)
    data2 = pd.read_sql_query(query2, connection)
    #print(data2)

    # Update the first graph
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=data2['datetime'], y=data2['allocation'], mode='lines+markers', name='allocation'))
    fig2.add_trace(go.Scatter(x=data2['datetime'], y=data2['hr_flow'], mode='lines+markers', name='flow'))
    fig2.update_layout(title='IOT Meter Reading Data', xaxis_title='Time', yaxis_title='Figures(in cusec)')

    return fig2


@app.callback(Output('line-fig3', 'figure'), [Input('industry-dropdown3', 'value'), Input('date-dropdown3', 'date')])
def update_line_fig3(selected_industry, selected_date):
    if selected_industry is None or selected_date is None:
        return go.Figure()  # Return an empty graph if any input is not selected

    # Filter the data based on the selected industry and date
    #print(selected_industry, selected_date)
    query3 = "SELECT allocation, min_flow, max_flow, avg_flow , datetime FROM oneday_flow_table WHERE plant_nm = '{}' AND DATE(datetime) = '{}' ORDER BY datetime DESC LIMIT 10".format(
        selected_industry, selected_date)

    data3 = pd.read_sql_query(query3, connection)

    # Update the first graph
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=data3['datetime'], y=data3['allocation'], mode='lines+markers', name='allocation'))
    fig3.add_trace(go.Scatter(x=data3['datetime'], y=data3['min_flow'], mode='lines+markers', name='min_flow'))
    fig3.add_trace(go.Scatter(x=data3['datetime'], y=data3['max_flow'], mode='lines+markers', name='max_flow'))
    fig3.add_trace(go.Scatter(x=data3['datetime'], y=data3['avg_flow'], mode='lines+markers', name='avg_flow'))
    fig3.update_layout(title='Allocation VS MAX VS MIN VS AVG', xaxis_title='Time', yaxis_title='Figures(in cusec)')

    return fig3


# @app.callback(Output("output-div", "children"), [Input("my-dropdown", "value")])
# def update_output(value):
#     if value:
#         return f"You have selected {value}"


# @app.callback(Output('line-fig4', 'figure'), [Input('interval-component', 'n_intervals'), Input("my-dropdown", "value")])
# def update_realtime_flow(n, selected_dropdown_value):
#     if selected_dropdown_value is None:
#         return go.Figure()  # Return an empty graph if no dropdown value is selected
#
#     # Fetch the latest data from the database
#     query4 = "SELECT minute_flow, datetime FROM minute_flow_table WHERE plant_nm = '{}' ORDER BY datetime DESC LIMIT 10".format(
#         selected_dropdown_value)
#     data4 = pd.read_sql_query(query4, connection)
#     print(data4)
#
#     # Update the graph
#     fig4 = go.Figure()
#     fig4.add_trace(go.Scatter(x=data4['datetime'], y=data4['minute_flow'], mode='lines+markers', name='allocation'))
#     fig4.update_layout(title='Real-Time Flow Data', xaxis_title='Time', yaxis_title='Flow(in cusec)')
#
#     return fig4

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
        conn1 = mysql.connector.connect(user='root', password='admin', host='localhost', database='nic',
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

if __name__ == "__main__":
    app.run_server(debug=True)
