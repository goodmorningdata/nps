'''Create NPS park lookup table

This script allows the user to create an excel spreadsheet lookup table of all of the National Park Service sites. NPS Sites include National Parks, Monuments, Historic Sites, etc.

The script creates an Excel file as output named "nps_park_lookup.xlsx" with column headers. Columns include: park_code, park_name, designation, states, lat, and long.

This script requires the following libraries: os, sys, urllib, json, and pandas.

This script contains the following functions:

    * get_api_data - retrives data from the NPS API.
    * create_parks_df - creates a pandas dataframe from the NPS data.
    * clean_parks_df - performs data cleanup tasks on the dataframe.
'''

import os
import sys
import urllib.request, urllib.parse
import json
import pandas as pd

# Retrieve the nps api key from the config file. API key stored in the
# file, nps_config.py, in the root directory to avoid uploading it to
# Github.
sys.path.append(os.path.expanduser('~'))
from nps_config import *

def get_api_data(url):
    '''
    Read data returned by a url rquest.

    This function opens the url, reads the data returned by the url,
    and decodes the bytes object to string. It then converts the json
    document to a python dictionary. The function also prints the api
    request limit and remaining requests for the user.

    Parameters
    ----------
    url : str
      The API request url.

    Returns
    -------
    js : dict
      Json-formatted python dictionary returned by API request.
    '''

    print('')
    print('Retrieving', url)
    connection = urllib.request.urlopen(url)
    data = connection.read().decode()
    headers = dict(connection.getheaders())
    print('24-hour Request Limit: ', headers['X-RateLimit-Limit'])
    print('Requests Remaining: ', headers['X-RateLimit-Remaining'])

    try:
        js = json.loads(data)
    except:
        js = None
    if not js:
        print('==== Failure to Retrieve ====')

    return js

def create_parks_df():
    '''
    Create parks dataframe from data returned by the NPS API.

    This function creates a dataframe with columns: park_code,
    'park_name', 'designation', 'states', 'lat', and 'long'. The data
    is retrieved from the National Parks API parks-related data. The
    dataframe includes a row for each NPS site - National Parks,
    National Monuments, Historic Sites, etc.

    Parameters
    ----------
    None

    Returns
    -------
    df : pandas DataFrame
      National Parks API parks data.
    '''

    domain = 'https://developer.nps.gov/api/v1'
    path = '/parks?'
    domain_path = domain + path

    # Retrieve all park sites from the NPS API.
    url = domain_path + urllib.parse.urlencode({'limit': 600,
                                                'api_key': apikey})
    js = get_api_data(url)

    # Create the parks dataframe.
    park_list = []
    for i, item in enumerate(js['data']):
        park_list.append(item)
    df = pd.DataFrame(park_list)

    # Split latLong column into two columns.
    df['lat'] = pd.to_numeric(df['latLong'].str.split(',').str.get(0).str[4:])
    df['long'] = pd.to_numeric(df['latLong'].str.split(',').str.get(1).str[6:])

    df.rename(columns={'parkCode':'park_code', 'fullName':'park_name'},
              inplace=True)

    return df[['park_code', 'park_name', 'designation',
               'states', 'lat', 'long']]

def clean_parks_df(df):
    '''
    Performs data cleanup tasks on the parks dataframe.

    This function performs data cleanup tasks on the parks dataframe,
    the bulk of which are assigning park deignations to sites for which
    the designation is missing. Fill values were found here:
    # https://www.nps.gov/articles/nps-designations.htm and by looking
    # up park info on the park's official NPS website.

    Parameters
    ----------
    df : pandas DataFrame
      Dataframe of NPS API parks data.

    Returns
    -------
    clean_df : pandas DataFrame
      Dataframe of NPS API parks data after data cleanup.
    '''

    # Fill in missing designations.
    df.loc[df.park_code == 'npsa',
           'designation'] = 'National Park'

    df.loc[df.park_code.isin(['frde', 'kowa', 'linc', 'lyba', 'this', 'thje',
                              'vive', 'wamo', 'wwii', 'arho', 'mlkm', 'afam']),
           'designation'] = 'National Memorial'

    df.loc[df.park_code.isin(['alca']),
           'designation'] = 'National Recreation Area'

    df.loc[df.park_code.isin(['foth']),
           'designation'] = 'National Historic Site'

    df.loc[df.park_code.isin(['cahi', 'cogo', 'cwdw', 'fodu', 'haha', 'keaq',
                              'nace', 'nama', 'npnh', 'oxhi', 'paav', 'whho',
                              'prwi', 'wotr']),
           'designation'] = 'Park'

    df.loc[df.park_code.isin(['greg']),
           'designation'] = 'Scenic & Recreational River'

    df.loc[df.park_code.isin(['grsp']),
           'designation'] = 'National Historic Landmark District'

    df.loc[df.park_code.isin(['tule']),
           'designation'] = 'National Monument'

    df.loc[df.park_code.isin(['inup']),
           'designation'] = 'Heritage Center'

    # Change designation, "National Parks", to the singular.
    df.designation.replace({'National Parks':'National Park'},
                           regex=True, inplace=True)

    return df

def main():
    parks_df = create_parks_df()
    cleaned_parks_df = clean_parks_df(parks_df)
    cleaned_parks_df.to_excel('nps_park_lookup.xlsx', index=False)

if __name__ == '__main__':
    main()
