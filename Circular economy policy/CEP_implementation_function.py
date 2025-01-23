import pandas as pd
import numpy as np

def Ceteris_Paribus_shocks(Full_shocks_A, Full_shocks_Y, A, Y_s_c, Y_s_s, f, L, I, impact_indicator, ancilliary ='yes'):
    """
    Function to apply shocks to matrices A and Y and calculate the corresponding footprints.
    
    Arguments:
    - Full_shocks_A, Full_shocks_Y: DataFrames containing the shocks for A and Y.
    - A, Y_s_c, Y_s_s, f, L, I: Matrices for economic analysis.
    - impact_indicator: The impact indicator for the calculation.
    -
    Returns:
    - CEP_ftp_results: Dictionary containing footprint values for each shock applied to A and Y.
    """
    
    CEP_ftp_results = {}
    
    
        
    
    if ancilliary == 'yes': 
        None
    elif ancilliary == 'no':
        Full_shocks_A = Full_shocks_A[Full_shocks_A['type intervention'] == 'primary']
        
    # Apply shocks to A
    group_pol = Full_shocks_A['policy group'].unique()
    group_pol_dict = {f'group_pol_{i}': Full_shocks_A.loc[Full_shocks_A['policy group'] == i] for i in group_pol}
    
    
    
    for group_key, pol in group_pol_dict.items():  # Loop through the dictionary
        A_modif = A.copy()  # Create a copy of A to apply shocks without modifying the original
        A_modif.index = pd.MultiIndex.from_tuples(
            [
                ('EU', 'Construction') if (level0 == 'EU' and level1 == 'Buildings') else (level0, level1)
                for level0, level1 in A_modif.index
            ],
            names=['country', 'sector']
        )
        A_modif.columns = pd.MultiIndex.from_tuples(
            [
                ('EU', 'Construction') if (level0 == 'EU' and level1 == 'Buildings') else (level0, level1)
                for level0, level1 in A_modif.index
            ],
            names=['country', 'sector']
        )
        for _, row in pol.iterrows():  # Iterate through each row in `pol`
            #position
                if row['row region']  == "All countries":
                    country_row = A_modif.columns.get_level_values(0).unique()
                else:
                    country_row = row['row region']
                
                sector_row = row['row sector']
                    
                country_col = 'EU'
                if row['column sector']  == "All industries":
                    sector_col = A_modif.columns.get_level_values(1).unique()
                else:
                    sector_col = row['column sector']
                    
            # value
                value = row['value']
                mp = row['Market penetration']
                
                
                if row['name'] == ' Increase in demand for office machineries and equipment due to higher wear and tear. ':
                            # Iterate through the countries and sectors
                    for cr in country_row:
                        for sc in sector_col:
                            selected_value = A_modif.loc[(cr, 'Construction'), (country_col, sc)]
                            if selected_value == 0:  # Skip modification if the value is 0
                                continue
                            else:
                                A_modif.loc[(cr, sector_row), (country_col, sc)] *= (1 + value * mp)

                else:    # Apply percentage or absolute changes
                    A_modif.loc[(country_row, sector_row), (country_col, sector_col)] *= (1 + value * mp)
        
        A_modif.index = pd.MultiIndex.from_tuples(
            [
                ('EU', 'Buildings') if (level0 == 'EU' and level1 == 'Construction') else (level0, level1)
                for level0, level1 in A_modif.index
            ],
            names=['country', 'sector']
        )
        A_modif.columns = pd.MultiIndex.from_tuples(
            [
                ('EU', 'Buildings') if (level0 == 'EU' and level1 == 'Construction') else (level0, level1)
                for level0, level1 in A_modif.index
            ],
            names=['country', 'sector']
        )
        
        # Calculate the modified Leontief inverse
        L_modif = np.linalg.inv(I - A_modif)
    
        footprint_A = f.values@ L_modif @ Y_s_c
        footprint_A = footprint_A * 1e6  # Convert to kilotons
        footprint_A = pd.DataFrame(footprint_A)
        
        # Store the footprint in CEP_ftp_results using the group_key as the dictionary key
        CEP_ftp_results[group_key] = footprint_A





   
    # Apply shocks to Y
    if ancilliary == 'yes': 
        None
    elif ancilliary == 'no':
        Full_shocks_Y = Full_shocks_Y[Full_shocks_Y['type intervention'] == 'primary']
    
    group_pol = Full_shocks_Y['policy group'].unique()
    group_pol_dict = {f'group_pol_{i}': Full_shocks_Y.loc[Full_shocks_Y['policy group'] == i] for i in group_pol}

    for group_key, pol in group_pol_dict.items():
        Y_modif = Y_s_s.copy()  # Create a copy of A to apply shocks without modifying the original
        Y_modif.index = pd.MultiIndex.from_tuples(
            [
                ('EU', 'Construction') if (level0 == 'EU' and level1 == 'Buildings') else (level0, level1)
                for level0, level1 in Y_modif.index
            ],
            names=['country', 'sector']
        )
        # Iterate through each row in `pol` (filtered DataFrame)
        for _, row in pol.iterrows():
            if row['row region']  == "All countries":
                country_row = A_modif.columns.get_level_values(0).unique()
            else:
                country_row = row['row region']
            
            sector_row = row['row sector']
                
            country_col = 'EU'
            if row['demand category']  == "All industries":
                sector_col = A_modif.columns.get_level_values(1).unique()
            else:
                sector_col = row['demand category']
                
        # value
            value = row['value']
            mp = row['Market penetration']

            # Apply percentage or absolute changes
            Y_modif.loc[(country_row, sector_row), (country_col, sector_col)] *= (1 + value * mp)
        
        Y_modif.index = pd.MultiIndex.from_tuples(
            [
                ('EU', 'Buildings') if (level0 == 'EU' and level1 == 'Construction') else (level0, level1)
                for level0, level1 in Y_modif.index
            ],
            names=['country', 'sector']
        )
        # Calculate the footprint for modified Y using BAU Leontief inverse and intensity
        footprint_Y = f.values@ L @ Y_modif.T.groupby('country').sum().T
        footprint_Y = footprint_Y * 1e6  # Convert to kilotons
        footprint_Y = pd.DataFrame(footprint_Y)

        # Store the footprint in CEP_ftp_results using the group_key as the dictionary key
        CEP_ftp_results[group_key] = footprint_Y

    return CEP_ftp_results

