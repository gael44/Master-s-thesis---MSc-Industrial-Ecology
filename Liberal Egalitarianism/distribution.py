# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:00:14 2024

@author: user
"""

import pandas as pd
import os
import numpy as np

script_directory = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory
os.chdir(script_directory)

# Normalize and split the directory path
path_parts = script_directory.split(os.sep)

# Remove "liberal egalitarianism" from the path parts
if "liberal egalitarianism" in path_parts:
    path_parts.remove("liberal egalitarianism")

path_pop = os.path.join(os.sep.join(path_parts), "Egalitarianism")
path_pop = os.path.abspath(path_pop)
pop = pd.read_csv(path_pop + '\\population.csv', sep=',', index_col=[0])

path_1 = os.path.join(os.sep.join(path_parts), "Cleaning and shaping ICIO", "cleant tables")
path_1 = os.path.abspath(path_1)
# Load the CSV files using the corrected path
A = pd.read_csv(path_1 + '\\A_ICIO.csv', sep=',', index_col=[0, 1], header=[0, 1])
Y = pd.read_csv(path_1 + '\\Y_sc_ICIO_agg.csv', sep=',', index_col=[0, 1], header=[0])
F = pd.read_csv(path_1 + '\\F_ICIO.csv', sep=',', index_col=[0], header=[0, 1])

country_lab = Y.columns

#%% Calculate footprint threshold and the baseline

path_BAU = os.path.join(os.sep.join(path_parts), "Results analysis", "Results.xlsx")

ftp_BAU_cap = pd.read_excel(path_BAU, sheet_name='ftp_BAU_cap', index_col=[0])
ftp_BAU = pd.read_excel(path_BAU, sheet_name='ftp_BAU', index_col=[0])

threshold_cap = np.median(ftp_BAU_cap)

threshold_country = threshold_cap * pop.squeeze()

#%% Calculating tax revenue with tax rate of 50% and 100%

# Calculate the difference between BAU footprints and C_PB
diff = ftp_BAU.squeeze() - threshold_country
diff = pd.DataFrame(diff, columns=['difference'], index=country_lab).T

# Calculate tax revenues
well_off = diff.loc['difference'][diff.loc['difference'] > 0]
tax_revenue_50 = (well_off * 0.5).sum()
tax_revenue_100 = well_off.sum()

# Redistribution of the tax revenue
worse_off = diff.loc['difference'][diff.loc['difference'] < 0]  # Countries below their threshold
total_worse_off = worse_off.abs().sum()  # Total distance below threshold

redistribution_full = pd.DataFrame(0, index=['redistribution'], columns=country_lab)

# Take off half of their overshoot from well_off countries
redistribution_full.loc['redistribution', well_off.index] = -(well_off * 0.5)

#%%
sensitivity = "no"

if sensitivity == "yes":
    revenue = tax_revenue_100
elif sensitivity == "no":
    revenue = tax_revenue_50

#%%
# Redistribution logic
if revenue >= total_worse_off:
    # Redistribute the tax revenue to worse_off countries
    redistribution_full.loc['redistribution', worse_off.index] = worse_off.abs()
    
    remaining_budget = revenue - total_worse_off
    
    # Calculate proportional shares of the remaining budget based on tax revenue contributions
    tax_revenue_contribution = well_off / well_off.sum()  # Proportional shares based on tax revenue
    redistribution_full.loc['redistribution', well_off.index] += remaining_budget * tax_revenue_contribution
else:
    # Partial allocation to minimize the average distance
    abs_needs = -worse_off  # Absolute values of the needs
    allocation = np.zeros_like(abs_needs)
    
    while revenue > 0:
        remaining_needs = abs_needs[abs_needs > 0]
        if len(remaining_needs) == 0:
            break
        
        # Distribute budget equally among remaining needs
        per_unit_allocation = revenue / len(remaining_needs)
        reduction = np.minimum(per_unit_allocation, abs_needs)
        
        allocation += reduction
        abs_needs -= reduction
        revenue -= np.sum(reduction)
    
    redistribution_full.loc['redistribution', worse_off.index] = -abs_needs

# Convert redistribution into a DataFrame
redi = pd.DataFrame(redistribution_full.loc['redistribution'])

if sensitivity == "yes":
    ftp_LE_s = ftp_BAU + redi.T.values
    ftp_LE_s.index = ['ftp_LE']
    ftp_LE_cap_s = ftp_LE_s / pop.squeeze()
    ftp_LE_cap_s = pd.DataFrame(ftp_LE_cap_s)
    ftp_LE_cap_s.index = ['ftp_LE_cap']
else:
    ftp_LE = ftp_BAU + redi.T.values
    ftp_LE.index = ['ftp_LE']
    ftp_LE_cap = ftp_LE / pop.squeeze()
    ftp_LE_cap = pd.DataFrame(ftp_LE_cap)
    ftp_LE_cap.index = ['ftp_LE_cap']

#%%

# Add the desired subdirectory
path_1 = os.path.join(os.sep.join(path_parts), "Results analysis")

# Ensure the directory exists
os.makedirs(path_1, exist_ok=True)

# Define the Excel file path
excel_path = os.path.join(path_1, 'results.xlsx')

# Append the DataFrame to an Excel file, creating a new sheet named after the DataFrame
with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    ftp_LE_cap.to_excel(writer, sheet_name='ftp_LE_cap', index=True)
    ftp_LE.to_excel(writer, sheet_name='ftp_LE', index=True)
