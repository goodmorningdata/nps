''' Create master dataframe of National Park Service site data.

This script creates a dataframe of all data collected by this project
about the NPS official units.
1. Read the data available from the api. This source provides the four
   character code that uniquely identifies each park, the list of state
   codes the park is in, and the latitude and longitiude of the park.
2. Merge the api data with the list of official park units available
   on nps.gov. This source provides the official list of units, the park
   name, and park designation.

Required libraries: pandas, SequenceMatcher

Dependencies:
    * Run the script, nps_get_park_sites_web.py, to create the file,
      'nps_park_sites_web.xlsx'.
    * Run the script, nps_get_par_sites_api.py, to create the file,
      'nps_park_sites_api.xlsx'.
'''

import pandas as pd
from difflib import SequenceMatcher

def strip_park_name(park_name):
    ''' Strip unnecessary text from park name.

    Park names for the same park may be slightly different between
    sources, making matching them difficult. This function strips
    designation from the park name to improve the chance of matching.

    Parameters
    ----------
    park_name : str : Park name to strip of designations.

    Returns
    -------
    park_name : str : Stripped park name.
    '''

    park_name = (park_name.replace('National Monument & Preserve','')
                          .replace('National Park & Preserve','')
                          .replace('National Park and Preserve','')
                          .replace('National Historical Park','')
                          .replace('National Historic Site','')
                          .replace('National Monument','')
                          .replace('National Park','')
                          .replace('National Preserve','')
                          .replace('National Scenic and Recreational River','')
                          .replace('&', 'and'))

    return park_name.rstrip()

def read_park_sites_web():
    ''' Read list of park sites from the nps.gov web source.

    Read the list of park sites extracted from nps.gov and saved
    in an Excel file by the nps_get_park_sites_web.py script into a
    dataframe.

    Parameters
    ----------
    None

    Returns
    -------
    df : pandas DataFrame : Dataframe of park site data.
    '''

    df = pd.read_excel('_reference_data/nps_park_sites_web.xlsx', header=0)
    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    return df

def read_park_sites_api():
    ''' Read list of park sites from the NPS API source.

    Read the list of park sites and associated data pulled from the
    NPS API and saved in an Excel file by the nps_get_park_sites_api.py
    script into a dataframe.

    Parameters
    ----------
    None

    Returns
    -------
    df : pandas DataFrame : Dataframe of park site data.
    '''

    df = pd.read_excel('_reference_data/nps_park_sites_api.xlsx', header=0)
    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    return df[['park_code', 'park_name', 'park_name_stripped',
               'states', 'lat', 'long']]

def lookup_park_code(park_name, lookup_df):
    ''' Look up the park code for a park using the park name.

    Each park is assigned a four character park code that uniquely
    identifies it. The park code for each park is available from the
    NPS API. This function accepts a park name and returns the park code
    after looking in up in the API dataframe.

    Parameters
    ----------
    park_name : str : Park name to lookup the code for.
    lookup_df : pandas DataFrame : Dataframe of park names and codes.

    Returns
    -------
    df : pandas DataFrame : Dataframe of park site data.
    '''

    df = lookup_df
    # Use SequenceMatcher to comapre the stripped park names and find
    # the best match.
    df['name_match'] = df['park_name_stripped'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       park_name.lower()).ratio())
    park_code = df.loc[df['name_match'].idxmax()].park_code

    # The park names for the following parks differ so greatly between
    # the name to be lookup up and the name in the API dataframe, that
    # they must be assigned directly.
    if park_name == "Arlington House": park_code = 'arho'
    if park_name in ["Kings Canyon", "Sequoia"]: park_code = 'seki'

    return park_code

def main():
    pd.set_option('display.max_rows', 1000)

    # Read in the list of nps sites from the nps api into a dataframe.
    df_api = read_park_sites_api()

    # Read in the list of nps sites from nps.gov into a dataframe.
    df_master = read_park_sites_web()

    # Find the park code for each park in the df_master dataframe by
    # matching it to the park in the df_api dataframe.
    df_master['park_code'] = df_master.park_name_stripped.apply(
                             lambda x: lookup_park_code(x, df_api))

    # Merge the nps.gov and nps api dataframes.
    df_master = pd.merge(df_master[['park_name', 'park_code', 'designation']],
                         df_api[['park_code', 'states', 'lat', 'long']],
                         how='left', on='park_code')

    df_master = df_master.sort_values(by=['park_name']).reset_index(drop=True)
    print(df_master)

    # Save the dataframe to an Excel file.
    df_master.to_excel('nps_parks_master_df.xlsx')

if __name__ == '__main__':
    main()
