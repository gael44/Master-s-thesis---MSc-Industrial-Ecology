# group EU countries

"""
    Computes the modified matrix Y_modif_s_s based on input Y, EU countries, and sectors. This modified Y 
    is to be used when CE policies are implemented on the Y matrix's specific final demand categories.

    Parameters:
    Y (pd.DataFrame): Input DataFrame Y.
    EU_countries (list): List of EU countries for aggregation.
    sectors (list): List of sectors for multi-indexing.

    Returns:
    pd.DataFrame: Modified matrix Y_modif_s_s.
    """
    ## Y per country and final demand sector, aggregated for EU countries 
    ## aggregation columns
    
import pandas as pd
import numpy as np

def compute_Y_EU_single (Y, EU_countries):
    """
    Function to compute a modified matrix Y for EU countries by aggregating sectors and final demand categories.
    """
    # Extract unique sectors from the index of the DataFrame
    sectors = Y.index.get_level_values(1).unique()

    # Select data for the EU countries
    Y_eu_s = Y.loc[:, EU_countries]

    results = []
    for i in range(7):  # Loop over 7 sectors
        # Sum the columns for each sector across all rows (i.e., summing along axis 1)
        sector = np.sum(Y_eu_s.iloc[:, i + 7 * np.arange(27)], axis=1)
        results.append(sector)
    # Convert results into a DataFrame
    Y_eu_s = pd.DataFrame(results).T

    # Define the final demand categories to be included in the aggregation
    final_demand_categories = [
        'Final consumption expenditure by households', 
        'Final consumption expenditure by non-profit organisations serving households (NPISH)', 
        'Final consumption expenditure by government', 
        'Gross fixed capital formation', 
        'Changes in inventories', 
        'Changes in valuables', 
        'Exports: Total (fob)'
    ]
    # Create a multi-index for the final demand categories
    multi_index_c_fd = pd.MultiIndex.from_product([['EU'], final_demand_categories], names=['Region', 'Final Demand Category'])
    
    # Assign the multi-index to the columns of the DataFrame
    Y_eu_s.columns = multi_index_c_fd

    # Drop EU countries from the original DataFrame
    Y_wt_eu = Y.drop(columns=EU_countries)
    # Concatenate the modified EU data with the rest of the data
    Y_modif = pd.concat([Y_wt_eu, Y_eu_s], axis=1)
    Y_modif.index = Y_modif.index.set_names(['region', 'category'])
    Y_modif.columns = Y_modif.columns.set_names(['region', 'category'])

    ## aggregation rows
    # Select the EU countries data for further aggregation
    Y_eu_s = Y_modif.loc[EU_countries, :]

    results = []
    # Loop through each sector and aggregate the data by summing along the rows
    for i in range(163):
        sector = np.sum(Y_eu_s.iloc[i + 163 * np.arange(27), :], axis=0)
        results.append(sector)
    Y_eu_s = pd.DataFrame(results)

    # Create a multi-index for sectors in the EU aggregation
    multi_index_cs = pd.MultiIndex.from_product([['EU'], sectors])
    Y_eu_s.index = multi_index_cs

    # Drop the EU countries data from the modified DataFrame
    Y_wt_eu = Y_modif.drop(index=EU_countries)

    # Concatenate the aggregated EU data with the rest of the data
    Y_modif = pd.concat([Y_wt_eu ,Y_eu_s], axis=0)
    
    # Set the column and index names
    Y_modif.columns.names = ['region','category']
    Y_modif.index.names = ['region','category']

    # Return the modified DataFrame
    return Y_modif
