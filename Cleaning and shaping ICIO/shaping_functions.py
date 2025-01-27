import pandas as pd

## A_modif

def compute_modified_matrix(Z, sectors, EU_countries):
    """
    Computes the modified matrix A_modif based on input A, sectors, and EU countries.

    Parameters:
    A (pd.DataFrame): Input DataFrame A.
    sectors (list): List of sectors for multi-indexing.
    EU_countries (list): List of EU countries for aggregation.

    Returns:
    pd.DataFrame: Modified matrix A_modif.
    """
    ## aggregation Eu columns
    Z_eu = Z.loc[:, EU_countries]
    results = []
    for i in range(0, 49): 
        sector = 0  
        for j in range(0, 27):  
            sector += Z_eu.iloc[:, i + 27 * j]  # Summing columns for each sector
        results.append(sector)
    Z_eu = pd.DataFrame(results).T  # Transpose to align the shape
    multi_index_cs = pd.MultiIndex.from_product([['EU'], sectors])  # Create multi-index for EU
    Z_eu.columns = multi_index_cs

    Z_modif = pd.concat([Z.T.drop(index=EU_countries).T, Z_eu], axis=1)  # Concatenate modified EU columns
    
    ## aggregation rows
    Z_eu = Z_modif.loc[EU_countries, :]
    results = []
    for i in range(0, 49): 
        sector = 0  
        for j in range(0, 27):  
            sector += Z_eu.iloc[i + 27 * j, :]  # Summing rows for each sector
        results.append(sector)
    Z_eu = pd.DataFrame(results)
    Z_eu.index = multi_index_cs  # Set index for EU sectors

    Z_modif = pd.concat([Z_modif.drop(index=EU_countries), Z_eu], axis=0)  # Concatenate modified EU rows
    Z_modif.columns.names = ['country', 'sector']  # Set column names
    Z_modif.index.names = ['country', 'sector']  # Set index names
    return Z_modif

## Y_modif_s_c

def compute_modified_Y_s_c(Y, EU_countries, sectors):
    """
    Computes the modified matrix Y_modif_s_c based on input Y, EU countries, and sectors. This modified Y is to be used when CE policies are implemented
    on the A matrix.

    Parameters:
    Y (pd.DataFrame): Input DataFrame Y.
    EU_countries (list): List of EU countries for aggregation.
    sectors (list): List of sectors for multi-indexing.

    Returns:
    pd.DataFrame: Modified matrix Y_modif_s_c.
    """
    ## Y per country, aggregated for EU countries
    ## aggregation columns
    Y_c = Y.T.groupby('country').sum().T  # Summing Y values by country
    Y_eu = Y_c.loc[:, EU_countries].sum(1)  # Aggregating EU countries' columns
    Y_c = pd.concat([Y_c.drop(columns=EU_countries), Y_eu], axis=1)  # Concatenating EU aggregated values
    Y_c.columns.values[40] = 'EU'  # Assuming there are at least 41 columns for EU aggregation
    Y_c.shape

    ## aggregation rows
    Y_c_modif = Y_c.loc[EU_countries, :]
    results = []
    for i in range(0, 49): 
        sector = 0  
        for j in range(0, 27):  
            sector += Y_c_modif.iloc[i + 27 * j, :]  # Summing rows for each sector
        results.append(sector)
    Y_c_modif = pd.DataFrame(results)
    multi_index_cs = pd.MultiIndex.from_product([['EU'], sectors])  # Creating multi-index for EU sectors
    Y_c_modif.index = multi_index_cs
    
    Y_modif_s_c = pd.concat([Y_c.drop(index=EU_countries), Y_c_modif], axis=0)  # Concatenating modified EU rows
    Y_modif_s_c.columns.names = ['country']  # Setting column names
    Y_modif_s_c.index.names = ['country', 'sector']  # Setting index names
    return Y_modif_s_c


## Y_modif_s_s

