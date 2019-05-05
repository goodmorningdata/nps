''' Pull park data from NPS API.

This script pulls park site data from the NPS API into a dataframe and
saves it as the Excel file, nps_park_sites_api.xlsx.

This script requires the following libraries: os, sys, urllib, json,
and pandas.

Dependencies:
    * Create file, nps_config.py file in the root directory to store
      the user's NPS API key. File should contain the line:
      "api_key = ", followed by the API key in quotations.
'''

import os
import sys
import urllib.request, urllib.parse
import json
import pandas as pd

# Retrieve the nps api key from the config file, nps_config.py, stored
# in the root directory.
sys.path.append(os.path.expanduser('~'))
from nps_config import *

def get_api_data(url):
    ''' Read data returned by a url rquest.

    This function opens the url, reads the data returned by the url,
    and decodes the bytes object to string. It then converts the json
    document to a python dictionary. The function also prints the api
    request limit and remaining requests for the user.

    Parameters
    ----------
    url : str : The API request url.

    Returns
    -------
    js : dict : Json-formatted python dictionary returned by API request.
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
    ''' Create parks dataframe from data returned by the NPS API.

    This function calls the get_api_data function to pull park site
    data from the NPS API using the /parks path. The API data is loaded
    into a dataframe, and the latLong field is split into two columns.

    Parameters
    ----------
    None

    Returns
    -------
    df : pandas DataFrame : Dataframe of park sites.
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

def main():
    df_parks = create_parks_df()
    df_parks.to_excel('_reference_data/nps_park_sites_api.xlsx',
                      index=False)

if __name__ == '__main__':
    main()
