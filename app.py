# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from funding import df, df2, nextFundingTime
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# Chart table
fig = go.Figure(data=[go.Table(
    header=dict(values=list(df2.columns)),
    cells=dict(values=[df2['Perps Name'],
                        df2['Predicted hourly funding rate in %'],
                        df2['Price'],
                        df2['OI in lots'],
                        df2['OI in notional'],
                        df2['Volume'],
                        df2['Volume in notional']]))
    ])

fig2 = px.bar(df, x=df['Perps Name'], y=df['Predicted hourly funding rate in %'])


app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    html.Div(children=f'''
        Next Funding Time: {nextFundingTime}
    '''),
    dcc.Graph(
        id='example-graph-2',
        figure=fig
    ),
    dcc.Graph(
        id='example-graph-3',
        figure=fig2
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)