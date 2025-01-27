# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 16:12:42 2024

@author: user
"""
from ecoinvent_interface import Settings, EcoinventRelease, ReleaseType
import os


## Downloading ecoinvent data
def download_data(username, password, version, system_model, output_path):
    # Set up your Ecoinvent credentials (username, password)
    # and specify the output path where the data will be saved.

    # Check if the output path exists; if not, create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)  # Create the output directory if it doesn't exist
        
    # Set up the settings with the provided username, password, and output path
    my_settings = Settings(username=username, password=password, output_path=output_path)

    # Initialize the EcoinventRelease object, using the provided settings
    release = EcoinventRelease(my_settings)

    # Get the release of the Ecoinvent data using the specified version, system model, and release type (LCI)
    release.get_release(version=version, system_model=system_model, release_type=ReleaseType.lci)

    # Return None as there is no further output needed from this function
    return None

# Define the output path where the data will be saved
output_path = r'C:\Users\user\OneDrive - Universiteit Leiden\Thesis Franco\Step 3\sufficientarianism\Ecoivent_exiobase matching'

# Call the function to download the data, providing the credentials, version, system model, and output path
download_data('LUCML', 'ecoV3JG62,0', '3.8', 'cutoff', output_path)
