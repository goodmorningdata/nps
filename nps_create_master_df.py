'''Create master dataframe of National Park Service park data.

This script allows the user to create an excel spreadsheet of all of the
National Park Service sites with relevant data to be used by reporting
tools. NPS Sites include National Parks, Monuments, Historic Sites, etc.
General park data, location, acreage, and visitation data are included.

The script creates an Excel file as output named
"nps_df_parks_master.xlsx" with column headers. Columns include:
park_code, park_name, designation, states, lat, long, gross_area_acres,
and columns 2008-2017 of total park visitors.

This script requires the following libraries: os, pandas, numpy, and
difflib.

Dependencies:

    * Run the script, nps_create_park_lookup.py, to create the file,
      'nps_park_lookup.xls'
    * Download the most recent acreage report from the nps website at:
      https://www.nps.gov/subjects/lwcf/acreagereports.htm Calendar
      Year Reports, Year = 2018. Place this file in the acreage_data
      directory of this project.
    * Download the most recent visitation report from the nps webiste
      at: https://irma.nps.gov/Stats/SSRSReports/National%20Reports/
      Annual%20Visitation%20By%20Park%20(1979%20-%20Last%20Calendar
      %20Year Place this file in the visitation_data directory of this
      project.

This script contains the following functions:

    *

'''

import os.path
#import requests
import pandas as pd
import numpy as np
from difflib import SequenceMatcher

def read_park_lookup():
    '''
    Read the park lookup table.

    This function reads the park lookup table from the Excel file,
    'nps_park_lookup.xls' into a pandas dataframe and sets the index
    to park_code. The park code is a 4 character code that uniquely
    identifies a NPS site. Lookup table columns include: park_code,
    park_name, designation, states, lat, long.

    Parameters
    ----------
    None

    Returns
    -------
    df : Pandas dataframe
      Park lookup dataframe.
    '''

    df = pd.read_excel('nps_park_lookup.xlsx', header=0)
    df.set_index(df.park_code, inplace=True, drop=True)

    return df

def strip_park_lookup(df):
    '''
    Simplify the park name.

    This function strips all designation text, such as 'National
    Monument' from the park_name column of the dataframe to distill the
    essence of the name. This allows for easier lookups by park name
    when trying to lookup the park_code for park data from sources other
    than the NPS API.

    Parameters
    ----------
    df : Pandas dataframe
      Park lookup dataframe.

    Returns
    -------
    df : Pandas dataframe
      Dataframe with stripped park name values and columns park_name,
      and park_code only.
    '''

    df = df[['park_name', 'park_code']]
    df['park_name'].replace({
       'National Historical Park and Ecological Preserve':'',
       'National Park & Preserve':'', 'National Historic':'',
       'National Memorial':'', 'National Heritage':'',
       'National Monument':'', 'National Heritage Corridor':'',
       'National Historical':'', 'National Parks':'', 'National Park':'',
       'National Battlefield':'', 'National Recreation Area':'',
       'National Preserve':'', 'National Military Park':'',
       'National Seashore':'', 'National Lakeshore':'',
       'National Scenic Riverway':'', 'National Scenic River':'',
       'Scenic & Recreational River':'', 'National Wild and Scenic River':'',
       'National River and Recreation Area':'',
       'Ecological & Historic Preserve':'',
       'National and State Parks':'', 'Recreation Area':'',
       'National Scenic':'', 'Site':'', 'Park':'', 'Area':''},
       regex=True, inplace=True)

    return df

def read_acreage_data(df_parks_lookup):
    '''
    Read the park acreage data file.

    This function reads the acreage data report into a dataframe,
    removes rows for parks that are not available through the NPS API,
    and simplifies the park name so that it can be more easily found in
    the park lookup table. This function also assigns the correct four-
    character park code to each row.

    To-Do:
    - Why are some parks in this list not in the API list? Are they
      part of a larger park and should be rolled in?

    Parameters
    ----------
    df_parks_lookup : Pandas dataframe
      Park lookup dataframe.

    Returns
    -------
    df : Pandas dataframe
      Park acreage dataframe.
    '''

    infile = 'acreage_data/NPS-Acreage-12-31-2018.xlsx'
    df = pd.read_excel(infile, skiprows=1)
    df = df[pd.notnull(df['State'])]
    df = df.rename({'Gross Area Acres': 'gross_area_acres'}, axis='columns')

    # Remove parks not available through the NPS API park list.
    missing_list = ['R REAGAN BOYHOOD HOME NHS', 'ROSS LAKE NRA',
                    'FT CAROLINE NMEM', 'WHITE HOUSE', 'WORLD WAR I NMEM',
                    'LAKE CHELAN NRA', 'JDROCKEFELLER MEM PKWY']
    df = df[~df['Area Name'].isin(missing_list)]

    # Strip out park designations, and make a few text replacements so
    # that park code lookup will be able to find the matching park.
    df['area_name_stripped'] = df['Area Name'].replace({'NBP':'', 'NHP':'',
                               'NHS':'', 'NMEM':'', 'NMP':'', 'NRA':'',
                               'NSR':'', 'NST':'', 'NB':'', 'NL':'', 'NM':'',
                               'NP':'', 'NS':'', 'N PRESERVE':'', 'NB':'',
                               'NMP':'', 'NATIONAL PRESERVE':'',
                               'N. SCENIC RIVER':'',
                               'NATIONAL MEMORIAL':'',
                               'FDR':'Franklin Delano Roosevelt',
                               'T ROOSEVELT':'Theodore Roosevelt',
                               'FRED-SPOTS':'FREDERICKSBURG-SPOTSYLVANIA',
                               'WWII':'World War II',
                               'DELAWARE NSR':'LOWER DELAWARE',
                               'KINGS CANYON':'SEQUOIA & KINGS CANYON'}, regex=True)

    # Call the lookup_park_code function to find the correct four-char
    # park code for each park row.
    df['park_code'] = df.area_name_stripped.apply(
                      lambda x: lookup_park_code(x, df_parks_lookup))

    df = df[['park_code', 'gross_area_acres']]

    # Convert gross acres to numeric and total for each park. This is
    # necessary because some parks have more than one row in the
    # acreage data file. For example: 'GLACIER BAY NP', and 'GLACIER
    # BAY N PRESERVE'.
    df['gross_area_acres'] = pd.to_numeric(df_acre['gross_area_acres'],
                                           errors='coerce')
    df = df.groupby(['park_code'], as_index=False).sum()

    return df

