# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 15:44:10 2024

@author: user
"""
# data from ComTrade 2021.

# deflating prices allows to account for the real value of goods without the effect of price variation.
# We used prices of 2021 to calculate the monetary value of DLS translated into IO sectors.
# The IO data to which DLS will be compared dates from 2021 as well. Consequently there is no need for deflation.

import pandas as pd
import os

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory
os.chdir(script_directory)

# Define path to the TradeData Excel file
path = script_directory + r'/data/Prices/TradeData_goods.xlsx'
# Read the trade data from the Excel file
trade_data = pd.read_excel(path)

#%% Calculate world average price

# Filter relevant columns from the trade data
trade_data = trade_data.loc[:, ['cmdDesc', 'cmdCode', 'qty', 'qtyUnitAbbr', 'primaryValue']]

#%%
# Drop rows with missing values to ensure clean data
trade_data = trade_data.dropna()

# Calculate the price per unit for each item
trade_data['price'] = trade_data['primaryValue'] / trade_data['qty']

# Calculate the total quantity per cmdDesc (commodity description)
trade_data['total_qty'] = trade_data.groupby('cmdDesc')['qty'].transform('sum')

# Calculate the weight of each entry's quantity relative to the total quantity for that cmdDesc
trade_data['weight'] = trade_data['qty'] / trade_data['total_qty']

# Calculate the weighted price by multiplying the price by the weight of the quantity
trade_data['weighted_price'] = trade_data['price'] * trade_data['weight']

# Now, calculate the weighted average price for each commodity (cmdDesc)
weighted_avg_price = trade_data.groupby('cmdDesc').agg({
    'weighted_price': 'sum',  # Sum the weighted prices
})

# Reset the index and set a new hierarchical index if needed
weighted_avg_price = weighted_avg_price.reset_index().set_index(['cmdDesc'], append=True)

#%% Adding units

# Retrieve the unique units for each commodity (cmdDesc) from the trade data
units = trade_data.dropna(subset=['qtyUnitAbbr'])[['cmdDesc', 'qtyUnitAbbr','cmdCode']].drop_duplicates()

# Ensure each cmdDesc has a corresponding unit, map it to the weighted_avg_price index
weighted_avg_price = weighted_avg_price.reset_index()

# Merge the unit information into the weighted_avg_price DataFrame
weighted_avg_price = weighted_avg_price.merge(units, on='cmdDesc', how='left')

# Add the 'unit/euro' format to the unit column to display it clearly
weighted_avg_price['euro/unit'] = 'euro/' + weighted_avg_price['qtyUnitAbbr'] 

# Set the index again with the 'cmdDesc' and the 'euro/unit' column added
weighted_avg_price = weighted_avg_price.set_index(['cmdDesc', 'euro/unit'])

# Optionally, drop the extra 'qtyUnitAbbr' column if it's no longer needed
weighted_avg_price = weighted_avg_price.drop(columns=['qtyUnitAbbr','level_0'])

#%%
# Convert the prices to Euros based on the average USD/EUR exchange rate for 2021
# 1 USD = 0.8458 EUR
weighted_avg_price = weighted_avg_price * 0.8458

# Define the output path to save the result in an Excel file
output_path = script_directory + r'/data/DLS_requirements_Exiobase.xlsx'
# Write the weighted average price data to the Excel file
with pd.ExcelWriter(output_path, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
    weighted_avg_price.to_excel(writer, sheet_name='Price', index=True)
