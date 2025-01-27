import os 

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Import necessary libraries
import pandas as pd
import numpy as np
from Cleaning_IOT import cleaning_IOT_function
from shaping_functions import compute_EU_shaped_matrix
from sorting_function import sorting

# Set display format for pandas
pd.set_option('display.float_format', '{:.0f}'.format)

# Define the path to the Disaggregated Construction MRIOT data
path_1 = script_directory + "\DisaggregatedConstructionMRIOT/"

# Load CSV files for the residuals distributed data (Z, Y, F)
Z = pd.read_csv(path_1 + 'Z_sub_agg_residualsdistributed.csv', sep=',')
Y = pd.read_csv(path_1 + 'Y_sub_agg_residualsdistributed.csv', sep=',', header=[0, 2])
F = pd.read_csv(path_1 + 'F_sub_agg_residualsdistributed.csv', sep=',')

# Normalize and split the directory path
path_parts = script_directory.split(os.sep)

# Remove "cleaning and shaping icio" if present in the path parts
if "cleaning and shaping icio" in path_parts:
    path_parts.remove("cleaning and shaping icio")

# Reconstruct the script directory path after modification
script_dir = os.sep.join(path_parts)
path_pop = os.path.join(script_dir, "Egalitarianism")

# Ensure path is absolute
path_pop = os.path.abspath(path_pop)

# Clean and prepare the input data (Z, Y, F)
Z_clean, Y_clean, F_clean = cleaning_IOT_function(Z, Y, F)

# Load country and sector information for reshaping ICIO tables
path_2 = script_directory + r'\Country_and_sectors.xlsx'
EU_countries = pd.read_excel(path_2, sheet_name='EU_countries', header=None)[0].tolist()
sectors = pd.read_excel(path_2, sheet_name='sectors', header=None)[0].tolist()

# Reshape the ICIO tables for CE policy implementation
Z, Y_s_c, Y_s_s, F = compute_EU_shaped_matrix(Z_clean, Y_clean, F_clean, EU_countries, sectors)

# Clean up infinite and NaN values in Z and Y
Z.replace([np.inf, -np.inf], np.nan, inplace=True)
Z.replace(np.nan, 0, inplace=True)
Z = Z.astype(float)
Y = Y.astype(float)

# Calculate total output (x)
x = Z.sum(axis=1) + Y.sum(axis=1)

# Clean up infinite and NaN values in x
x.replace([np.inf, -np.inf], np.nan, inplace=True)
x.replace(np.nan, 0, inplace=True)
x_out = x.copy()

# Calculate inverse of diagonal elements of x
x_out[x_out != 0] = 1 / x_out[x_out != 0]
inv_diag_x = np.diag(x_out.values)

# Compute the technical coefficients matrix (A)
A = Z.values @ inv_diag_x
A = pd.DataFrame(A, columns=Z.columns, index=Z.index)
A = A.astype(float)

# Identity matrix for Leontief inverse calculation
I = np.identity(A.shape[0])

# Leontief inverse matrix
L = np.linalg.inv(I - A)

# Impact indicator for GHG emissions
impact_indicator = pd.DataFrame(F.loc['GHG'], columns=['GHG']).T

# Calculate environmental extension vector (f)
impact_indicator = impact_indicator.astype(float)
inv_diag_x = inv_diag_x.astype(float)
f = impact_indicator @ inv_diag_x
f = f.replace([np.inf, -np.inf, np.nan], 0)

# Calculate the total production (ftp) for the BAU scenario
ftp_BAU = f.values @ L @ Y
ftp_BAU = ftp_BAU * 1e6  # Convert to kilotons
ftp_BAU = ftp_BAU.T.groupby('country').sum().T
ftp_BAU.index = ['ftp_BAU']

# Load population data
pop = pd.read_csv(path_pop + r'/population.csv', index_col=0)
pop = pop.T.sort_index().T

# Calculate footprint per capita (BAU scenario)
ftp_BAU_cap = ftp_BAU / pop.squeeze()
ftp_BAU_cap.index = ['ftp_BAU_cap']

# Sort the matrices
Z = sorting(Z)
A = sorting(A)
F = sorting(F)
Y_s_c = sorting(Y_s_c)
Y_s_s = sorting(Y_s_s)

# Save cleaned and sorted tables to CSV
Z.to_csv(script_directory + '/cleant tables/Z_ICIO.csv', index=True)
A.to_csv(script_directory + '/cleant tables/A_ICIO.csv', index=True)
F.to_csv(script_directory + '/cleant tables/F_ICIO.csv', index=True)
Y_s_c.to_csv(script_directory + '/cleant tables/Y_sc_ICIO_agg.csv', index=True)
Y_s_s.to_csv(script_directory + '/cleant tables/Y_ss_ICIO_agg.csv', index=True)

# Construct the path to save results
path_1 = os.path.join(script_dir, "Results analysis")

# Ensure the results directory exists
os.makedirs(path_1, exist_ok=True)

# Define the Excel file path to save results
excel_path = os.path.join(path_1, 'Results.xlsx')

# Append the calculated footprints to the Excel file
with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    ftp_BAU_cap.to_excel(writer, sheet_name='ftp_BAU_cap', index=True)
    ftp_BAU.to_excel(writer, sheet_name='ftp_BAU', index=True)
