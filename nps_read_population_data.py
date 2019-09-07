import os
import sys
import urllib.request, urllib.parse
import json
import pandas as pd
import numpy as np
import itertools
from functools import reduce
from nps_shared import *

# Retrieve the census api key from the config file, nps_config.py,
# stored in the root directory.
sys.path.append(os.path.expanduser('~'))
from nps_config import *

def read_2010_2018_data():
    '''
    Data source: www.census.gov
    U.S. Census Bureau American Fact Finder
    https://factfinder.census.gov/faces/nav/jsf/pages/searchresults.xhtml?refresh=t

    - Enter "PEPANNRES" in "topic or table name" and click "Go"
    - Click the link next to ID, "PEPANNRES"
    - Click "Add/Remove Geographies"
    - Select "geographic type", "State - 040"
    - Select "All States within United States and Puerto Rico"
    - Click "Add to your selections"
    - Click "Show Table"
    - Click "Download", "Use the data", then "OK", then "Download"
    - Move this file to the _census_data folder of the project and unzip
    - File downloaded as PEP_2018_PEPANNRES.zip
    - Unzip and use file: PEP_2018_PEPANNRES_with_ann.csv
    '''

    col_names = ['state', 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
    df = pd.read_csv('_census_data/PEP_2018_PEPANNRES_with_ann.csv',
                     skiprows=3, header=None, usecols= np.r_[2, 5:14], nrows=51)
    df.columns = col_names
    df = pd.melt(df, id_vars=['state'], value_vars=col_names[1:],
                 var_name='year', value_name='population')

    return df[['year', 'state', 'population']]

def read_2000_2009_data():
    '''
    Data source: www.census.gov
    State Intercensal Tables: 2000-2010
    https://www.census.gov/data/tables/time-series/demo/popest/intercensal-2000-2010-state.html

    Click "Intercensal Estimates of the Resident Population for the
    United States, Regions, States, and Puerto Rico: April 1, 2000 to
    July 1, 2010" under "Annual Population Estimates". Save file as "st-est_2000-2010.xlsx" in the _census_data folder. Downloaded
    file is .xls, make sure to save in the newer Excel format, .xlsx.
    '''

    col_names = ['state', 2000,2001,2002,2003,2004,2005,2006,2007,2008,2009]
    df = pd.read_excel('_census_data/st-est_2000-2010.xlsx', header=None,
                       skiprows=9, nrows=51, usecols='A,C:L', names=col_names)
    df.state = df.state.str.replace('.', '')
    df = pd.melt(df, id_vars=['state'], value_vars=col_names[1:],
                 var_name='year', value_name='population')

    return df[['year', 'state', 'population']]

def read_1990_1999_data():
    '''
    Data source: www.census.gov
    Time Series of Intercensal State Population Estimates: April 1, 1990
    https://www2.census.gov/programs-surveys/popest/tables/1990-2000/intercensal/st-co/co-est2001-12-00.pdf

    1990-99 data only available at the state level as a pdf file. Used
    Tabula (https://tabula.technology/) to convert the pdf to csv and
    then performed the data cleanup tasks below to get the data into
    the correct format.
    '''
    df = pd.read_csv('_census_data/co-est2001-12-00.csv',
                     skiprows=6, skipfooter=4, usecols=[0,2,3,4,5],
                     names=['state', 1990, 'combined', 1998, 1999],
                     engine='python')
    df = df[df.state != 'Geography']
    df = df.dropna(axis=0).reset_index(drop=True)
    df = pd.concat([df[['state', 1990]],
                    df['combined'].str.split(' ', expand=True),
                    df[[1998, 1999]]],
                    axis=1)
    df = df.rename(columns = {0: 1991, 1: 1992, 2: 1993, 3: 1994,
                              4: 1995, 5: 1996, 6: 1997})

    df = pd.melt(df, id_vars=['state'], var_name='year',
                     value_name='population')
    df.population = df.population.str.replace(',','')
    df.population = pd.to_numeric(df.population)
    df = df.sort_values(by=['year', 'state'])

    return df[['year', 'state', 'population']]

def read_intercensal_table(file, start_line, end_line, col_names, cols):

    with open(file) as f:
        year_list = []
        for line in itertools.islice(f, start_line, end_line):
            line_list = line.rstrip().split(' ')
            line_list = [x for x in line_list if x]
            line_list = [line_list[i] for i in cols]
            year_list.append(line_list)
        df = pd.DataFrame(columns=col_names, data=year_list)

    return df

def read_1900_1989_data():
    '''
    Data source: www.census.gov
    State Intercensal Tables:
    https://www.census.gov/content/census/en/data/tables/time-series/demo/popest/1980s-state.html
    1980-1990
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st8090ts.txt
    1970-80
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st7080ts.txt
    1960-70
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st6070ts.txt
    1950-60
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st5060ts.txt
    1940-50
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st4049ts.txt
    1930-40
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st3039ts.txt
    1920-30
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st2029ts.txt
    1910-20
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st1019ts_v2.txt
    1900-10
    https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st0009ts.txt
    '''

    df_8084 = read_intercensal_table(
                  '_census_data/st8090ts.txt', 11, 62,
                  ['state', 1980, 1981, 1982, 1983, 1984],
                  list(range(0,6)))

    # Read years 1985 - 1989
    df_8589 = read_intercensal_table(
                  '_census_data/st8090ts.txt', 70, 121,
                  ['state', 1985, 1986, 1987, 1988, 1989],
                  list(range(0,6)))

    # Read years 1970 - 1975
    df_7075 = read_intercensal_table(
                  '_census_data/st7080ts.txt', 18, 69,
                  ['state', 1970, 1971, 1972, 1973, 1974, 1975],
                  list(range(1,8)))

    # Read years 1976-1979
    df_7679 = read_intercensal_table(
                  '_census_data/st7080ts.txt', 71, 122,
                  ['state', 1976, 1977, 1978, 1979],
                  list(range(1,6)))

    # Read years 1960 - 1964
    df_6064 = read_intercensal_table(
                  '_census_data/st6070ts.txt', 24, 75,
                  ['state', 1960, 1961, 1962, 1963, 1964],
                  [0,2,3,4,5,6])

    # Read years 1965-1969
    df_6569 = read_intercensal_table(
                  '_census_data/st6070ts.txt', 86, 142,
                  ['state', 1965, 1966, 1967, 1968, 1969],
                  list(range(0,6)))

    # Read years 1950 - 1954
    df_5054 = read_intercensal_table(
                  '_census_data/st5060ts.txt', 27, 78,
                  ['state', 1950, 1951, 1952, 1953, 1954],
                  [0,2,3,4,5,6])

    # Read years 1955 - 1959
    df_5559 = read_intercensal_table(
                  '_census_data/st5060ts.txt', 92, 143,
                  ['state', 1955, 1956, 1957, 1958, 1959],
                  list(range(0,6)))

    # Read years 1940 - 1945
    df_4045 = read_intercensal_table(
                  '_census_data/st4049ts.txt', 21, 70,
                  ['state', 1940, 1941, 1942, 1943, 1944, 1945],
                  list(range(0,7)))

    # Read years 1946 - 1949
    df_4649 = read_intercensal_table(
                  '_census_data/st4049ts.txt', 79, 143,
                  ['state', 1946, 1947, 1948, 1949],
                  list(range(0,5)))

    # Read years 1930 - 1935
    df_3035 = read_intercensal_table(
                  '_census_data/st3039ts.txt', 23, 72,
                  ['state', 1930, 1931, 1932, 1933, 1934, 1935],
                  list(range(0,7)))

    # Read years 1936 - 1939
    df_3639 = read_intercensal_table(
                  '_census_data/st3039ts.txt', 82, 143,
                  ['state', 1936, 1937, 1938, 1939],
                  list(range(0,5)))

    # Read years 1920 - 1925
    df_2025 = read_intercensal_table(
                  '_census_data/st2029ts.txt', 23, 72,
                  ['state', 1920, 1921, 1922, 1923, 1924, 1925],
                  list(range(0,7)))

    # Read years 1926 - 1929
    df_2629 = read_intercensal_table(
                  '_census_data/st2029ts.txt', 81, 143,
                  ['state', 1926, 1927, 1928, 1929],
                  list(range(0,5)))

    # Read years 1910 - 1915
    df_1015 = read_intercensal_table(
                '_census_data/st1019ts_v2.txt', 23, 72,
                ['state', 1910, 1911, 1912, 1913, 1914, 1915],
                list(range(0,7)))

    # Read years 1916 - 1919
    df_1619 = read_intercensal_table(
                '_census_data/st1019ts_v2.txt', 81, 143,
                ['state', 1916, 1917, 1918, 1919],
                list(range(0,5)))

    # Read years 1900 - 1905
    df_0005 = read_intercensal_table(
                  '_census_data/st0009ts.txt', 23, 72,
                  ['state', 1900, 1901, 1902, 1903, 1904, 1905],
                  list(range(0,7)))

    # Read years 1906 - 1909
    df_0609 = read_intercensal_table(
                  '_census_data/st0009ts.txt', 81, 143,
                  ['state', 1906, 1907, 1908, 1909],
                  list(range(0,5)))

    df_list = [df_8084, df_8589, df_7075, df_7679, df_6064, df_6569, df_5054,
               df_5559, df_4045, df_4649, df_3035, df_3639, df_2025, df_2629,
               df_1015, df_1619, df_0005, df_0609]

    df = reduce(lambda a,b: pd.merge(a, b, how='left', on='state'), df_list)
    df = pd.melt(df, id_vars=['state'], var_name='year',
                 value_name='population')
    df = df.sort_values(by=['year', 'state'])

    df.population = df.population.str.replace(',','')
    df = df.fillna(value=0)
    df.population = pd.to_numeric(df.population)
    df.population = np.where(df.year < 1970,
                             df.population * 1000,
                             df.population)
    df.state = df.state.replace(us_state_code_to_name)

    return df[['year', 'state', 'population']]

def main():
    #state_fips_dict = get_fips_state_codes()
    df_pop = pd.DataFrame(columns=['year', 'state', 'population'])

    # Add 2010-2018 census data to the dataframe.
    df_decade = read_2010_2018_data()
    df_pop = df_pop.append(df_decade, ignore_index=True, sort=True)

    # Add 2000-2009 census data to the dataframe.
    df_decade = read_2000_2009_data()
    df_pop = df_pop.append(df_decade, ignore_index=True, sort=True)

    # Add 1990-1999 census data to the dataframe.
    df_decade = read_1990_1999_data()
    df_pop = df_pop.append(df_decade, ignore_index=True, sort=True)

    # Add 1900-1989 census data to the dataframe.
    df_decade = read_1900_1989_data()
    df_pop = df_pop.append(df_decade, ignore_index=True, sort=True)

    #df_sum = df_pop.groupby(['year'])['population'].agg('sum')
    #df_sum.to_excel('_census_data/us_est_1900-2018_TOTALS.xlsx')

    (df_pop[['year', 'state','population']]
           .sort_values(by=['year', 'state'])
           .to_excel('_census_data/us_est_1900-2018.xlsx', index=False))

if __name__ == '__main__':
    main()
