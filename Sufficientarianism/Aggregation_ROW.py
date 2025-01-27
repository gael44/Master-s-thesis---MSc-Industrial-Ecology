# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 14:39:38 2024

@author: user
"""
import pandas as pd

def aggregation_row_function(Y):
    # The correspondence matrix includes 5 different ROW regions in the ICIO.
    # This function aggregates the data across these ROW regions to match the dimensions of the other matrix.

    ## Row aggregation
    # Define the regions to be aggregated (ROW1, ROW2, ROW3, ROW4, ROW5)
    row = ['ROW1','ROW2','ROW3','ROW4','ROW5']

    # Extract the data for the ROW regions
    ROW = Y.loc[pd.IndexSlice[row,:],:]
    
    # Get the unique sector labels from the second level of the MultiIndex
    sec_label = ROW.index.get_level_values(1).unique()
    
    result = []  # List to store the aggregated sector data
    
    # Loop through each sector and aggregate the data for each sector across the ROW regions
    for sector in sec_label:
        # Filter data for the current sector across ROW regions and sum across the first level (ROW1-ROW5)
        sector_data = ROW.loc[(slice(None), sector), :].sum()  
        result.append(sector_data)  # Add the aggregated data to the result list
    
    # Create a new DataFrame with the aggregated data, using a MultiIndex for the rows (ROW, sector)
    result = pd.DataFrame(result, index=pd.MultiIndex.from_tuples([('ROW', sector) for sector in sec_label], names=['Region', 'Sector']))
    
    # Drop the original ROW regions from the DataFrame
    Y = Y.drop(row, level=0)

    # Concatenate the aggregated ROW data back to the DataFrame
    Y = pd.concat([Y, result], axis=0)

    ## Column aggregation
    # Sum the values across the ROW regions for each column and assign the result to a new 'ROW' column
    Y['ROW'] = Y.loc[:,row].sum(1)
    
    # Drop the original ROW region columns
    Y = Y.drop(columns=row)
    
    return Y  # Return the updated DataFrame
