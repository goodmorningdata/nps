'''
Create master dataframe of National Park Service site data.

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

    This function strips designation from the park name so that matching
    names between two different sources will work correctly. There may 
    small differences in the name of the same park from two differenct
    sources.
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
    '''
    '''
    df = pd.read_excel('nps_park_sites_web.xlsx', header=0)
    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    return df

def read_park_sites_api():
    '''
    '''
    df = pd.read_excel('nps_park_sites_api.xlsx', header=0)
    #df.park_name.replace({'&':'and'}, regex=True, inplace=True)
    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    return df[['park_code', 'park_name', 'park_name_stripped',
               'states', 'lat', 'long']]

def lookup_park_code(park_name, lookup_df):
    df = lookup_df
    df['name_match'] = df['park_name_stripped'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       park_name.lower()).ratio())
    park_code = df.loc[df['name_match'].idxmax()].park_code

    if park_name == 'Arlington House': park_code = 'arho'
    if park_name in ['Kings Canyon', 'Sequoia']: park_code = 'seki'

    return park_code

def main():
    pd.set_option('display.max_rows', 1000)

    # Read in the list of nps sites from the nps api into a dataframe.
    df_api = read_park_sites_api()

    # Read in the list of nps sites from nps.gov into a dataframe.
    df_master = read_park_sites_web()
    df_master['park_code'] = df_master.park_name_stripped.apply(
                             lambda x: lookup_park_code(x, df_api))

    # Merge the nps.gov and nps api dataframes.
    df_master = pd.merge(df_master[['park_name', 'park_code', 'designation']],
                         df_api[['park_code', 'states', 'lat', 'long']],
                         how='left', on='park_code')

    df_master = df_master.sort_values(by=['park_name']).reset_index(drop=True)
    print(df_master)

    df_master.to_excel('nps_parks_master_df.xlsx')

if __name__ == '__main__':
    main()
