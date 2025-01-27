import pandas as pd
import numpy as np

def cleaning_IOT_function(Z, Y, F):
    """
    Cleans and formats the input IOT matrices Z, Y, and F by replacing infinities with NaN, 
    reshaping labels, and harmonizing sector names.

    Parameters:
    Z (pd.DataFrame): The input matrix for Z.
    Y (pd.DataFrame): The input matrix for Y.
    F (pd.DataFrame): The input matrix for F.

    Returns:
    pd.DataFrame, pd.DataFrame, pd.DataFrame: Cleaned and formatted Z, Y, and F matrices.
    """
    
    # Replace infinities with NaN and NaN with 0
    Z.replace([np.inf, -np.inf], np.nan, inplace=True)
    Z.replace(np.nan, 0, inplace=True)
    Y.replace([np.inf, -np.inf], np.nan, inplace=True)
    Y.replace(np.nan, 0, inplace=True)
    F.replace([np.inf, -np.inf], np.nan, inplace=True)
    F.replace(np.nan, 0, inplace=True)
    
    ## Formatting Z labels
    ## Extracting sector labels
    Z_labels = Z.iloc[:, 0:3]
    Z = Z.drop(columns=['region', 'Unnamed: 1', 'Unnamed: 2'])
    Z = Z.drop(index=[0, 1, 2])
    Z_labels = Z_labels.drop(index=[0, 1, 2])
    Z_labels.columns = ['country', 'sector', 'subsector']
    Z_labels['order'] = range(1, len(Z_labels) + 1)
    
    ## Reshape the labels
    Z_labels['new_sector'] = np.where(Z_labels['subsector'] == 'Total', Z_labels['sector'], Z_labels['subsector'])
    Z_labels = Z_labels.drop(columns=['sector', 'subsector']) 
    Z_labels.columns = ['country', 'order', 'sector']
    Z_labels = Z_labels.drop(columns=['order'])
    Z_labels = pd.MultiIndex.from_frame(Z_labels)

    ## Attaching formatted labels to Z
    Z.columns = Z_labels
    Z.index = Z_labels

    ## Y Formatting labels
    Y_labels = Y.iloc[:, 0:3]
    Y = Y.drop(columns=['region', 'Unnamed: 1_level_0', 'Unnamed: 2_level_0'])
    Y_labels_col = Y.columns.to_frame().reset_index()
    Y_labels_col = Y_labels_col.drop(columns=['level_0', 'level_1', 1])
    Y_labels_col.columns.name = 'country'

    Y_labels.columns = ['country', 'sector', 'subsector']
    Y_labels['order'] = range(1, len(Y_labels) + 1)

    ## Reshape the labels
    Y_labels['new_sector'] = np.where(Y_labels['subsector'] == 'Total', Y_labels['sector'], Y_labels['subsector'])
    Y_labels = Y_labels.drop(columns=['sector', 'subsector']) 
    Y_labels.columns = ['country', 'order', 'sector']
    Y_labels = Y_labels.drop(columns=['order'])
    Y_labels = pd.MultiIndex.from_frame(Y_labels)
    Y.index = Y_labels

    final_demand_sector = ['HFCE', 'NPISH', 'GGFC', 'GFCF', 'INVNT', 'DPABR']
    final_demand_sector = final_demand_sector * 67
    final_demand_sector = pd.DataFrame(final_demand_sector).T
    countries = Y_labels_col.loc[:, 0]
    countries = pd.DataFrame(countries).T
    Y_columns = pd.concat([countries, final_demand_sector], axis=0)

    # Create a MultiIndex with 'Country' and 'Sector' as the names
    Y_columns = pd.MultiIndex.from_frame(Y_columns.T, names=['country', 'sector'])
    Y.columns = Y_columns

    ## F formatting labels
    F = F.set_index(F.columns[0])
    F = F.rename_axis('Pressure')
    F.columns = Z_labels
    F = F.drop(index=['sector', 'subsector'])

    # Harmonizing labels
    def transform_multiindex(df, code="both"):
        """
        Transforms specific strings in the MultiIndex of rows, columns, or both 
        based on predefined pairs.

        Parameters:
        df (pd.DataFrame): Input DataFrame with MultiIndex rows/columns to be transformed.
        code (str): Specifies whether to transform the row index, column index, or both.
                    Options: "rows", "columns", "both".

        Returns:
        pd.DataFrame: DataFrame with transformed MultiIndex.
        """
        # Define the replacement pairs
        replacements = {
            'Activities of households as employers; undifferentiated goods- and services- services-producing activities of households for own use': 'Activities of households as employers',
            'Machinery and equipment, nec': 'Machinery and equipment',
            'Manufacturing nec; repair and installation of machinery and equipment ': 'Manufacturing nec; repair and installation of machinery and equipment'
        }

        # Helper function to transform MultiIndex levels
        def transform_index(index):
            # Transform each level in the MultiIndex
            transformed_levels = [index.get_level_values(i).to_series().replace(replacements).values for i in range(index.nlevels)]
            return pd.MultiIndex.from_arrays(transformed_levels, names=index.names)

        # Transform based on the specified code
        if code == "rows":
            df.index = transform_index(df.index)
        elif code == "columns":
            df.columns = transform_index(df.columns)
        elif code == "both":
            df.index = transform_index(df.index)
            df.columns = transform_index(df.columns)

        return df

    Z = transform_multiindex(Z, 'both')
    Y = transform_multiindex(Y, 'rows')
    F = transform_multiindex(F, 'columns')

    return Z, Y, F
