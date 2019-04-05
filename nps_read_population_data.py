import os
import sys
import urllib.request, urllib.parse
import json
import pandas as pd
import itertools

# Retrieve the census api key from the config file, nps_config.py,
# stored in the root directory.
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

    try:
        js = json.loads(data)
    except:
        js = None
    if not js:
        print('==== Failure to Retrieve ====')

    #print (json.dumps(js, indent=1))

    return js

def read_1970_1979_data():
    # Read years 1970 - 1975
    with open('_census_data/us-est_1970-1980.txt') as f:
        year_list = []
        for line in itertools.islice(f, 14, 65):
            line_list = line.rstrip().split(' ')
            line_list = [x for x in line_list if x]
            year_list.append(line_list[1:])
        df1 = pd.DataFrame(columns=['state', '1970', '1971', '1972', '1973',
                                    '1974','1975'], data=year_list)

    # Read years 1976-1980
    with open('_census_data/us-est_1970-1980.txt') as f:
        year_list = []
        for line in itertools.islice(f, 67, 118):
            line_list = line.rstrip().split(' ')
            line_list = [x for x in line_list if x]
            year_list.append(line_list[1:6])
        df2 = pd.DataFrame(columns=['state', '1976', '1977', '1978', '1979'],
                           data=year_list)

    df = df1.merge(df2, how='left', on='state')
    df = pd.melt(df, id_vars=['state'],
                     var_name='year',
                     value_name='population')

    return df[['year', 'state', 'population']]

def read_1980_1989_data():
    # Read years 1980 - 1984
    with open('_census_data/us-est_1980-1990.txt') as f:
        year_list = []
        for line in itertools.islice(f, 11, 62):
            line_list = line.rstrip().split(' ')
            line_list = [x for x in line_list if x]
            year_list.append(line_list)
        df1 = pd.DataFrame(columns=['state', '1980', '1981', '1982', '1983',
                                    '1984'], data=year_list)

    # Read years 1985 - 1990
    with open('_census_data/us-est_1980-1990.txt') as f:
        year_list = []
        for line in itertools.islice(f, 70, 121):
            line_list = line.rstrip().split(' ')
            line_list = [x for x in line_list if x]
            year_list.append(line_list[:6])
        df2 = pd.DataFrame(columns=['state', '1985', '1986', '1987', '1988',
                                    '1989'], data=year_list)

    df = df1.merge(df2, how='left', on='state')
    df = pd.melt(df, id_vars=['state'],
                     var_name='year',
                     value_name='population')

    return df[['year', 'state', 'population']]

def read_1990_2000_data():
    df = pd.read_csv('_census_data/us-est_1990-2000.csv',
                     names=['year', 'age', 'population', 'male', 'female'],
                     skiprows=2)
    df = df[df.age == 'All Age']
    df = df.drop(['male', 'female', 'age'], axis=1)
    df = df[df.year.str[:4] == 'July']
    df['year'] = df['year'].str[8:]
    df['state'] = 'XX'

    return df[['year', 'state', 'population']]

def read_2000_2010_data():
    ['']
    df = pd.read_excel('_census_data/us-est_2000-2010.xls',
                       header=3, nrows=1, usecols='C:L')
    df = df.T.reset_index().rename(columns = {'index':'year', 0:'population'})
    df['state'] = 'XX'

    return df[['year', 'state', 'population']]

def get_2010_2017_data(state_fips_dict):
    '''
    Rerieve U.S. population data from the census.gov api. Data is
    available by state for this decade.

    Returns
    -------
    df : pandas DataFrame
      U.S. Census data.
    '''

    domain = 'https://api.census.gov'

    df = pd.DataFrame(columns=['year', 'state', 'population'])
    years = list(map(lambda x: str(x), range(2010, 2018)))

    for year in years:
        path = '/data/' + year + '/acs/acs1?'
        domain_path = domain + path
        url = domain_path + urllib.parse.urlencode({'get': 'B01003_001E',
                                                    'for': 'state:*',
                                                    'key': census_apikey})
        js = get_api_data(url)
        year_df = pd.DataFrame(columns=['population', 'state'],
                               data=js[1:])

        year_df['state'].replace(state_fips_dict, inplace=True)
        year_df['year'] = year
        df = df.append(year_df, ignore_index=True, sort=True)

    return(df[['year', 'state', 'population']])

def get_fips_state_codes():
    df = pd.read_excel('_reference_data/fips_state_codes.xlsx',
                       header=0)
    df.dropna(axis=0, inplace=True)
    df = df[['state_alpha_code', 'state_fips_code']]
    df['state_fips_code'] = df['state_fips_code'].apply(str).str.rjust(2,'0')
    d = dict([(f, a) for f, a in zip(df.state_fips_code, df.state_alpha_code)])

    return d

def main():
    state_fips_dict = get_fips_state_codes()
    pop_df = pd.DataFrame(columns=['year', 'state', 'population'])

    decade_df = read_1970_1979_data()
    pop_df = pop_df.append(decade_df, ignore_index=True, sort=True)

    decade_df = read_1980_1989_data()
    pop_df = pop_df.append(decade_df, ignore_index=True, sort=True)

    decade_df = read_1990_2000_data()
    pop_df = pop_df.append(decade_df, ignore_index=True, sort=True)

    decade_df = read_2000_2010_data()
    pop_df = pop_df.append(decade_df, ignore_index=True, sort=True)

    decade_df = get_2010_2017_data(state_fips_dict)
    pop_df = pop_df.append(decade_df, ignore_index=True, sort=True)

    (pop_df[['year', 'state','population']]
           .to_excel('_census_data/us_est_1970-2017.xlsx', index=False))

if __name__ == '__main__':
    main()
