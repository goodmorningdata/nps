#import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.parse
import json
import pandas as pd
import os, sys

# Get the nps api key from the config file.
# Store the key in the file, nps_config.py, in the home directory, so that code
# can be pushed to GitHub with no security concerns.
sys.path.append(os.path.expanduser('~'))
from nps_config import *

def retrieve_data(url):
    print('')
    print('Retrieving', url)
    connection = urllib.request.urlopen(url)
    data = connection.read().decode()
    headers = dict(connection.getheaders())
    print('Limit', headers['X-RateLimit-Limit'])
    print('Remaining', headers['X-RateLimit-Remaining'])

    try:
        js = json.loads(data)
    except:
        js = None
    if not js:
        print('==== Failure to Retrieve ====')

    # Option to print the json.
    #print(json.dumps(js, indent=4))
    return js

def get_api_data():
    domain = 'https://developer.nps.gov/api/v1'
    path = '/parks?'
    domain_path = domain + path

    # Retrieve the total number of park sites.
    url = domain_path + urllib.parse.urlencode({'limit': 1,
                                                'api_key': apikey})
    js = retrieve_data(url)
    total_sites = js['total']
    print('Total number of park sites: ', js['total'])

    # Retrieve all park sites using the total number as the limit.
    url = domain_path + urllib.parse.urlencode({'limit': total_sites,
                                                'api_key': apikey})
    js = retrieve_data(url)

    # Create parks dataframe.
    park_list = []
    for i, item in enumerate(js['data']):
        park_list.append(item)
    df = pd.DataFrame(park_list)

    # Split latLong column into two columns.
    df['lat'] = pd.to_numeric(df['latLong'].str.split(',').str.get(0).str[4:])
    df['long'] = pd.to_numeric(df['latLong'].str.split(',').str.get(1).str[6:])

    # Rename some columns
    df.rename(columns={'parkCode':'park_code', 'fullName':'park_name'},
              inplace=True)

    # Data Cleanup - Assign the correct designation to National Park of American
    # Samoa. Designation is blank via api.
    df.loc[df.park_code == 'npsa', 'designation'] = 'National Park'

    # Data Cleanup - Fill in some missing designations. Fill values found here:
    # https://www.nps.gov/articles/nps-designations.htm and found by looking
    # up park info on nps site.
    df.loc[df.park_code.isin(['frde', 'kowa', 'linc', 'lyba', 'this', 'thje',
                              'vive', 'wamo', 'wwii', 'arho', 'mlkm', 'afam']),
                              'designation'] = 'National Memorial'

    df.loc[df.park_code.isin(['alca']),
                              'designation'] = 'National Recreation Area'

    df.loc[df.park_code.isin(['foth']),
                              'designation'] = 'National Historic Site'

    df.loc[df.park_code.isin(['cahi', 'cogo', 'cwdw', 'fodu', 'haha', 'keaq',
                              'nace', 'nama', 'npnh', 'oxhi', 'paav', 'whho',
                              'prwi', 'wotr']), 'designation'] = 'Park'

    df.loc[df.park_code.isin(['greg']),
                              'designation'] = 'Scenic & Recreational River'

    df.loc[df.park_code.isin(['grsp']),
                              'designation'] =
                              'National Historic Landmark District'

    df.loc[df.park_code.isin(['tule']), 'designation'] = 'National Monument'
    df.loc[df.park_code.isin(['inup']), 'designation'] = 'Heritage Center'

    # Data Cleanup - Change designation, "National Parks", to the singular.
    df.designation.replace(
        {'National Parks':'National Park'},
         regex=True, inplace=True)

    return df[['park_code', 'park_name', 'designation',
               'states', 'lat', 'long']]

df = get_api_data()
df.to_excel('park_lookup.xlsx', index=False)
