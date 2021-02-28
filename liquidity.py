# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 15:05:45 2021

@author: yukih
"""
import dash
import dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from decimal import Decimal
from funding import FTXClient
import os

os_api_key = os.environ['FTX_API_KEY']
os_api_secret = os.environ['FTX_API_SECRET']

# Price |
new_instance = FTXClient()
new_instance.__init__(os_api_key,os_api_secret)

all_listed = new_instance.get_futures()

perps_list = []
for listed in all_listed:
    if listed['perpetual'] is not False:
        perps_list.append(listed)

def standard_dp(number) -> Decimal:
    if number <= 0.00001:
        return Decimal(number).quantize(Decimal('0.000000001'))
    elif 0.00001 < number <= 0.0001:
        return Decimal(number).quantize(Decimal('0.00000001'))
    elif 0.0001 < number <= 0.001:
        return Decimal(number).quantize(Decimal('0.0000001'))
    elif 0.001 < number <= 0.01:
        return Decimal(number).quantize(Decimal('0.000001'))
    elif 0.01 < number <= 0.1:
        return Decimal(number).quantize(Decimal('0.00001'))
    elif 0.1 < number <= 1:
        return Decimal(number).quantize(Decimal('0.0001'))
    elif 1 < number <= 10:
        return Decimal(number).quantize(Decimal('0.001'))
    elif 10 < number <= 100:
        return Decimal(number).quantize(Decimal('0.01'))
    elif 100 < number <= 10000:
        return Decimal(number).quantize(Decimal('0.1'))
    elif number > 10000:
        return Decimal(number).quantize(Decimal('1'))

def convert_dp(number, dp: str) -> Decimal:
    # e.g to conver to 3dp, pass in '0.001', for 1 dp '0.1', for 0 dp, '1'
    return Decimal(number).quantize(Decimal(dp))
            

for perp in perps_list:
    perp['bid_ask_spread'] = perp['ask'] - perp['bid']     
    perp['bid_ask_spread in %'] = convert_dp((perp['bid_ask_spread'] / perp['last'])*100, '0.0001')
    perp['bid_ask_spread'] = standard_dp(perp['ask'] - perp['bid'])     
    perp['index'] = standard_dp(perp['index'])
    perp['change1h'] = convert_dp(perp['change1h']*100, '0.01')
    perp['change24h'] = convert_dp(perp['change24h']*100, '0.01')
    perp['volumeUsd24h'] = convert_dp(perp['volumeUsd24h'], '1')

    # remove other info in json
    [perp.pop(key) for key in ["changeBod",
                              "description",
                              "enabled",
                              "expired",
                              "expiry",
                              "expiryDescription",
                              "group",
                              "imfFactor",
                              "lowerBound",
                              "marginPrice",
                              "moveStart",
                              "perpetual",
                              "positionLimitWeight",
                              "postOnly",
                              "priceIncrement",
                              "sizeIncrement",
                              "type",
                              "underlying",
                              "underlyingDescription",
                              "upperBound",
                              "volume"]]
 
df = pd.DataFrame(perps_list)

# Rename columns 
df.rename(columns={'bid': 'Bid',
                    'ask': 'Ask',
                    'change1h': '1h Price %', 
                    'change24h': '24h Price %',
                    'index': 'Index Price',
                    'last': 'Last Price',
                    'mark': 'Mark Price',
                    'name': 'Futures Name',
                    'volumeUsd24h': '24h NotionalVolume',
                    'bid_ask_spread': 'Bid-ask spread',
                    'bid_ask_spread in %': 'Bid-ask spread in %'},
          inplace=True)


# Reorder columns
df = df[['Futures Name',
         'Bid',
         'Ask',
         'Bid-ask spread',
         'Bid-ask spread in %',
         'Index Price',
         'Last Price',
         'Mark Price',
         '1h Price %', 
         '24h Price %',
         '24h NotionalVolume']] 
 
app = dash.Dash(__name__)
app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    )

if __name__ == '__main__':
    app.run_server(debug=True)
