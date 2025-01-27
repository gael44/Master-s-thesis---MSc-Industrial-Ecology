# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 17:45:36 2024

@author: user
"""

import pandas as pd
import matplotlib.pyplot as plt
import os 
import numpy as np

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory
os.chdir(script_directory)

# Read data for various scenarios (Justice, Circular Economy, and Business-as-usual)
# Justice scenarios
ftp_LE_cap = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_LE_cap', index_col=[0])
ftp_SF_cap = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_SF_cap', index_col=[0])
ftp_SF = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_SF', index_col=[0])
ftp_EG = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_EG', index_col=[0])

# Circular economy scenarios
ftp_CEP_TOT_cap = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_CEP_TOT_cap', index_col=[0])
ftp_CEP_TOT = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_CEP_TOT', index_col=[0])
ftp_CEP_RE_cap = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_CEP_RE_cap', index_col=[0])
ftp_CEP_RE = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_CEP_RE', index_col=[0])
ftp_CEP_PLE_cap = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_CEP_PLE_cap', index_col=[0])
ftp_CEP_PLE = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_CEP_PLE', index_col=[0])
ftp_CEP_CP_cap = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_CEP_CP_cap', index_col=[0])
ftp_CEP_CP = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_CEP_CP', index_col=[0])

# Business-as-usual scenarios
ftp_BAU_cap = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_BAU_cap', index_col=[0])
ftp_BAU = pd.read_excel(script_directory + '/Results.xlsx', sheet_name = 'ftp_BAU', index_col=[0])

# List of countries from the data
countries = ftp_LE_cap.columns

# DataFrame for World Bank classification by income
data = {
    "Rank": [
        "Upper-Middle-Income", "High-Income", "Upper-Middle-Income", "High-Income", "High-Income",
        "High-Income", "High-Income", "Upper-Middle-Income", "Upper-Middle-Income", "Upper-Middle-Income",
        "High-Income", "High-Income", "High-Income", "Lower-Middle-Income", "Lower-Middle-Income",
        "High-Income", "High-Income", "High-Income", "Upper-Middle-Income", "Lower-Middle-Income",
        "High-Income", "Lower-Middle-Income", "Lower-Middle-Income", "Upper-Middle-Income",
        "Low-Income", "Upper-Middle-Income", "High-Income", "High-Income", "Upper-Middle-Income",
        "Lower-Middle-Income", "Upper-Middle-Income", "High-Income", "High-Income", "Upper-Middle-Income",
        "Lower-Middle-Income", "Upper-Middle-Income", "High-Income", "Lower-Middle-Income", "Upper-Middle-Income",
        "Lower-Middle-Income", "ROW"
    ]
}

# Country index for the analysis
index = [
    "ARG", "AUS", "BRA", "BRN", "CAN", "CHE", "CHL", "CHN", "COL", "CRI", "EU", "GBR", "HKG", "IDN",
    "IND", "ISL", "ISR", "JPN", "KAZ", "KHM", "KOR", "LAO", "MAR", "MEX", "MMR", "MYS", "NOR", "NZL",
    "PER", "PHL", "RUS", "SAU", "SGP", "THA", "TUN", "TUR", "TWN", "USA", "VNM", "ZAF", "ROW"
]

# Create a DataFrame for World Bank income classifications
rank = pd.DataFrame(data, index=index)

# Custom ordering for ranks
custom_order = ["ROW", "Low-Income", "Lower-Middle-Income", "Upper-Middle-Income", "High-Income"]

# Policy analysis for Circular Economy (CE) Total Footprint Change
ftp_CE = pd.concat([ftp_CEP_TOT, ftp_CEP_PLE, ftp_CEP_RE, ftp_CEP_CP ], axis = 0)

# Function to calculate relative change in global footprint
def relative_change_global(baseline, scenario):
    RC = (scenario.sum().sum() - baseline.sum().sum()) * 100 / baseline.sum().sum()  # Calculate relative change
    return RC

RC = {}
# Loop through each row (scenario) of the CE data and calculate relative change
for row in range(len(ftp_CE.index)):
    pol = ftp_CE.iloc[row, :]  # Get the row data (policy scenario)
    label = ftp_CE.index[row]  # Get the label (index value)
    pol = relative_change_global(ftp_BAU, pol)  # Calculate the relative change for the scenario
    RC[label] = pol  # Store the result

# Convert the dictionary to a DataFrame for easier viewing
RC = pd.DataFrame.from_dict(RC, orient="index", columns=["Relative change"])

# Function to calculate relative and absolute change per region
def relative_and_absolute_change_per_reg(baseline, scenario, rank, custom_order):
    def process_dataframe(df, rank, custom_order):
        # Combine the scenario DataFrame with rank DataFrame
        df = pd.concat([df, rank.T], axis=0).T.reset_index(drop=True).set_index('Rank').groupby('Rank').sum()
        df = df.reindex(index=custom_order)  # Reorder rows based on the custom order
        return df

    # Process both baseline and scenario DataFrames
    scenario = process_dataframe(scenario, rank, custom_order)
    baseline = process_dataframe(baseline, rank, custom_order)

    # Calculate relative change
    RC = (scenario - baseline.values) * 100 / baseline.values

    # Calculate absolute change
    AC = scenario - baseline.values

    return RC, AC

# Loop through each policy scenario and calculate regional changes
RC_per_reg = {}
for row in range(len(ftp_CE.index)):
    pol = ftp_CE.iloc[row, :].to_frame().T  # Get the row data (scenario)
    label = ftp_CE.index[row]  # Get the label (index value)
    RC_pol, AC_pol = relative_and_absolute_change_per_reg(ftp_BAU, pol, rank, custom_order)
    RC_per_reg[label] = RC_pol.iloc[:, 0]  # Store relative change

# Convert dictionary to DataFrame for easier viewing
Abs_contrib_RC_per_reg_non_weighted = pd.concat(RC_per_reg.values(), axis=1).T

# Calculate regional weights for further decomposition of the global relative change
reg_ftp = pd.concat([ftp_CE, rank.T], axis=0).T.reset_index(drop=True).set_index('Rank').groupby('Rank').sum().reindex(index=custom_order).T
reg_ftp['total ftp'] = reg_ftp.sum(axis=1)  # Sum the total footprint for each region
reg_ftp.loc[:, reg_ftp.columns != 'total ftp'] = reg_ftp.loc[:, reg_ftp.columns != 'total ftp'].div(reg_ftp['total ftp'], axis=0)  # Normalize by total footprint
weights = reg_ftp.drop(columns=['total ftp'])  # Weights per region

# Calculate the final contribution for each region using weights
Abs_contrib_RC_per_reg = Abs_contrib_RC_per_reg_non_weighted * weights

# Discrete and continuous analysis for SF (Social Foundation)
# Calculate how many countries below their DLS (doughnut lower bound) in BAU reach them in CE
diff_BAU = ftp_SF_cap - ftp_BAU_cap.values
count_BAU_tot = np.sum(diff_BAU.values > 0)  # Count all positive elements.

# Continuous analysis for SF: Calculate average distance to DLS for countries below their DLS in BAU
below_DLS_BAU = diff_BAU.loc[:, diff_BAU.iloc[0] > 0]
below_DLS_CE = ftp_CEP_TOT_cap.loc[:, below_DLS_BAU.columns]
below_DLS_SF = ftp_SF_cap.loc[:, below_DLS_BAU.columns]
below_DLS_BAU = ftp_BAU_cap.loc[:, below_DLS_BAU.columns]

# Calculate average distance for SF in both BAU and CE scenarios
av_dist_SF_BAU = (below_DLS_SF - below_DLS_BAU.values)
av_dist_SF_CE = (below_DLS_SF - below_DLS_CE.values)

# Calculate the change in distance for SF
change_distance_SF = av_dist_SF_CE - av_dist_SF_BAU

# Prepare the result
change_distance_SF = change_distance_SF.mean(axis=1)
change_distance_SF.index = ['Change distance to DLS']  # Rename index for clarity

# Combine results into a single DataFrame
results = pd.concat([Abs_contrib_RC_per_reg.sum(axis=1), RC_per_reg['ROW'], change_distance_SF], axis=1)
results.columns = ['Change in global footprint (percentage)', 'Change in ROW footprint (percentage)', 'Change in distance to DLS']
