# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 00:31:53 2021

@author: yukih
"""

import time
from api_box.ftx import os_api_key, os_api_secret, FTXClient 
import pandas as pd

start_time = time.time()


"""Part 1: Get data via FTX API"""

# Initialize instance with api keys        
new_instance = FTXClient()      
new_instance.__init__(os_api_key,os_api_secret)

# Get list of all futures
# futures_lst = list(future['name'] for future in new_instance._get('futures'))

# Get list(set) of all existing futures with funding 
all_funding = new_instance._get('/funding_rates')
ff_set = list(set(future['future'] for future in all_funding))
#print(ff_set)

# get existing funding rates for all futures and add to dictionary ff_dict
ff_dict = {}
nextFundingTime = {}

print('Getting data and calculating...')
for ff in ff_set:
    # get stats for each future and linked to var ff_stats
    ff_stats = new_instance.get_stats(ff)
    nextFundingTime = ff_stats['nextFundingTime']
    print(ff_stats)
    
    # check if OI is None, if so it is likely delisted and then ignore
    if ff_stats['openInterest'] is not None:
        ff_stats['price'] = new_instance.get_price(ff)
        # remove nextFundingTime key-value pair
        [ff_stats.pop(key) for key in ["nextFundingTime"]]
        # add in notional calculations for OI and volume and calc funding rate in %
        ff_stats['openInterestNotional'] = ff_stats['openInterest']*ff_stats['price']
        ff_stats['volumeNotional'] = ff_stats['volume']*ff_stats['price']
        ff_stats['nextFundingRate'] = ff_stats['nextFundingRate']*100
        ff_dict[ff] = ff_stats
        
print("---API script took estimated %s seconds ---" % (time.time() - start_time))
 
"""Part 2: Clean data and add to Pandas dataframe"""

# Create dataframe with ff_dict, transpose to get each coin data on each row
df = pd.DataFrame(ff_dict).transpose()
df = df.reset_index()

# Rename dataframe to be more readable
df.rename(columns={'index': 'Perps Name',
                    'nextFundingRate': 'Predicted hourly funding rate in %',
                    'price': 'Price', 
                    'openInterest': 'OI in lots',
                    'openInterestNotional': 'OI in notional',
                    'volume': 'Volume',
                    'volumeNotional': 'Volume in notional'},
          inplace=True)

# snap_time = datetime.now().now().strftime('%d%m%Y-%H.%M.%S')
# file_name = snap_time +'.csv'

# df.to_csv(file_name, index=False)

# Reorder columns
df = df[['Perps Name',
       'Predicted hourly funding rate in %',
       'Price',
       'OI in lots',
       'OI in notional',
       'Volume',
       'Volume in notional']].sort_values(by='OI in notional',ascending=False)

#Round off a column "col_name" to some dp specified
def column_rounder(col_name: str, dp: int): 
        df[col_name] = df[col_name].astype(float).round(dp)
        
for col in ['OI in lots','OI in notional','Volume','Volume in notional']:
    column_rounder(col, 0)        
    
# Convert original dataframe to string dataframe "df2"
df2 = df.copy().astype('string')

# modify funding rate column by 4 d.p and add %
df2['Predicted hourly funding rate in %'] = df['Predicted hourly funding rate in %'].map('{:,.4f}%'.format)

# comma separate for numbers
def comma_separate(col_name: str):
    df2[col_name] = pd.to_numeric(df[col_name].fillna(0), errors='coerce')    
    df2[col_name] = df[col_name].map('{:,.0f}'.format)

for col in ['OI in lots','OI in notional','Volume','Volume in notional']:
    comma_separate(col)        
        
print(df2)