def compute_modified_Y_s_s(Y, EU_countries, sectors):
    """
    Computes the modified matrix Y_modif_s_s based on input Y, EU countries, and sectors. This modified Y is to be used when CE policies are implemented
    on the Y matrix's specific final demand categories.

    Parameters:
    Y (pd.DataFrame): Input DataFrame Y.
    EU_countries (list): List of EU countries for aggregation.
    sectors (list): List of sectors for multi-indexing.

    Returns:
    pd.DataFrame: Modified matrix Y_modif_s_s.
    """
    ## Y per country and final demand sector, aggregated for EU countries 
    ## aggregation columns
    Y_eu_s = Y.loc[:, EU_countries]
    results = []
    for i in range(0, 6): 
        sector = 0  
        for j in range(0, 27):  
            sector += Y_eu_s.iloc[:, i + 6 * j]  # Summing final demand sectors for EU countries
        results.append(sector)  # This needs to be inside the outer loop
    Y_eu_s = pd.DataFrame(results).T

    multi_index_c_fd = pd.MultiIndex.from_tuples([  # Multi-index for final demand sectors
        ('EU', 'HFCE'), 
        ('EU', 'NPISH'), 
        ('EU', 'GGFC'), 
        ('EU', 'GFCF'), 
        ('EU', 'INVNT'), 
        ('EU', 'DPABR')
    ])
    Y_eu_s.columns = multi_index_c_fd
    Y_c_s_modif = pd.concat([Y.T.drop(index=EU_countries).T, Y_eu_s], axis=1)

    ## aggregation rows
    Y_eu_s = Y_c_s_modif.loc[EU_countries, :]
    results = []
    for i in range(0, 49): 
        sector = 0  
        for j in range(0, 27):  
            sector += Y_eu_s.iloc[i + 27 * j, :]  # Summing rows for each sector
        results.append(sector)  # This needs to be inside the outer loop
    Y_eu_s = pd.DataFrame(results)

    multi_index_cs = pd.MultiIndex.from_product([['EU'], sectors])  # Creating multi-index for EU sectors
    Y_eu_s.index = multi_index_cs
    Y_modif_s_s = pd.concat([Y_c_s_modif.drop(index=EU_countries), Y_eu_s], axis=0)  # Concatenating EU rows
    Y_modif_s_s.columns.names = ['country', 'final demand']  # Setting column names
    Y_modif_s_s.index.names = ['country', 'sector']  # Setting index names
    return Y_modif_s_s


## F_modif

def compute_modified_F(F, EU_countries, sectors):
    """
    Computes the modified matrix F_modif based on input F, EU countries, and sectors.

    Parameters:
    F (pd.DataFrame): Input DataFrame F.
    EU_countries (list): List of EU countries for aggregation.
    sectors (list): List of sectors for multi-indexing.

    Returns:
    pd.DataFrame: Modified matrix F_modif.
    """
    F_eu = F.loc[:, EU_countries]
    results = []
    for i in range(0, 49): 
        sector = 0  
        for j in range(0, 27):  
            sector += F_eu.iloc[:, i + 27 * j]  # Summing columns for each sector
        results.append(sector)
    
    F_eu = pd.DataFrame(results).T
    multi_index_cs = pd.MultiIndex.from_product([['EU'], sectors])  # Multi-index for EU sectors
    F_eu.columns = multi_index_cs
    F_modif = pd.concat([F.T.drop(index=EU_countries).T, F_eu], axis=1)  # Concatenating EU columns
    F_modif.columns.names = ['country', 'sector']  # Setting column names
    return F_modif

##  general shaping function
def compute_EU_shaped_matrix(Z, Y, F, EU_countries, sectors):
    Z = Z.astype(float)  # Convert Z to float type
    Y = Y.astype(float)  # Convert Y to float type
    F = F.astype(float)  # Convert F to float type
    Z_modif = compute_modified_matrix(Z, sectors, EU_countries)  # Compute modified A matrix
    Y_modif_s_c = compute_modified_Y_s_c(Y, EU_countries, sectors)  # Compute modified Y for supply chains
    Y_modif_s_s = compute_modified_Y_s_s(Y, EU_countries, sectors)  # Compute modified Y for specific final demand
    F_modif = compute_modified_F(F, EU_countries, sectors)  # Compute modified F matrix
    return(Z_modif, Y_modif_s_c, Y_modif_s_s, F_modif)  # Return all modified matrices