#%%
def total_shocks(Full_shocks_A, Full_shocks_Y, A, Y_s_c, Y_s_s, f, L, I, impact_indicator, strat = 'CP', ancilliary = 'yes'):     
    A_modif = A.copy()  # Create a copy of A to apply shocks without modifying the original
    A_modif.index = pd.MultiIndex.from_tuples(
        [
            ('EU', 'Construction') if (level0 == 'EU' and level1 == 'Buildings') else (level0, level1)
            for level0, level1 in A_modif.index
        ],
        names=['country', 'sector']
    )
    A_modif.columns = pd.MultiIndex.from_tuples(
        [
            ('EU', 'Construction') if (level0 == 'EU' and level1 == 'Buildings') else (level0, level1)
            for level0, level1 in A_modif.index
        ],
        names=['country', 'sector']
    )
    
    
    if strat == 'RE':
        Full_shocks_A = Full_shocks_A[Full_shocks_A['strategy'] == 'RE']
    elif strat == 'PLE':
        Full_shocks_A = Full_shocks_A[Full_shocks_A['strategy'] == 'PLE']
    elif strat == 'Total':
        None
    
    
    if ancilliary == 'yes': 
        None
    elif ancilliary == 'no':
        Full_shocks_A = Full_shocks_A[Full_shocks_A['type intervention'] == 'primary']
        
    for _, row in Full_shocks_A.iterrows():
        
        
        #position
            if row['row region']  == "All countries":
                country_row = A_modif.columns.get_level_values(0).unique()
            else:
                country_row = row['row region']
            
            sector_row = row['row sector']
                
            country_col = 'EU'
            if row['column sector']  == "All industries":
                sector_col = A_modif.columns.get_level_values(1).unique()
            else:
                sector_col = row['column sector']
                
        # value
            value = row['value']
            mp = row['Market penetration']
            
            
            if row['name'] == ' Increase in demand for office machineries and equipment due to higher wear and tear. ':
                        # Iterate through the countries and sectors
                for cr in country_row:
                    for sc in sector_col:
                        selected_value = A_modif.loc[(cr, 'Construction'), (country_col, sc)]
                        if selected_value == 0:  # Skip modification if the value is 0
                            continue
                        else:
                            A_modif.loc[(cr, sector_row), (country_col, sc)] *= (1 + value * mp)

            else:    # Apply percentage or absolute changes
                A_modif.loc[(country_row, sector_row), (country_col, sector_col)] *= (1 + value * mp)
            
            
            
                
    A_modif.index = pd.MultiIndex.from_tuples(
        [
            ('EU', 'Buildings') if (level0 == 'EU' and level1 == 'Construction') else (level0, level1)
            for level0, level1 in A_modif.index
        ],
        names=['country', 'sector']
    )
    A_modif.columns = pd.MultiIndex.from_tuples(
        [
            ('EU', 'Buildings') if (level0 == 'EU' and level1 == 'Construction') else (level0, level1)
            for level0, level1 in A_modif.index
        ],
        names=['country', 'sector']
    )


          #%%          
                
    Y_modif = Y_s_s.copy()  # Create a copy of A to apply shocks without modifying the original
    Y_modif.index = pd.MultiIndex.from_tuples(
        [
            ('EU', 'Construction') if (level0 == 'EU' and level1 == 'Buildings') else (level0, level1)
            for level0, level1 in Y_modif.index
        ],
        names=['country', 'sector']
    )
    
    
    if strat == 'RE':
        Full_shocks_Y = Full_shocks_Y[Full_shocks_Y['strategy'] == 'RE']
    elif strat == 'PLE':
        Full_shocks_Y = Full_shocks_Y[Full_shocks_Y['strategy'] == 'PLE']
    elif strat == 'Total':
        None
        
    
    
    if ancilliary == 'yes': 
        None
    elif ancilliary == 'no':
        Full_shocks_Y = Full_shocks_Y[Full_shocks_Y['type intervention'] == 'primary']
        
    for _, row in Full_shocks_Y.iterrows():
        
        
        #position
            if row['row region']  == "All countries":
                country_row = A_modif.columns.get_level_values(0).unique()
            else:
                country_row = row['row region']
            
            sector_row = row['row sector']
                
            country_col = 'EU'
            if row['demand category']  == "All industries":
                sector_col = A_modif.columns.get_level_values(1).unique()
            else:
                sector_col = row['demand category']
                
        # value
            value = row['value']
            mp = row['Market penetration']

            # Apply percentage or absolute changes
            Y_modif.loc[(country_row, sector_row), (country_col, sector_col)] *= (1 + value * mp)
              
    Y_modif.index = pd.MultiIndex.from_tuples(
        [
            ('EU', 'Buildings') if (level0 == 'EU' and level1 == 'Construction') else (level0, level1)
            for level0, level1 in Y_modif.index
        ],
        names=['country', 'sector']
    )
    
    #%% CE scenario footprint
         # Identity matrix for calculating the Leontief inverse
    I = np.eye(A.shape[0])
        # Calculate the modified Leontief inverse after applying all shocks to A
    L_modif = np.linalg.inv(I - A_modif)
 
            # Calculate the new footprint after the total intervention (modifications on both A and Y)
    Y_modif_ = Y_modif.T.groupby('country').sum(1).T.values
    #%% Alternative output to analysis sectorial demand change
    #Y_modif_ = pd.DataFrame(Y_modif_)
    #Y_modif_.columns = Y_s_c.columns 
  
    #c = ['IND','KHM','LAO','MMR','ROW','VNM']
    #Y_test_w = Y_modif_.loc[:,c].sum(1)
    #Y_test_c = Y_modif_.loc[:,c]
    #CEP_ftp_w = np.diag(f.values.flatten())@ L_modif @ Y_test_w
    #CEP_ftp_w = CEP_ftp_w*1e6
    #CEP_ftp_w = pd.DataFrame(CEP_ftp_w)
    #CEP_ftp_w.columns = ['global']
    #CEP_ftp_w.index = A.index
    
    #CEP_ftp_c = np.diag(f.values.flatten())@ L_modif @ Y_test_c
    #CEP_ftp_c = CEP_ftp_c*1e6
    #CEP_ftp_c = pd.DataFrame(CEP_ftp_c)
    #CEP_ftp_c.columns = c
    #CEP_ftp_c.index = A.index
    #%% 
    
    CEP_ftp = f.values@ L_modif @ Y_modif_
    CEP_ftp = CEP_ftp*1e6
    CEP_ftp = pd.DataFrame(CEP_ftp)
    CEP_ftp.columns = A.index.get_level_values(0).unique()

    CEP_ftp.index = ["total CE"]
    return CEP_ftp
