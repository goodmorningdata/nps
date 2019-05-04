'''
'''

import pandas as pd
from difflib import SequenceMatcher

def strip_park_name(park_name):
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
    #df_api['park_name_stripped'] = df_api.park_name.apply(
    #                               lambda x: strip_park_name(x))

    # Read in the list of nps sites from nps.gov into a dataframe.
    df_master = read_park_sites_web()
    #df_master['park_name_stripped'] = df_master.park_name.apply(
    #                                  lambda x: strip_park_name(x))
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
