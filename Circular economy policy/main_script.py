import os 
import pandas as pd
import numpy as np
# Get the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory

os.chdir(script_directory)
from CEP_implementation_function import Ceteris_Paribus_shocks
from CEP_implementation_function import total_shocks
# Get the script's directory

# Normalize and split the directory path
path_parts = script_directory.split(os.sep)

# Remove "step 4_ce ope" from the path parts if it exists

if "circular economy policy" in path_parts:
    path_parts.remove("circular economy policy")
    
    
    
# Reconstruct the script directory without "step 4_ce ope"
script_dir = os.sep.join(path_parts)

# Construct the path to "Step 3\Cleaning and shaping ICIO\cleant tables"
path_1 = os.path.join(script_dir, "Cleaning and shaping ICIO", "cleant tables")

# Ensure the path is in proper format
path_1 = os.path.abspath(path_1)

#%%
A = pd.read_csv(path_1 + '/A_ICIO.csv', sep=',', index_col= [0,1], header=[0, 1])
Y_s_s = pd.read_csv(path_1 + '/Y_ss_ICIO_agg.csv', sep=',', index_col= [0,1], header=[0, 1])
Y_s_c = pd.read_csv(path_1 + '/Y_sc_ICIO_agg.csv', sep=',', index_col= [0,1], header=[0])
F = pd.read_csv(path_1 + '/F_ICIO.csv', sep=',', index_col= [0], header=[0, 1])

#%%
## PART 3: Applying CEP to the modified matrix

path_CEP = script_directory + r'/all_shocks_substitution.xlsx'
path_pop = os.path.join(os.sep.join(path_parts), "Egalitarianism", "population.csv")

pop = pd.read_csv(path_pop, index_col = [0])


#%%
Full_shocks_A = pd.read_excel(path_CEP, sheet_name='A')
Full_shocks_Y = pd.read_excel(path_CEP, sheet_name='Y')

impact_indicator = pd.DataFrame(F.loc['GHG'], columns = ['GHG']).T
impact_indicator = impact_indicator

sensitivity = 1
I = np.eye(A.shape[0])  # Identity matrix for Leontief inverse
L = np.linalg.inv(I - A)  # BAU Leontief inverse
L = pd.DataFrame(L, index=A.index, columns=A.columns)
# Calculate the base (BAU) emission intensity
x_BAU = L @ (Y_s_s).sum(axis=1)
x_out = x_BAU.copy()
x_out[x_out != 0] = 1 / x_out[x_out != 0]
inv_diag_x_BAU = np.diag(x_out)
f = impact_indicator @ inv_diag_x_BAU  # Emission intensity
f.columns = F.columns

#%%

# manage the fact that some policies yields into several primary interventions.
ftp_CEP_TOT = total_shocks(
    Full_shocks_A, Full_shocks_Y, A, Y_s_c, Y_s_s, f, L, I, impact_indicator, ancilliary='yes')
ftp_CEP_TOT_cap = ftp_CEP_TOT/pop.values.squeeze()
ftp_CEP_TOT_cap.index = ['ftp_CEP_cap']

#%%
ftp_CEP_RE = total_shocks(
    Full_shocks_A, Full_shocks_Y, A, Y_s_c, Y_s_s, f, L, I, impact_indicator, strat = 'RE', ancilliary='yes'
)

ftp_CEP_RE.index = ['RE']
ftp_CEP_RE_cap = ftp_CEP_RE/pop.values.squeeze()
ftp_CEP_RE_cap.index = ['ftp_RE_cap']

