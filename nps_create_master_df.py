'''
Read data sources and create a master dataframe of NPS data for reporting.
Export this dataframe to be used by reporting tools.

List of sources:

List of data elements:

'''

import pandas as pd
import numpy as np
import requests
import os.path
#from Levenshtein import distance
from difflib import SequenceMatcher

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

def lookup_park_code(lookup_park_name, lookup_df):
    df = lookup_df[['park_name', 'park_code']]
    df['name_match'] = df['park_name'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       lookup_park_name.lower()).ratio())

    #print(df.loc[df['name_match'].idxmax()].park_name)
    #print(df.loc[df['name_match'].idxmax()].park_code)

    return df.loc[df['name_match'].idxmax()].park_code

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

# Visitor data pulled from - https://irma.nps.gov/Stats/SSRSReports/National%20
# Reports/Annual%20Visitation%20By%20Park%20(1979%20-%20Last%20Calendar%20Year)
def read_visitor_data(df_parks_lookup):
    df = pd.read_excel('visitation_reports/annual_visitation_by_park_2008_2017.xlsx', header=8)
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

# Park acreage data pulled from:
# National Park Service Acreage Reports
# https://www.nps.gov/subjects/lwcf/acreagereports.htm
# Calendar Year Reports, Year = 2018
def read_acreage_data(df_parks_lookup):
    infile = 'acreage_reports/NPS-Acreage-12-31-2018.xlsx'
    cols = ['Area Name', 'State', 'Region', 'Gross Area Acres']

    df = pd.read_excel(infile, skiprows=1)
    df = df[pd.notnull(df['State'])]

    # The following park sites are removed from the acreage dataframe because
    # they are not on the NPS master list. Maybe they are a part of other parks?
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

def read_park_lookup():
    df = pd.read_excel('park_lookup.xlsx', header=0)
    df.set_index(df.park_code, inplace=True, drop=True)

    # Fill in some missing designations. Fill values found here:
    # https://www.nps.gov/articles/nps-designations.htm
    df.loc[['frde', 'kowa', 'linc', 'lyba', 'this', 'thje','vive', 'wamo',
            'wwii', 'arho', 'mlkm', 'afam'], 'designation'] = 'National Memorial'

    return df

# Main program block.
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
df_master.to_excel('df_master.xlsx')











# This is an older version of read_acreage_data that reads a pdf file.
# Park acreage data pulled from - https://irma.nps.gov/Stats/Reports/National,
# Park Acreage Reports (1997 – Last Calendar/Fiscal Year). Used options:
# "By Park", "Calendar Year", "2017".
#
# Most recent available is 2017, so Gateway Arch National Park is not included.
#
# ** Status - Complete
#
def pdfToTable(PDFfilename, apiKey, fileExt, downloadDir):
    fileData = (PDFfilename, open(PDFfilename, 'rb'))
    files = {'f': fileData}
    postUrl = "https://pdftables.com/api?key={0}&format={1}".format(apiKey, fileExt)
    print(postUrl)
    response = requests.post(postUrl, files=files)
    response.raise_for_status()
    with open(downloadDir, "wb") as f:
        f.write(response.content)
# def read_acreage_data():
    pdffile = 'Acrebypark17CY.pdf'
    apiKey = 'r5acwelq7g3z'
    fileExt = 'csv'
    outfile = 'Acrebypark17CY.csv'

    if os.path.isfile(outfile):
        print('Acreage csv file already exists, no recreation.')
    else:
        print('Acreage csv file does not exist, creating now.')
        pdfToTable(pdffile, apiKey, fileExt, outfile)
    cols = ['Area Name', 'State', 'Reg', 'NPS Fee Acres', 'Fee Acres',
            'Fee Acres', 'Acres', 'Acres', 'Private Acres', 'Federal Acres',
            'Gross Area Acres']
    df = pd.read_csv(outfile, usecols=cols, skiprows=4)

    # Remove header and notes rows from pdf
    df = df[pd.notnull(df['Area Name'])]
    df = df[pd.notnull(df['State'])]
    df = df[df['State'] != 'Area Name']
    df = df[df['Area Name'] != 'Area Name']

    # The following park sites are removed from the acreage dataframe because
    # they are not on the NPS master list. Maybe they are a part of other parks?
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

    df_parks_stripped = strip_park_lookup(df_parks)
    df['park_code'] = df.area_name_stripped.apply(
                      lambda x: lookup_park_code(x, df_parks_stripped))
    df.set_index(df.park_code, inplace=True)
    df = df.rename({'Reg': 'region', 'Gross Area Acres': 'gross_area_acres'}, axis='columns')

    return df

# Create 4 character official NPS park code using park name.
# Examples:
#   1) Grand Canyon => grca
#   2) Arches => arch
def get_park_code(park_name):
    park_name = park_name.lower()

    # Remove 'National' and anything following
    index = park_name.find('National')
    if index > 0:
        park_name = park_name[0:index]

    # Deal with exceptions
    if 'samoa' in park_name:
        return 'npsa'
    if 'carlsbad' in park_name:
        return 'cave'
    if 'arctic' in park_name:
        return 'gaar'
    if 'wrangell' in park_name:
        return 'wrst'

    list = park_name.split(' ')
    if len(list) == 1:
        return list[0][:4].lower()
    else:
        return list[0][:2].lower() + list[1][:2].lower()
