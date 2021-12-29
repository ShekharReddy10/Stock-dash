from matplotlib import ticker
import dash
from dash import dcc
from dash import html
from datetime import date, datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
# model
from model import prediction
from sklearn.svm import SVR
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt 


def get_stock_price_fig(df):
    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Opening Price vs Date")
    return fig

def get_stock_price_fig2(df1,df2,val1,val2):
    fig=px.line(df1,x="Date",y=["Open"],title="Comparing stocks between "+val1+" and "+val2)
    fig.add_scatter(x=df2["Date"],y=df2["Open"],text=val2)
    return fig


def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="EWA_20",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig


app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Roboto&display=swap"
    ])
server = app.server
# html layout of site
app.layout = html.Div(
    [
        html.Div([# header
                    html.Img(src=app.get_asset_url('img.png'),id="logos"),
                    html.H1("Stock Visualising and Forecasting",id="heading_text")
                ],
                 className="Border"),
        html.Div(
            [
                # Navigation
                html.Div([
                    dcc.ConfirmDialog(
                        id='alert',
                        message="Enter Valid input",
                    ),
                    html.P("Input stock code: ",id="block_heading"),
                    html.Div([
                        dcc.Input(id="dropdown_tickers",placeholder="Enter stock code", type="text"),
                        html.Button("Submit", id='submit'),
                    ],
                             className="form")
                ],
                         className="input-place"),
                html.Div([
                    dcc.DatePickerRange(id='my-date-picker-range',
                                        min_date_allowed=dt(1995, 8, 5),
                                        max_date_allowed=dt.now(),
                                        initial_visible_month=dt.now(),
                                        end_date=dt.now().date()),
                ],
                         className="date"),
                html.Div([
                    html.Button(
                        "Stock Price", className="stock-btn", id="stock"),
                    html.Button("Indicators",
                                className="indicators-btn",
                                id="indicators"),
                    dcc.Input(id="n_days",
                              type="text",  
                              placeholder="number of days"),
                    html.Button(
                        "Forecast", className="forecast-btn", id="forecast")

                ],

                         className="buttons"),
                html.Div([
                    dcc.ConfirmDialog(
                        id='alert1',
                        message="Enter Valid inputs",
                    ),
                    html.H2("Enter stocks code to compare",id="compare"),
                    html.Div([
                        dcc.Input(id="dropdown_tickers1",placeholder="Enter stock code", type="text"),
                        dcc.Input(id="dropdown_tickers2",placeholder="Enter stock code", type="text"),
                        html.Button("Submit",id="compare_submit"),
                    ],
                        className="compare_div")
                ],className="compare_big_div"),
                html.Div([
                    html.H4("Do you want to invest click here...",id="invest"),
                html.A(
                    href="https://groww.in/",
                    children=[
                    html.Img(src=app.get_asset_url('groww.png'),id="groww"),
                ],),


                html.A(
                    href="https://www.angelone.in/",
                    children=[
                    html.Img(src=app.get_asset_url('Angel.png'),id="Angel")
                ],),
            ],className="logoes"),
                # here
            ],
            className="nav"),

        # content
        html.Div(
            [
                html.Div(
                    [ 
                        html.Img(id="logo"),
                        html.P(id="ticker")
                    ],
                    className="header"),
                html.Div(id="description", className="decription_ticker"),
                html.Div([], id="graphs-content"),
                html.Div([], id="main-content"),
                html.Div([], id="forecast-content"),
                html.Div([], id="compare_stocks")
            ],
            className="content"),
    ],
    className="container")


# @app.callback([
#     Output("alert","displayed")
# ],[Input("submit","n_clicks")],[State("dropdown_tickers", "value")])
# def fun(n,val):
#     if val == None:
#         raise PreventUpdate
#     else:
#         ticker = yf.Ticker(val)
#         #print(ticker)
#         inf = ticker.info
#         if(inf['logo_url']==""):
#             return True
#         return False
    
# callback for company info
@app.callback([
    Output("alert","displayed"),
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(n, val):  # inpur parameter(s)
    if n == None:
        return  False,"", "", "", None, None, None
        # raise PreventUpdate
    else:
        if val == None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            #print(ticker)
            inf = ticker.info
            print(inf['logo_url']=="")
            if(inf['logo_url']==""):
                return True,"", "", "", None, None, None
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df[['logo_url', 'shortName', 'longBusinessSummary']]
            return False,df['longBusinessSummary'].values[0], df['logo_url'].values[
                0], df['shortName'].values[0], None, None, None

@app.callback([
    Output("alert1","displayed"),
    Output("compare_stocks","children"),
],[
    Input("compare_submit","n_clicks")
],[State("dropdown_tickers1","value"),State("dropdown_tickers2","value")])
def compare_stock_price(n,val1,val2):
    if n== None:
        return False,[""]
    if val1==None or val2==None:
        raise PreventUpdate
    else:
        ticker1=yf.Ticker(val1)
        ticker2=yf.Ticker(val2)
        inf1=ticker1.info
        inf2=ticker2.info
        if(inf1['logo_url']=="" or inf2['logo_url']==""):
            return True,""
        df1=yf.download(val1)
        df2=yf.download(val2)
    df1.reset_index(inplace=True)
    df2.reset_index(inplace=True)
    fig=get_stock_price_fig2(df1,df2,val1,val2)
    return False,[dcc.Graph(figure=fig)]    
    

# callback for stocks graphs
@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]


# callback for indicators
@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]


# callback for forecast
@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)
