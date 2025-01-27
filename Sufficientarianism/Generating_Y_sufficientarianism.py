# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 08:40:32 2024

@author: user
"""

# -*- coding: utf-8 -*-µ
"""
Created on Fri Oct 25 16:59:31 2024

@author: user
"""

import pandas as pd
import os

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory
os.chdir(script_directory)

# Normalize and split the directory path into parts
path_parts = script_directory.split(os.sep)

# Remove "sufficientarianism" from the path if it exists
if "sufficientarianism" in path_parts:
    path_parts.remove("sufficientarianism")

#%% Import necessary libraries
import numpy as np

# Import custom functions for shaping and processing data
from Shaping_function import compute_Y_EU_single
from Building_Y_DLS_exiobase import building_Y_DLS_exiobase
from ICIO_match import ICIO_match

#%% Load data

# Path to EU country list and read the file
path_EU_countries = script_directory + '/data/Country_sector.xlsx'
EU_countries = pd.read_excel(path_EU_countries, sheet_name='EU_countries', header=None)[0].tolist()

# Path to Exiobase data and read the file
path_Y_exiobase  = script_directory + '/data/Y_exiobase.txt'
Y_exiobase = pd.read_csv(path_Y_exiobase, sep='\t', index_col=[0, 1], header=[0, 1])

#%% Compute the EU-specific demand vector
Y_EU_single = compute_Y_EU_single(Y_exiobase, EU_countries)

#%% Define file paths for additional data
path_pop = os.path.join(os.sep.join(path_parts), "Egalitarianism", "WPP2024_Demographic_Indicators_Medium.csv", "s.csv")
path_DLS = script_directory + '/data/DLS_requirements_Exiobase.xlsx'
path_country_label_match = os.path.join(os.sep.join(path_parts), "Sufficientarianism",'data', 'country_label_correspondence.xlsx' )

#%% Building the demand data using a custom function

# Call the function to build the Y_DLS_exiobase matrix and population data
Y_DLS_exiobase, pop = building_Y_DLS_exiobase(Y_EU_single, path_DLS, path_pop, path_country_label_match)

#%% Reshape the modified Exiobase demand vector into ICIO format

# Define the path for the ICIO correspondence matrix
path_correspondence = script_directory + '/data/Concordance matrix ICIO.xlsx'

# Perform the ICIO match and get the adjusted Y matrix
Y = Y_DLS_exiobase
Y_SF = ICIO_match(Y_DLS_exiobase, path_correspondence)

# Note: Y_ICIO vector is the baseline of decent living above which emissions will be taxed in the modelling of liberal egalitarianism.

#%% Load cleaned ICIO tables for further processing

# Construct path to the cleaned ICIO tables and ensure the path is absolute
path_1 = os.path.join(os.sep.join(path_parts), "Cleaning and shaping ICIO", "cleant tables")
path_1 = os.path.abspath(path_1)

# Read the cleaned data for Y, A, and F matrices
Y = pd.read_csv(path_1 + '/Y_sc_ICIO_agg.csv', index_col=[0, 1], header=[0])
A = pd.read_csv(path_1 + '/A_ICIO.csv', index_col=[0, 1], header=[0, 1])
F = pd.read_csv(path_1 + '/F_ICIO.csv', index_col=[0], header=[0, 1])

# Retrieve the country labels from the Y matrix
country_lab = Y.columns

# Select the CO2 impact indicator from F
impact_indicator = pd.DataFrame(F.loc['CO2'], columns=['CO2']).T

#%% Calculate thresholds and baseline footprints using Leontief inverse

# Identity matrix based on the shape of A
I = np.identity(A.shape[0])

# Calculate the Leontief inverse matrix (L)
L = np.linalg.inv(I - A)

# Sum the total demand for all sectors
y_total = Y.sum(1)

# Calculate the total outputs using Leontief inverse and total demand
x = L @ y_total
x_out = x.copy()
x_out[x_out != 0] = 1 / x_out[x_out != 0]

# Construct the inverse diagonal matrix of outputs
inv_diag_x = np.diag(x_out)

# Calculate the impact factor (f) using the footprint matrix and inverse diagonal matrix
f = impact_indicator @ inv_diag_x

# Compute the BAU (business-as-usual) footprint by multiplying the impact factor with Leontief inverse and Y
ftp_BAU = f.values @ L @ Y.values * 1000000
ftp_BAU = pd.DataFrame(ftp_BAU, index=['footprint'], columns=country_lab)

#%% Compute the SF (sufficiency footprint)

# Calculate the sufficiency footprint by adjusting with Y_SF
ftp_SF = (f.values @ L @ Y_SF.values) * 1000000
ftp_SF = pd.DataFrame(ftp_SF, index=['footprint'], columns=country_lab)

#%% Visualize the footprint comparison

import matplotlib.pyplot as plt

# Concatenate the BAU and CO2 footprints for comparison
ftp = pd.concat([ftp_BAU, ftp_SF], axis=0).T
ftp = ftp.reset_index()
ftp.columns = ['country', 'BAU footprint', 'CO2 footprint']

# Set the positions of the bars on the x-axis
x = np.arange(len(ftp['country']))

# Width of the bars
width = 0.4

# Create a figure and axes for the plot
fig, ax = plt.subplots(figsize=(14, 7))

# Plot the BAU and CO2 footprint bars
ax.bar(x - width / 2, ftp['BAU footprint'], width=width, label='BAU Footprint', color='skyblue', edgecolor='black')
ax.bar(x + width / 2, ftp['CO2 footprint'], width=width, label='CO₂ Footprint', color='green', edgecolor='black')

# Set the labels and title for the plot
ax.set_xlabel('Country', fontsize=14)
ax.set_ylabel('Footprint', fontsize=14)
ax.set_title('Comparison of BAU and CO₂ Footprints by Country', fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(ftp['country'], rotation=45, fontsize=12)
ax.legend(fontsize=12)

# Adjust layout for better display
plt.tight_layout()

# Display the plot
plt.show()

#%% Save the sufficiency footprint to a file

# Define the path for the results directory and ensure it exists
path_1 = os.path.join(os.sep.join(path_parts), "Results analysis")
os.makedirs(path_1, exist_ok=True)

# Save the sufficiency footprint (ftp_SF) as a CSV file
file_path = os.path.join(path_1, 'ftp_SF.csv')
ftp_SF.to_csv(file_path, index=True)