ftp_CEP_PLE = total_shocks(
    Full_shocks_A, Full_shocks_Y, A, Y_s_c, Y_s_s, f, L, I, impact_indicator, strat = 'PLE', ancilliary='yes'
)
ftp_CEP_PLE.index = ['PLE']
ftp_CEP_PLE_cap = ftp_CEP_PLE/pop.values.squeeze()
ftp_CEP_PLE_cap.index = ['ftp_PLE_cap']
#%%
ftp_CEP_CP  = Ceteris_Paribus_shocks(
    Full_shocks_A, Full_shocks_Y, A, Y_s_c, Y_s_s, f, L, I, impact_indicator, ancilliary='yes', 
)
#%% Investigation origin decrease footprint below SF
index = pd.concat([
    Full_shocks_A[Full_shocks_A['type intervention'] == 'primary']['name'], 
    Full_shocks_Y[Full_shocks_Y['type intervention'] == 'primary']['name']
], axis=0).unique()
#%% Getting the contributing sectors of suffi CP 
'''
c = ['IND','KHM','LAO','MMR','ROW','VNM']

# Create a new dictionary to store the updated values
updated_ftp_CEP_CP = {}

for i, (keys, value) in enumerate(ftp_CEP_CP.items()):
    if i < len(index):  # Ensure you don't exceed the length of index
        new_key = index[i]  # Modify the key
        new_value = value.loc[:, c]  # Select the specific columns
        new_value.index = Y_s_c.index
        updated_ftp_CEP_CP[new_key] = new_value  # Store the updated key-value pair

# Now update the original dictionary
ftp_CEP_CP = updated_ftp_CEP_CP


ftp_BAU = np.diag(f.values.flatten()) @ L @ Y_s_c * 1e6
ftp_BAU = ftp_BAU.loc[:, c]
ftp_BAU.index = Y_s_c.index
ftp_BAU = ftp_BAU.groupby('sector').sum()
lab = Y_s_c.index.get_level_values(1).unique()
ftp_BAU.index = lab
# Create a new dictionary to store the modified values
new_ftp_CEP_CP = {}

for keys, value in ftp_CEP_CP.items():
    # Calculate the new value by subtracting ftp_BAU
    value = value.groupby('sector').sum()
    value.index = lab 
    new_value =  (ftp_BAU - value)/ftp_BAU
    
    # Store the new value with the same key
    new_ftp_CEP_CP[keys] = new_value

# Now update the original dictionary
ftp_CEP_CP = new_ftp_CEP_CP

results= {}
for keys, value in ftp_CEP_CP.items():
    pol = {}
    for i in range(len(value.columns)):
        label = value.columns[i]
        country = value.iloc[:,i]
        top = country.sort_values(ascending=False)
        top = top.iloc[0:3]
        pol[label] = top
    results[keys]=pol
data = []

# Loop through the outer dictionary (7 elements)
for key, inner_dict in results.items():
    # Loop through the second-level dictionary (6 elements)
    for label, top_values in inner_dict.items():
        # Loop through the top values (the 3 elements)
        for idx, value in top_values.items():
            # Add the key, label, index, and the corresponding value to the data list
            row = [key, label, idx, value]
            data.append(row)

# Create a DataFrame with 7 columns (one for each of the outer dictionary keys) and 3x6 rows for the second-level values
df = pd.DataFrame(data, columns=['Key', 'Label', 'Index', 'Value'])
'''
#%% Getting the contributing sectors of suffi TOTAL
'''
ftp_CEP_w, ftp_CEP_c = total_shocks(
    Full_shocks_A, Full_shocks_Y, A, Y_s_c, Y_s_s, f, L, I, impact_indicator, ancilliary='yes')



ftp_CEP_c =ftp_CEP_c.groupby('sector').sum()

c = ['IND','KHM','LAO','MMR','ROW','VNM']
Y_c = Y_s_c.loc[:,c]
ftp_BAU_c = np.diag(f.values.flatten()) @ L @ Y_c * 1e6
ftp_BAU_c.index = Y_s_c.index
ftp_BAU_c = ftp_BAU_c.groupby('sector').sum()
lab = Y_s_c.index.get_level_values(1).unique()

ftp_CEP_c_d = ftp_CEP_c - ftp_BAU_c.values


LAO = ftp_CEP_c_d.loc[:,['LAO']].sort_values(by  ='LAO')
tot_LAO = abs(LAO).sum().sum()
LAO_rel = (LAO/tot_LAO)*100

MMR = ftp_CEP_c_d.loc[:,['MMR']].sort_values(by  ='MMR')
tot_MMR = abs(MMR).sum().sum()
MMR_rel = (MMR/tot_MMR)*100

VNM = ftp_CEP_c_d.loc[:,['VNM']].sort_values(by  ='VNM')
tot_VNM = abs(VNM).sum().sum()
VNM_rel = (VNM/tot_VNM)*100

'''


#%%


ftp_CEP_CP = pd.concat(ftp_CEP_CP)
ftp_CEP_CP.index = index
ftp_CEP_CP_cap = ftp_CEP_CP/pop.values.squeeze()

#%%

# Define the path for the Excel file
output_dir = os.path.join(script_dir, "Results analysis")

# Ensure the directory exists
os.makedirs(output_dir, exist_ok=True)

# Define the full Excel file path
excel_path = os.path.join(output_dir, 'results.xlsx')

# Create a writer object to save all DataFrames in the same Excel file
with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    # Save DataFrames to the Excel file with each DataFrame on its own sheet
    ftp_CEP_TOT_cap.to_excel(writer, sheet_name='ftp_CEP_TOT_cap', index=True)
    ftp_CEP_TOT.to_excel(writer, sheet_name='ftp_CEP_TOT', index=True)
    ftp_CEP_CP_cap.to_excel(writer, sheet_name='ftp_CEP_CP_cap', index=True)
    ftp_CEP_CP.to_excel(writer, sheet_name='ftp_CEP_CP', index=True)
    ftp_CEP_RE_cap.to_excel(writer, sheet_name='ftp_CEP_RE_cap', index=True)
    ftp_CEP_RE.to_excel(writer, sheet_name='ftp_CEP_RE', index=True)
    ftp_CEP_PLE_cap.to_excel(writer, sheet_name='ftp_CEP_PLE_cap', index=True)
    ftp_CEP_PLE.to_excel(writer, sheet_name='ftp_CEP_PLE', index=True)
    