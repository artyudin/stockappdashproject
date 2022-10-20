
from ctypes import alignment
from email.contentmanager import raw_data_manager
import dash
import dash_bootstrap_components as dbc
from tracemalloc import start
from dash import html, dcc, dash_table, callback_context
import plotly.graph_objects as go
import dash_trich_components as dtc
from dash.dependencies import Input, Output, State
import plotly.express as px
import numpy as np
import pandas as pd
from pandas_ta import bbands
import pandas_datareader as web
import yfinance as yf
import json
import datetime
from scipy.stats import pearsonr
today = datetime.datetime.today()
sector_stocks = json.load(open('sector_stocks.json', 'r'))


stock_ticker = yf.Ticker("AAPL").get_info()
Name=stock_ticker['shortName']
Price=stock_ticker['currentPrice']
def call_stock(s):
    d = yf.Ticker(s).get_info()
    return d

# stock_ticker = stock_ticker
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

stock_info = html.Div(id="stock_info",children=[ 
                            html.P(["Name:"," ",stock_ticker['shortName']],id="Name"),
                            html.P(["Price:"," ",stock_ticker['currentPrice']],id="Price"),
                            html.P(["Target:"," ", stock_ticker['targetLowPrice']],id="Target"),
                            html.P(["Rating:"," ",stock_ticker['recommendationKey']],id="Rating"),
                            html.P(["PE:"," ",stock_ticker['forwardPE']],id="PE"),
                            html.P(["PEG:"," ",stock_ticker['pegRatio']],id="PEG"),
                            html.P(["ROE:"," ",stock_ticker['returnOnEquity']],id="ROE"),
                            html.P(["Beta:"," ",stock_ticker['beta']],id="Beta"),
                            html.P(["52 Week Change:"," ",stock_ticker['52WeekChange']],id="WeekChange"),
                ],style={"margin-top":"10px"})


controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Select one of S&P 500 Sectors"),
                dcc.Dropdown(
                    id="sector-dropdown",
                    options=[
                        {"label": sector, "value": sector} for sector in sector_stocks
                    ],
                    value="Information Technology",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Select company from the sector"),
                dcc.Dropdown(
                    id="stock-dropdown",
                    value='AAPL',
                ),
            ]
        ),
        stock_info,
        
    ],body=True,
)

@app.callback(
    Output('stock_info', 'children'),
    Input('stock-dropdown', 'value'),
     
)
def update_stock_info(stock):
    ticker=call_stock(stock)
    return [                
        html.P(["Name:"," ",ticker['shortName']],id="Name"),
        html.P(["Price:"," ",ticker['currentPrice']],id="Price"),
        html.P(["Target:"," ", ticker['targetLowPrice']],id="Target"),
        html.P(["Rating:"," ",ticker['recommendationKey']],id="Rating"),
        html.P(["PE:"," ",ticker['forwardPE']],id="PE"),
        html.P(["PEG:"," ",ticker['pegRatio']],id="PEG"),
        html.P(["ROE:"," ",ticker['returnOnEquity']],id="ROE"),
        html.P(["Beta:"," ",ticker['beta']],id="Beta"),
        html.P(["52 Week Change:"," ",ticker['52WeekChange']],id="WeekChange")
    ]

#     Output("Price", 'children'),
#     Output("Target", 'children'),
#     Output("Rating", 'children'),
#     Output("PE", 'children'),
#     Output("PEG", 'children'),
#     Output("ROE", 'children'),
#     Output("Beta", 'children'),
#     Output("WeekChange", 'children'),
#     Input('stock-dropdown', 'value')
# )


analytics = dbc.Col([
                    dcc.Checklist(
                            ['Rolling Mean',
                            'Exponential Rolling Mean',
                            'Bollinger Bands'],
                            inputStyle={'margin-left': '15px',
                                        'margin-right': '5px'},
                                        id='complements-checklist',
                                        style={'margin-top': '20px'}
                            )
                    ], width=8)
time_boxes = dbc.Row([
                        dbc.Col([

                            # This Div contains the time span buttons for adjustment of the x-axis' length.
                            html.Div([
                                     html.Button('1W', id='1W-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('1M', id='1M-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('3M', id='3M-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('6M', id='6M-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('1Y', id='1Y-button',
                                                 n_clicks=0, className='btn-secondary'),
                                     html.Button('3Y', id='3Y-button',
                                                 n_clicks=0, className='btn-secondary'),

                                     ], style={'padding': '15px', 'margin-left': '35px'})
                        ], width=4),analytics])


@ app.callback(
    Output('stock-dropdown', 'options'),
    Input('sector-dropdown', 'value')
)
def modify_stock_dropdown(sector):
    stocks = sector_stocks[sector]
    return stocks

stock_title = html.H1("AAPL", id="title",style={"align":"center"})
    
title = dbc.Row([dbc.Col([stock_title],md=8)],style={"align":"center"})
stock_data = web.DataReader('AAPL', 'yahoo',
                       start='01-01-2015', end=today)    
fig = go.Figure()
fig.add_trace(go.Candlestick(x=stock_data.index,
                             open=stock_data['Open'],
                             close=stock_data['Close'],
                             high=stock_data['High'],
                             low=stock_data['Low'],
                             name='Stock Price'))
fig.update_layout(
    paper_bgcolor='white',
    font_color='grey',
    height=500,
    width=1500,
    margin=dict(l=10, r=10, b=5, t=5),
    autosize=False,
    showlegend=False
)
min_date = '2021-01-01'
max_date = today
fig.update_xaxes(range=[min_date, max_date])
fig.update_yaxes(tickprefix='$')
raw_graph = dcc.Graph(id='price-chart', figure=fig)
# graph  = dbc.Col(dcc.Loading(, id='loading-price-chart',
#                             type='dot', color='#1F51FF'), md=8),

mean_52 = stock_data.resample('W')[
    'Close'].mean().iloc[-52:]
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=mean_52.index, y=mean_52.values))
fig2.update_layout(
    title={'text': 'Weekly Average Price', 'y': 0.9},
    font={'size': 8},
    plot_bgcolor='black',
    paper_bgcolor='black',
    font_color='grey',
    height=220,
    width=310,
    margin=dict(l=10, r=10, b=5, t=5),
    autosize=False,
    showlegend=False
)
fig2.update_xaxes(showticklabels=False, showgrid=False)
fig2.update_yaxes(range=[mean_52.min()-1, mean_52.max()+1.5],
                  showticklabels=False, gridcolor='darkgrey', showgrid=False)