def lookup_park_code(lookup_park_name, lookup_df):
    '''
    Lookup the park code using park name.

    This function finds the row matching the lookup_park_name parameter
    in the lookup_df park dataframe using SequenceMatcher, and returns
    the four-character park code of the closest match.

    Parameters
    ----------
    lookup_park_name : str
      Park name to look up.
    lookup_df : Pandas dataframe
      Lookup table dataframe.

    Returns
    -------
    df : Pandas dataframe
      Park acreage dataframe.
    '''

    df = lookup_df[['park_name', 'park_code']]
    df['name_match'] = df['park_name'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       lookup_park_name.lower()).ratio())

    return df.loc[df['name_match'].idxmax()].park_code

def read_visitor_data(df_parks_lookup):
    '''
    Read the park visitation data file.

    This function reads the park visitor data report into a dataframe,
    removes rows for parks that are not available through the NPS API,
    and makes some replacements to the park name string so that it can
    be more easily found in the park lookup table. This function also
    assigns the correct four-character park code to each row.

    To-Do:
    - Why are some parks in this list not in the API list? Are they
      part of a larger park and should be rolled in?

    Parameters
    ----------
    df_parks_lookup : Pandas dataframe
      Park lookup dataframe.

    Returns
    -------
    df : Pandas dataframe
      Park visitation dataframe.
    '''

    df = pd.read_excel(
         'visitation_data/annual_visitation_by_park_2008_2017.xlsx',
         header=8)
    df = df[['Park Name', 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]]
    df.rename(columns = {'Park Name':'park_name'}, inplace=True)

    # Remove parks not available through the NPS API park list.
    missing_list = ['Ross Lake NRA', 'Fort Caroline NMEM', 'Lake Chelan NRA',
                    'John D. Rockefeller, Jr. MEM PKWY']
    df = df[~df['park_name'].isin(missing_list)]

    # Make a few text replacements so that park code lookup will be able
    # to find the matching park.
    df.park_name.replace(
        {'National Capital Parks Central':'National Mall and Memorial Parks',
         'Longfellow NHS':"Longfellow House Washington's Headquarters",
         'White House':"President's Park (White House)"},
         regex=True, inplace=True)

    df['park_code'] = df.park_name.apply(
                         lambda x: lookup_park_code(x, df_parks_lookup))

    # Group and sum visitor rows assigned the same park code.
    print ('Checking group by by visitor data:')
    print(df.shape[0])
    print('** duplicates:')
    print(df[df.duplicated(['park_code'], keep=False)])

    df = df.groupby(['park_code'], as_index=False).sum()
    print(df.shape[0])

    return df

# def read_wikipedia_data():
#     df = pd.read_excel('20181225_wikipedia_list_of_national_parks.xlsx',
#                        header=0,
#                        names=['Name', 'Location', 'State', 'Date Established',
#                               'Area (2017)', 'Visitors (2017)', 'Description'])
#     df.rename(columns = {'Name':'park_name',
#                          'Location':'location',
#                          'State':'state',
#                          'Date Established':'date_established',
#                          'Area (2017)':'area_2017'}, inplace=True)
#     df['park_name'] = df.park_name.apply(lambda x: x.replace('*','').strip())
#     df['park_code'] = df.park_name.apply(lambda x: lookup_park_code(x))
#     df.drop(columns=['park_name'], inplace=True)
#     df.set_index(df.park_code, inplace=True)
#
#     return df

def main():
    pd.set_option('display.max_rows', 1000)

    df_master = read_park_lookup()
    df_master_stripped = strip_park_lookup(df_master)

    df_acre = read_acreage_data(df_master_stripped)
    df_master = pd.merge(df_master, df_acre, how='left', on='park_code')

    df_visitor = read_visitor_data(df_master_stripped)
    df_master = pd.merge(df_master, df_visitor, how='left', on='park_code')

    df_master.designation.fillna('Other', inplace=True)

    print('** duplicates:')
    print(df_master[df_master.duplicated(['park_code'], keep=False)])
    df_master.to_excel('nps_df_parks_master.xlsx')

if __name__ == '__main__':
    main()