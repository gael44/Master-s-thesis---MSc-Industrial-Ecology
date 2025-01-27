# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 11:25:47 2024

@author: user
"""
import os
import pandas as pd 

# Function to disaggregate a given dataset Y
def disaggregation_cons(Y):
    
    # Get the directory where the script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Change the working directory to the script's directory
    os.chdir(script_directory)

    # Split the directory path into parts
    path_parts = script_directory.split(os.sep)

    # Remove "sufficientarianism" from the path if it exists
    if "sufficientarianism" in path_parts:
        path_parts.remove("sufficientarianism")
        
    # Construct the path to the directory containing cleaned ICIO tables
    path_1 = os.path.join(os.sep.join(path_parts), "Cleaning and shaping ICIO", "cleant tables")

    # Ensure the path is in absolute format
    path_1 = os.path.abspath(path_1)
    
    # Define the full path to the CSV file containing the disaggregated ICIO data
    ICIO_path = path_1 + '/Y_sc_ICIO_agg.csv'

    # Read the disaggregated data into a DataFrame
    Y_disag = pd.read_csv(ICIO_path)

    # Set multi-index for the disaggregated data based on country and sector
    Y_disag = Y_disag.set_index(['country', 'sector'])

    # Extract data related to the EU's infrastructure and construction sectors
    Y_EU_subcons = Y_disag.loc[pd.IndexSlice['EU',['Buildings','Electricity infrastructure',
                                                'Other civil engineering','Railways','Roads']],:]
    
    # Sum the values of the EU sub-sectors
    Y_EU_con = Y_EU_subcons.sum(0)

    # Calculate the ratio of each sub-sector to the total EU construction
    Y_EU_subcons_ratio = Y_EU_subcons / Y_EU_con

    # Get the 'construction' row for the 'EU' from the original dataset Y
    construction = Y.loc[pd.IndexSlice['EU', 'Construction'], :]

    # Drop the 'EU' and 'Construction' rows from Y, as they will be reallocated
    Y = Y.drop([('EU', 'Construction')])

    # Iterate over the rows in Y_EU_subcons_ratio to apply the construction ratios
    for i in range(len(Y_EU_subcons_ratio.index)):
        # Multiply the row by the 'construction' row to allocate the sub-sector data
        Y_EU_subcons_ratio.iloc[i] = Y_EU_subcons_ratio.iloc[i] * construction

    # Append the adjusted EU sub-sector data back into Y
    Y = pd.concat([Y, Y_EU_subcons_ratio], axis=0)

    # Set appropriate names for the index levels ('Country' and 'Sector')
    Y.index.names = ['Country', 'Sector']

    # Sort the DataFrame by 'Country' and 'Sector'
    Y = Y.sort_index(level=['Country', 'Sector'])
    
    # Return the updated DataFrame
    return Y