@ app.callback(
    Output('title', 'children'),
    Input('stock-dropdown', 'value')
)
def modify_title(stock):
    return stock

@ app.callback(
    Output('price-chart', 'figure'),
    Input('stock-dropdown', 'value'),
    Input('complements-checklist', 'value'),
    Input('1W-button', 'n_clicks'),
    Input('1M-button', 'n_clicks'),
    Input('3M-button', 'n_clicks'),
    Input('6M-button', 'n_clicks'),
    Input('1Y-button', 'n_clicks'),
    Input('3Y-button', 'n_clicks'),
)
def change_price_chart(stock, checklist_values, button_1w, button_1m, button_3m, button_6m, button_1y, button_3y):
    # Retrieving the stock's data.
    df = web.DataReader(f'{stock}', 'yahoo',
                        start='01-01-2015', end=today)

    # Applying some indicators to its closing prices.
    df_bbands = bbands(df['Close'], length=20, std=2)
    # Measuring the Rolling Mean and Exponential Rolling means
    df['Rolling Mean'] = df['Close'].rolling(window=9).mean()
    df['Exponential Rolling Mean'] = df['Close'].ewm(
        span=9, adjust=False).mean()

    # Each metric will have its own color in the chart.
    colors = {'Rolling Mean': '#6fa8dc',
              'Exponential Rolling Mean': '#03396c', 'Bollinger Bands Low': 'darkorange',
              'Bollinger Bands AVG': 'brown',
              'Bollinger Bands High': 'darkorange'}

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], close=df['Close'],
                                 high=df['High'], low=df['Low'], name='Stock Price'))

    # If the user has selected any of the indicators in the checklist, we'll represent it in the chart.
    if checklist_values != None:
        for metric in checklist_values:

            # Adding the Bollinger Bands' typical three lines.
            if metric == 'Bollinger Bands':
                fig.add_trace(go.Scatter(
                    x=df.index, y=df_bbands.iloc[:, 0],
                    mode='lines', name=metric, line={'color': colors['Bollinger Bands Low'], 'width': 1}))

                fig.add_trace(go.Scatter(
                    x=df.index, y=df_bbands.iloc[:, 1],
                    mode='lines', name=metric, line={'color': colors['Bollinger Bands AVG'], 'width': 1}))

                fig.add_trace(go.Scatter(
                    x=df.index, y=df_bbands.iloc[:, 2],
                    mode='lines', name=metric, line={'color': colors['Bollinger Bands High'], 'width': 1}))

            # Plotting any of the other metrics remained, if they are chosen.
            else:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[metric], mode='lines', name=metric, line={'color': colors[metric], 'width': 1}))
    fig.update_layout(
        paper_bgcolor='white',
        font_color='grey',
        height=500,
        width=1000,
        margin=dict(l=10, r=10, b=5, t=5),
        autosize=False,
        showlegend=False
    )
    # Defining the chart's x-axis length according to the button clicked.
    # To do this, we'll alter the 'min_date' and 'max_date' global variables that were defined in the beginning of the script.
    global min_date, max_date
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if '1W-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(7)
        max_date = df.iloc[-1].name
    elif '1M-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(30)
        max_date = df.iloc[-1].name
    elif '3M-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(90)
        max_date = df.iloc[-1].name
    elif '6M-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(180)
        max_date = df.iloc[-1].name
    elif '1Y-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(365)
        max_date = df.iloc[-1].name
    elif '3Y-button' in changed_id:
        min_date = df.iloc[-1].name - datetime.timedelta(1095)
        max_date = df.iloc[-1].name
    else:
        min_date = min_date
        max_date = max_date
        fig.update_xaxes(range=[min_date, max_date])
        fig.update_yaxes(tickprefix='$')
        return fig
    # Updating the x-axis length.
    fig.update_xaxes(range=[min_date, max_date])
    fig.update_yaxes(tickprefix='$')
    return fig
    

app.layout = dbc.Container(
    [
        html.H1("The S&P 500 Sectors"),
        html.P("S&P 500 includes 11 industrial sectors."),
        html.P("Analyze S&P 500 stocks by sector."),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col([controls], md=2),
                dbc.Col( [title,raw_graph,time_boxes], md=10),
            ],
            align="center",
        ),
    ],
    fluid=True,
)

# Running the Dash app.
if __name__ == '__main__':
    app.run_server()