'''Create master dataframe of National Park Service park data.

This script allows the user to create an excel spreadsheet of all of the
National Park Service sites to be used by reporting tools. NPS Sites
include National Parks, Monuments, Historic Sites, etc. General park
data, location, acreage, and visitation data are all included.

The script creates an Excel file as output named
"nps_df_parks_master.xlsx" with column headers. Columns include:
park_code, park_name, designation, states, lat, long, gross_area_acres,
and columns 2008-2017 of total park visitors.

This script requires the following libraries: os, pandas, numpy, and
difflib.

Data sources:

    * General Park Data - NPS Data API


This script contains the following functions:

    *

Read data sources and create a master dataframe of NPS data for reporting.
Export this dataframe to be used by reporting tools.

List of sources:

List of data elements:

'''

import os.path
#import requests
import pandas as pd
import numpy as np
from difflib import SequenceMatcher

def read_park_lookup():
    df = pd.read_excel('park_lookup.xlsx', header=0)
    df.set_index(df.park_code, inplace=True, drop=True)

    return df

def strip_park_lookup(df):
    df = df[['park_name', 'park_code']]
    # Strip out all desgnations and abbreviations to distill the essence of the
    # park name to make lookups work correctly.
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

# Park acreage data pulled from:
# National Park Service Acreage Reports
# https://www.nps.gov/subjects/lwcf/acreagereports.htm
# Calendar Year Reports, Year = 2018
def read_acreage_data(df_parks_lookup):
    infile = 'acreage_data/NPS-Acreage-12-31-2018.xlsx'
    cols = ['Area Name', 'State', 'Region', 'Gross Area Acres']

    df = pd.read_excel(infile, skiprows=1)
    df = df[pd.notnull(df['State'])]

    # The following park sites are removed because they are not on the
    # NPS master list. MORE RESEARCH - there are part of other parks?
    missing_list = ['R REAGAN BOYHOOD HOME NHS', 'ROSS LAKE NRA',
                    'FT CAROLINE NMEM', 'WHITE HOUSE', 'WORLD WAR I NMEM',
                    'LAKE CHELAN NRA', 'JDROCKEFELLER MEM PKWY']
    df = df[~df['Area Name'].isin(missing_list)]

    # Strip out park designations and abbreviations so that matching to the nps
    # lookup table will work correctly. Also includes a few text swaps so that
    # lookup will work.
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

    df['park_code'] = df.area_name_stripped.apply(
                      lambda x: lookup_park_code(x, df_parks_lookup))
    df = df.rename({'Gross Area Acres': 'gross_area_acres'}, axis='columns')
    df = df[['park_code', 'gross_area_acres']]

    return df

def lookup_park_code(lookup_park_name, lookup_df):
    df = lookup_df[['park_name', 'park_code']]
    df['name_match'] = df['park_name'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       lookup_park_name.lower()).ratio())

    #print(df.loc[df['name_match'].idxmax()].park_name)
    #print(df.loc[df['name_match'].idxmax()].park_code)

    return df.loc[df['name_match'].idxmax()].park_code

# Visitor data pulled from - https://irma.nps.gov/Stats/SSRSReports/National%20
# Reports/Annual%20Visitation%20By%20Park%20(1979%20-%20Last%20Calendar%20Year)
def read_visitor_data(df_parks_lookup):
    df = pd.read_excel(
         'visitation_data/annual_visitation_by_park_2008_2017.xlsx',
         header=8)
    df = df[['Park Name', 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]]
    df.rename(columns = {'Park Name':'park_name'}, inplace=True)

    # The following park sites are removed from the visitor dataframe because
    # they are not on the NPS master list. Maybe they are a part of other parks?
    missing_list = ['Ross Lake NRA', 'Fort Caroline NMEM', 'Lake Chelan NRA',
                    'John D. Rockefeller, Jr. MEM PKWY']
    df = df[~df['park_name'].isin(missing_list)]

    df.park_name.replace(
        {'National Capital Parks Central':'National Mall and Memorial Parks',
         'Longfellow NHS':"Longfellow House Washington's Headquarters",
         'White House':"President's Park (White House)"},
         regex=True, inplace=True)

    df['park_code'] = df.park_name.apply(
                         lambda x: lookup_park_code(x, df_parks_lookup))
    #df.set_index(['park_code'], inplace=True)

    return df

def read_wikipedia_data():
    df = pd.read_excel('20181225_wikipedia_list_of_national_parks.xlsx',
                       header=0,
                       names=['Name', 'Location', 'State', 'Date Established',
                              'Area (2017)', 'Visitors (2017)', 'Description'])
    df.rename(columns = {'Name':'park_name',
                         'Location':'location',
                         'State':'state',
                         'Date Established':'date_established',
                         'Area (2017)':'area_2017'}, inplace=True)
    df['park_name'] = df.park_name.apply(lambda x: x.replace('*','').strip())
    df['park_code'] = df.park_name.apply(lambda x: lookup_park_code(x))
    df.drop(columns=['park_name'], inplace=True)
    df.set_index(df.park_code, inplace=True)

    return df

def main():
    pd.set_option('display.max_rows', 1000)

    df_master = read_park_lookup()
    df_master_stripped = strip_park_lookup(df_master)

    df_acre = read_acreage_data(df_master_stripped)
    df_acre['gross_area_acres'] = pd.to_numeric(df_acre['gross_area_acres'], errors='coerce')
    df_acre = df_acre.groupby(['park_code'], as_index=False).sum()

    df_master = pd.merge(df_master, df_acre, how='left', on='park_code')
    print(df_master[['park_code', 'designation']])

    df_visitor = read_visitor_data(df_master_stripped)
    df_visitor = df_visitor.groupby(['park_code'], as_index=False).sum()

    df_master = pd.merge(df_master, df_visitor, how='left', on='park_code')

    df_master.designation.fillna('Other', inplace=True)

    print('** duplicates:')
    print(df_master[df_master.duplicated(['park_code'], keep=False)])
    df_master.to_excel('nps_df_parks_master.xlsx')

if __name__ == '__main__':
    main()
