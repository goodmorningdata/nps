'''Create master dataframe of National Park Service park data.

This script allows the user to create an excel spreadsheet of all of the
National Park Service sites with relevant data to be used by reporting
tools. NPS Sites include National Parks, Monuments, Historic Sites, etc.
General park data, location, acreage, and visitor data are included.

The script creates an Excel file as output named
"nps_df_parks_master.xlsx" with column headers. Columns include:
park_code, park_name, designation, states, lat, long, gross_area_acres,
gross_area_square_mile, and columns 2009-2018 of total park visitors.

This script requires the following libraries: os, pandas, numpy, and
difflib.

Dependencies:

    * Run the script, nps_create_park_lookup.py, to create the file,
      'nps_park_lookup.xls'
    * Download the most recent acreage report from the nps website at:
      https://www.nps.gov/subjects/lwcf/acreagereports.htm Calendar
      Year Reports, Year = 2018. Place this file in the acreage_data
      directory of this project.
    * Run the script, nps_read_visitor_data.py to create the file:
      annual_visitors_by_park_1979_2018.xlsx.

This script contains the following functions:

    * read_park_lookup - read the park lookup table from file.
    * strip_park_lookup - prep lookup table for park name matching.
    * lookup_park_code - lookup park code with park name.
    * read_acreage_data - read park acreage data from file.
    * read_visitor_data - read park visitation data from file.
    * add_park_sets - add a parent designation, park set, to dataframe.
'''

import os.path
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

    stripped_df = df.copy()[['park_name', 'park_code']]
    stripped_df.park_name.replace({
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

    return stripped_df

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

    infile = '_acreage_data/NPS-Acreage-12-31-2018.xlsx'
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

    # Convert gross acres to numeric and sum for each park. This is
    # necessary because some parks have more than one row in the
    # acreage data file. For example: 'GLACIER BAY NP', and 'GLACIER
    # BAY N PRESERVE'.
    df['gross_area_acres'] = pd.to_numeric(df['gross_area_acres'],
                                           errors='coerce')
    df = df.groupby(['park_code'], as_index=False).sum()

    # Add square miles and square meters columns for reporting.
    df['gross_area_square_miles'] = df.gross_area_acres * 0.0015625
    df['gross_area_square_meters'] = df.gross_area_acres * 4046.86

    return df

def read_visitor_data(df_parks_lookup):
    '''
    Read the park visitors data file.

    This function reads the park visitor data Excel file into a
    dataframe, removes rows for parks that are not available through the
    NPS API, and makes some replacements to the park name string so that
    it can be more easily found in the park lookup table. This function
    also assigns the correct four-character park code to each row.

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
      Park visitors dataframe.
    '''

    infile = '_visitor_data/annual_visitors_by_park_1979_2018.xlsx'
    df = pd.read_excel(infile, header=0)
    df.rename(columns = {'Park Name':'park_name'}, inplace=True)
    df.columns = df.columns.astype(str)

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

    # Group and sum visitor rows assigned the same park code. This is
    # necessary because some parks report visitor data separately, but
    # roll up to one park in the NPS master park list. For example:
    # 'Sequoia NP', and 'Kings Canyon NP'
    df = df.groupby(['park_code'], as_index=False).sum()

    return df

def add_park_sets(df):
    '''
    Assign park set to each NPS site.

    This function assigns a park set to each NPS park site based on
    it's designation. This is done to allow for reporting and mapping
    based on park set. Park sets include National Monuments, National
    Historic Sites, etc. A number of designations may roll up into one
    park set.

    Parameters
    ----------
    df : Pandas dataframe
      Master dataframe of all NPS park sites.

    Returns
    -------
    df : Pandas dataframe
      Master dataframe with park_set column added.
    '''

    df['park_set'] = 'Other'

    national_parks = ['National Park', 'National Park & Preserve',
                      'National and State Parks']
    df.loc[df.designation.isin(national_parks),
          'park_set'] = 'National Park'

    monuments = ['National Monument', 'National Monument & Preserve',
                 'Part of Statue of Liberty National Monument',
                 'National Monument and Historic Shrine',
                 'National Monument of America']
    df.loc[df.designation.isin(monuments),
          ['park_set']] = 'National Monument'

    preserves_reserves = ['National Preserve', 'National Reserve']
    df.loc[df.designation.isin(preserves_reserves),
          ['park_set']] = 'National Preserve or Reserve'

    lakeshores_seashores = ['National Lakeshore', 'National Seashore']
    df.loc[df.designation.isin(lakeshores_seashores),
          ['park_set']] = 'National Lakeshore or Seashore'

    rivers = ['National River & Recreation Area', 'National Scenic River',
              'National River', 'Scenic & Recreational River', 'Wild River',
              'National River and Recreation Area', 'National Scenic Riverway',
              'National Recreational River', 'Wild & Scenic River',
              'National Scenic Riverways', 'National Wild and Scenic River']
    df.loc[df.designation.isin(rivers),
          ['park_set']] = 'National River'

    trails = ['National Scenic Trail', 'National Geologic Trail',
              'National Historic Trail']
    df.loc[df.designation.isin(trails),
          ['park_set']] = 'National Trail'

    historic_sites = ['National Historical Park', 'National Historic Site',
                      'National Historic Area', 'National Historical Reserve',
                      'Part of Colonial National Historical Park',
                      'National Historical Park and Preserve',
                      'National Historical Park and Ecological Preserve',
                      'National Historic District',
                      'Ecological & Historic Preserve',
                      'International Historic Site',
                      'International Park', 'National Battlefield',
                      'National Battlefield Site', 'National Military Park',
                      'National Battlefield Park',
                      'National Historic Landmark District']
    df.loc[df.designation.isin(historic_sites),
          ['park_set']] = 'National Historic Site'

    memorials = ['National Memorial', 'Memorial']
    df.loc[df.designation.isin(memorials),
          ['park_set']] = 'National Memorial'

    recreation_areas = ['National Recreation Area']
    df.loc[df.designation.isin(recreation_areas),
          ['park_set']] = 'National Recreation Area'

    parkways = ['Parkway', 'Memorial Parkway']
    df.loc[df.designation.isin(parkways),
          ['park_set']] = 'National Parkway'

    heritage_areas = ['National Heritage Partnership',  'Heritage Area',
                      'National Heritage Corridor', 'Heritage Center',
                      'Cultural Heritage Corridor', 'National Heritage Area']
    df.loc[df.designation.isin(heritage_areas),
          ['park_set']] = 'National Heritage Area'

    affiliated_areas = ['Affiliated Area']
    df.loc[df.designation.isin(affiliated_areas),
          ['park_set']] = 'Affiliated Area'

    others = ['Park', 'Other']
    df.loc[df.designation.isin(others),
          ['park_set']] = 'Other'

    return df

def main():
    pd.set_option('display.max_rows', 1000)

    df_master = read_park_lookup()
    df_master_stripped = strip_park_lookup(df_master)

    df_acre = read_acreage_data(df_master_stripped)
    df_master = pd.merge(df_master, df_acre, how='left', on='park_code')

    df_visitor = read_visitor_data(df_master_stripped)
    df_master = pd.merge(df_master, df_visitor, how='left', on='park_code')

    df_master.designation.fillna('Other', inplace=True)
    df_master = add_park_sets(df_master)

    df_master.to_excel('nps_parks_master_df.xlsx')

if __name__ == '__main__':
    main()
