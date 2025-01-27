import pandas as pd
import os

script_directory = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory
os.chdir(script_directory)

non_eu_countries = [
    'Argentina', 'Australia', 'Bahrain', 'Brazil', 'Canada', 'Chile', 'China', 'Colombia', 
    'Costa Rica', 'China, Hong Kong SAR', 'Iceland', 'India', 'Indonesia', 'Israel', 'Japan', 'Kazakhstan', 
    'Cambodia', 'Lao People\'s Democratic Republic', 'Malaysia', 'Mexico', 'Morocco', 'Myanmar', 
    'New Zealand', 'Norway', 'Peru', 'Philippines', 'Russian Federation', 'Saudi Arabia', 'Singapore', 
    'South Africa', 'Republic of Korea', 'China, Taiwan Province of China', 'Thailand', 'Tunisia', 
    'Türkiye', 'United Kingdom', 'United States of America', 'Viet Nam', 'Switzerland'
]
eu_countries = [
    'Austria', 'Belgium', 'Bulgaria', 'Cyprus', 'Czechia', 'Germany', 'Denmark', 
    'Spain', 'Estonia', 'Finland', 'France', 'Greece', 'Croatia', 'Hungary', 'Ireland', 
    'Italy', 'Luxembourg', 'Lithuania', 'Latvia', 'Malta', 'Netherlands', 'Poland', 
    'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Sweden'
]

data_pop = pd.read_csv(script_directory + '\\WPP2024_Demographic_Indicators_Medium.csv/s.csv')

#%%

pop = data_pop.loc[(data_pop['Time'] == 2021) & (data_pop['ISO3_code'].notna()), ['TPopulation1Jan', 'Location', 'ISO3_code']]
pop['TPopulation1Jan'] *= 1000  # Convert population to the full number

# Assign 'correspondence' based on country groupings
pop['correspondence'] = pop['Location'].apply(
    lambda x: 'EU' if x in eu_countries else ('ROW' if x not in non_eu_countries else x)
)

# Sum the populations by correspondence group and sort
pop = pop.groupby('correspondence').sum().reset_index().drop(columns=['Location', 'ISO3_code']).set_index('correspondence')
pop.index.name = 'country'

match = pd.read_excel(script_directory + '\\country_label_correspondence.xlsx', header=None)

name_to_abbrev = dict(zip(match.loc[1], match.loc[0]))

# Rename columns of C_PB using the mapping dictionary
pop = pop.T.rename(columns=name_to_abbrev).sort_index(axis=1)
pop.to_csv(script_directory + '\\population.csv', index=True)

# Blue water planetary boundary: 4,000 km³/yr
# Blue water planetary boundary per capita: 574 m³/yr

ftp_EG = pop * 1.61
ftp_EG.index = ['ftp_EG']

#%%

# Normalize and split the directory path
path_parts = script_directory.split(os.sep)

# Remove "liberal egalitarianism" from the path parts
if "egalitarianism" in path_parts:
    path_parts.remove("egalitarianism")

if "step 3" in path_parts:
    path_parts.remove("step 3")

# Define the Excel file path
excel_path = os.path.join(os.sep.join(path_parts), "Results analysis", 'results.xlsx')

# Append the DataFrame to an Excel file, creating a new sheet named after the DataFrame
with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    ftp_EG.to_excel(writer, sheet_name='ftp_EG', index=True)
