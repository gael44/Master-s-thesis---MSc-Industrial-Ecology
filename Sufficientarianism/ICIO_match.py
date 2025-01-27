# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 16:59:31 2024

@author: user
"""

# Import necessary libraries
import pandas as pd
from disaggregation_construction import disaggregation_cons
from Aggregation_ROW import aggregation_row_function

def ICIO_match(Y, path_correspondence):
    """
    Matches Exiobase data to ICIO data and performs necessary scaling and aggregation.

    Parameters:
    Y : DataFrame - Exiobase data to be matched to ICIO data.
    path_correspondence : str - Path to the Excel file containing correspondence data for country and sector mapping.

    Returns:
    Y_disag : DataFrame - Final matched and disaggregated data.
    """

    # Load sector and country matching sheets from the Excel file
    sec_matching = pd.read_excel(path_correspondence, sheet_name='Sectors', usecols=['ICIO description', 'Exiobase','ratio'])
    country_matching = pd.read_excel(path_correspondence, sheet_name='Regions', usecols=['ICIO', 'Exiobase', 'Population ratio'])

    #%% Country matching - rows
    Y = Y.reset_index()
    # Step 1: Create the 'ICIO_country' column with lists of two elements (ICIO, Population ratio) based on Exiobase country matching
    Y['ICIO_country'] = Y['region'].apply(lambda country: 
                                           country_matching.loc[country_matching['Exiobase'] == country, 
                                                                ['ICIO', 'Population ratio']].apply(lambda row: row.tolist(), axis=1).tolist())

    # Step 2: Explode the 'ICIO_country' column to split the lists into individual rows
    Y = Y.explode('ICIO_country')

    # Step 3: Expand the lists in the 'ICIO_country' column into two separate columns for ICIO and Population ratio
    Y[['ICIO', 'Population ratio']] = pd.DataFrame(Y['ICIO_country'].to_list(), index=Y.index)

    # Step 4: Clean up the 'ICIO_country' column, as it's no longer needed
    Y = Y.drop(columns=['ICIO_country','region'])

    # Step 5: Scale the rows by their population ratio
    Y = Y.set_index(['ICIO', 'category'])
    Y = Y.apply(lambda row: row * row['Population ratio'], axis=1).drop(columns=['Population ratio'])
    Y = Y.sort_values(by='ICIO').reset_index()

    #%% Error measurement introduced by the row country matching
    # This section is currently commented out, but it would compare the adjusted data against a baseline to measure errors.

    #%% Country matching - columns
    # Save the index labels for future use, as they need to be deleted for the columns' transformation
    Y_index = Y.loc[:,('ICIO', 'category')]
    Y = Y.drop(columns=['ICIO', 'category'])

    # Transpose the data for column-wise transformation
    Y = Y.T  # Transpose the DataFrame

    # Step 1: Create the 'ICIO_country' column again, similar to the previous section, but now for columns
    Y.reset_index(inplace=True)  # Convert the index to a column
    Y['ICIO_country'] = Y['region'].apply(lambda country: 
                                           country_matching.loc[country_matching['Exiobase'] == country, 
                                                                ['ICIO', 'Population ratio']].apply(lambda row: row.tolist(), axis=1).tolist())

    # Step 2: Explode the 'ICIO_country' column to split the lists into individual rows
    Y = Y.explode('ICIO_country')

    # Step 3: Expand the lists in the 'ICIO_country' column into two separate columns for ICIO and Population ratio
    Y[['ICIO', 'Population ratio']] = pd.DataFrame(Y['ICIO_country'].to_list(), index=Y.index)

    # Step 4: Clean up the 'ICIO_country' column, as it's no longer needed
    Y = Y.drop(columns=['ICIO_country','region'])

    # Step 5: Scale the rows by their population ratio
    Y = Y.set_index(['ICIO']) # Set the ICIO as the index
    Y = Y.apply(lambda row: row * row['Population ratio'], axis=1).drop(columns=['Population ratio'])
    Y = Y.sort_values(by='ICIO')  # Sort by ICIO

    # Transpose the data back to its original structure
    Y = Y.T

    # Reattach the previously saved index labels
    Y.index = pd.MultiIndex.from_frame(Y_index)

    # Note: The values for Hong Kong are 0 because of the surface area sharing method (Hong Kong has a small surface area)

    #%% Sector matching
    # Step 1: Assign a new column with the ICIO ratio and sectors matching each Exiobase sector
    Y = Y.reset_index()
    Y['ICIO_sector'] = Y['category'].apply(lambda sector: 
                                         sec_matching.loc[sec_matching['Exiobase'] == sector, ['ICIO description', 'ratio']].apply(lambda row: row.tolist(), axis=1).tolist())

    # Step 2: Create a line for each ICIO sector matched to an Exiobase sector
    Y = Y.explode('ICIO_sector').reset_index(drop=True)

    # Step 3: Create 2 columns: one for the ICIO sector, and the other for its ratio
    Y[['ICIO_s', 'ratio']] = pd.DataFrame(Y['ICIO_sector'].to_list(), index=Y.index)

    # Step 4: Clean up the 'ICIO_sector' column, as it's no longer needed
    Y = Y.drop(columns=['ICIO_sector','category'])

    # Step 5: Scale the ICIO sectors' values with their ratio and corresponding Exiobase sector
    Y = Y.set_index(['ICIO','ICIO_s']) # Set the ICIO and ICIO sector as the index
    Y = Y.apply(lambda row: row * row['ratio'], axis=1).drop(columns=['ratio'])

    # Step 6: Aggregate the ICIO sectors
    Y = Y.groupby(['ICIO', 'ICIO_s']).sum()

    #%% Aggregation and disaggregation
    # Perform aggregation and disaggregation on the data
    Y_agg = aggregation_row_function(Y)
    Y_disag = disaggregation_cons(Y_agg)

    # Return the final disaggregated data
    return Y_disag
