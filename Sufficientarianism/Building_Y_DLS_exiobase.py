# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 12:27:28 2024

@author: user
"""
import pandas as pd
import numpy as np

# Function to compute population and group countries into different categories (EU, WA, WL, etc.)
def compute_population(path_pop, path_country_label_match):
    
    # Define lists of countries belonging to different regions or groups
    non_eu_countries = [
        "United Kingdom", "United States of America", "Japan", "China", "Canada", 
        "Republic of Korea", "Brazil", "India", "Mexico", "Russian Federation", "Australia", "Switzerland", 
        "Türkiye", "China, Taiwan Province of China", "Norway", "Indonesia", "South Africa", "Bermuda"
    ]

    eu_countries = [
            "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", 
            "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", 
            "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", 
            "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Saint Pierre and Miquelon", "Greenland",
            "Slovenia", "Spain", "Sweden"
        ]
        

    WA = [
        "Burundi", "Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya", "Madagascar", "Malawi", "Mauritius",
        "Mayotte", "Mozambique", "Réunion", "Rwanda", "Seychelles", "Somalia", "South Sudan", "Uganda",
        "United Republic of Tanzania", "Zambia", "Zimbabwe", "Angola", "Cameroon", "Central African Republic",
        "Chad", "Congo", "Democratic Republic of the Congo", "Equatorial Guinea", "Gabon", "Sao Tome and Principe",
        "Algeria", "Egypt", "Libya", "Morocco", "Sudan", "Tunisia", "Western Sahara", "Botswana", "Eswatini",
        "Lesotho", "Namibia", "Benin", "Burkina Faso", "Cabo Verde", "Côte d'Ivoire", "Gambia", "Ghana",
        "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Saint Helena",
        "Senegal", "Sierra Leone", "Togo"
    ]

    # Continue defining other regions (WL, WE, WF, WM) similarly...

    # Read population data and filter for 2021 data
    data_pop = pd.read_csv(path_pop)
    pop = data_pop.loc[(data_pop['Time'] == 2021) & (data_pop['ISO3_code'].notna()), ['TPopulation1Jan', 'Location', 'ISO3_code']]
    pop['TPopulation1Jan'] *= 1000  # Convert population to the full number

    # Classify countries into groups (EU, WA, etc.) based on their location
    pop['correspondence'] = pop['Location'].apply(
            lambda x: 'EU' if x in eu_countries else (
                'WA' if x in WA else (
                    'WL' if x in WL else (
                        'WE' if x in WE else (
                            'WF' if x in WF else (
                                'WM' if x in WM else x
                            )
                        )
                    )
                )
            )
        )

    # Handle changes in naming conventions for specific countries
    change = {
        'Czechia': 'Czech Republic',
        'Republic of Korea': 'South Korea',
        'Russian Federation': 'Russia',
        'Türkiye': 'Turkey',
        'Saint Pierre and Miquelon': 'EU',
        'Greenland': 'EU',
        'Bermuda': 'United Kingdom',
        'China, Taiwan Province of China': 'Taiwan'
    }

    pop['correspondence'] = pop['correspondence'].replace(change)

    # Group population data by the 'correspondence' region and sum the populations
    pop = pop.groupby('correspondence').sum().reset_index().drop(columns=['Location','ISO3_code'])

    # Load country label matching data
    match = pd.read_excel(path_country_label_match, header = [0])
    match = match.set_index('Key')['value'].to_dict()

    # Apply the country label matching
    pop['correspondence'] = pop['correspondence'].replace(match)
    pop = pop.set_index('correspondence')
    pop.index.name = 'countries'

    return pop

# Function to build the Y matrix and apply DLS (Domestic Linkage Supply) adjustments
def building_Y_DLS_exiobase(Y_EU_single,path_DLS, path_pop, path_country_label_match):
    
    # Initialize Y_Exiobase from Y_EU_single
    Y_Exiobase = Y_EU_single
    Y_Exiobase = Y_Exiobase.T.groupby('region').sum().T

    # Load the DLS data from an Excel sheet
    DLS = pd.read_excel(
        path_DLS, 
        sheet_name='DLS-Exiobase', 
        usecols=['Values', 'Exiobase sector'], 
        header=1
    )

    DLS = DLS.set_index(['Exiobase sector'])
    DLS = DLS.groupby('Exiobase sector').sum()  # Aggregate DLS data by sector

    # Get the unique sectors from Y_Exiobase
    sector = Y_Exiobase.index.get_level_values(1).unique()

    # Calculate global supply for each sector
    global_supply = []
    for i in range(163):
        total_sect = np.sum(Y_Exiobase.iloc[i + 163*np.arange(23), :], axis = 0)
        global_supply.append(total_sect)

    global_supply = pd.DataFrame(global_supply, index=sector)

    # Calculate the ratio of supply
    global_supply_repeated = np.tile(global_supply.values, (23, 1))
    ratio_supply = Y_Exiobase / global_supply_repeated
    ratio_supply = pd.DataFrame(ratio_supply, index=Y_Exiobase.index, columns=Y_Exiobase.columns)
    ratio_supply = ratio_supply.fillna(0)  # Fill missing values

    # Initialize supply for DLS and apply the DLS adjustment for matching sectors
    global_supply_DLS = pd.DataFrame(np.zeros_like(global_supply), index=sector, columns=Y_Exiobase.columns)
    matching_sectors = global_supply_DLS.index.intersection(DLS.index)
    global_supply_DLS.loc[matching_sectors, :] = DLS.loc[matching_sectors].values

    # Apply DLS adjustment and create the new Y_DLS_exiobase matrix
    global_supply_DLS_expanded = np.repeat(global_supply_DLS.values[None, :, :], 23, axis=0).reshape(-1, global_supply_DLS.shape[1])
    Y_DLS_exiobase = ratio_supply.values * global_supply_DLS_expanded
    Y_DLS_exiobase = pd.DataFrame(Y_DLS_exiobase, index=Y_Exiobase.index, columns=Y_Exiobase.columns)

    # Scale the data based on the population of each country
    pop = compute_population(path_pop, path_country_label_match)
    pop = pop.sort_index()
    Y_DLS_exiobase = Y_DLS_exiobase.sort_index(level=0, sort_remaining=False)
    Y_DLS_exiobase = Y_DLS_exiobase.reindex(sorted(Y_DLS_exiobase.columns), axis=1)
    country_lab = Y_DLS_exiobase.index.get_level_values(0).unique()
    pop = np.diag(pop.values.flatten())
    Y_DLS_exiobase = Y_DLS_exiobase @ pop  # Apply population scaling
    Y_DLS_exiobase.columns = country_lab  # Update column names

    return Y_DLS_exiobase, pop  # Return the final adjusted matrix and population data
