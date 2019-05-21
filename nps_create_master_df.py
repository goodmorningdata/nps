'''
This script creates a dataframe of all data collected by this project
about the National Park Service Parks/Units. As of May 1, 2019, the NPS
manages 419 official units and 170 Related Areas. This project deals
only with the 419 official units.

1) Read the data available from the api. This source provides the four
   character code that uniquely identifies each park, the list of state
   codes the park is in, and the latitude and longitiude of the park.
2) Create the master dataframe by merging the api data with the list of
   official park units available on nps.gov. This source provides the
   official list of units, the park name, and park designation.
3) Read the established date for each National Park, available on a
   Wikipedia page, and merge with the master dataframe.
4) Read the park size data, available from nps.gov as a report, and
   merge with the master dataframe.
5) Read the park visitor use statistics, available from nps.gov as a
   report, and merge with the master dataframe.

Required Libraries
------------------
pandas, SequenceMatcher

Dependencies
------------
1) Run the script, nps_get_park_sites_web.py, to create the file,
   'nps_park_sites_web.xlsx'.
2) Run the script, nps_get_park_sites_api.py, to create the file,
   'nps_park_sites_api.xlsx'.
3) Run the script, nps_get_wikipedia_data.py, to create the file,
   'wikipedia_date_established.csv'.
4) Download the most recent acreage report from the nps website at:
   https://www.nps.gov/subjects/lwcf/acreagereports.htm Calendar
   Year Reports, Year = 2018. Place this file in the '_acreage_data'
   directory of this project.
5) Run the script, nps_read_visitor_data.py to create the file:
   annual_visitors_by_park_1904_2018.xlsx.
'''

import pandas as pd
from difflib import SequenceMatcher

def strip_park_name(park_name):
    '''
    Park names for the same park may be slightly different between
    sources, making matching them difficult. This function strips
    some designations from the park name to improve the chance of
    matching.

    Parameters
    ----------
    park_name : str
        Park name to strip of designations.

    Returns
    -------
    park_name : str
        Stripped park name.
    '''

    park_name = (park_name.replace("National Monument & Preserve", "")
                          .replace("National Park & Preserve", "")
                          .replace("National and State Parks", "")
                          .replace("National Monument", "")
                          .replace("National Park", "")
                          .replace("National Preserve", "")
                          .replace("NATIONAL PRESERVE", ""))
    if park_name.endswith('NP'):
        park_name = park_name.replace(" NP", "")

    return park_name.rstrip()

def read_park_sites_api():
    '''
    Read the list of park sites and associated data pulled from the
    NPS API and saved in an Excel file by the nps_get_park_sites_api.py
    script into a dataframe.

    Parameters
    ----------
    None

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park site data.
    '''

    filename = '_reference_data/nps_park_sites_api.xlsx'
    df = pd.read_excel(filename, header=0)

    # Exclude park codes that are not in the National Park System list
    # of 419 Units/Parks.
    exclude_park_codes = ['afam', 'alka', 'anch', 'alca', 'aleu', 'amme',
                          'anac', 'armo', 'attr', 'auca', 'balt', 'bawa',
                          'blrn', 'cali', 'crha', 'came', 'cahi', 'cajo',
                          'chva', 'cbpo', 'cbgn', 'cwdw', 'coal', 'colt',
                          'xrds', 'dabe', 'dele', 'elte', 'elca', 'elis',
                          'erie', 'esse', 'fati', 'fodu', 'fofo', 'glec',
                          'glde', 'grfa', 'grsp', 'guge', 'haha', 'jame',
                          'hurv', 'inup', 'iafl', 'iatr', 'blac', 'jthg',
                          'juba', 'keaq', 'klse', 'lecl', 'lode', 'loea',
                          'maac', 'mide', 'migu', 'mihi', 'mopi', 'auto',
                          'mush', 'avia', 'npnh', 'neen', 'pine', 'nifa',
                          'noco', 'oire', 'okci', 'olsp', 'oreg', 'ovvi',
                          'oxhi', 'para', 'poex', 'prsf', 'rist', 'roca',
                          'safe', 'scrv', 'semo', 'shvb', 'soca', 'stsp',
                          'tecw', 'qush', 'thco', 'tosy', 'trte', 'waro',
                          'whee', 'wing', 'york']
    df = df[~(df.park_code.isin(exclude_park_codes))]

    # Replace certain park names so that they will be matched correctly
    # with the park names in the official list of 419.
    df['park_name'].replace(
        {"Ford's Theatre":"Ford's Theatre National Historic Site",
        "Pennsylvania Avenue":"Pennsylvania Avenue National Historic Site",
        "Arlington House, The Robert  E. Lee Memorial":"Arlington House",
        "President's Park \(White House\)":"White House",
        "Great Egg Harbor River":
            "Great Egg Harbor National Scenic and Recreational River",
        "Lower Delaware National Wild and Scenic River":
            "Delaware National Scenic River"},
        regex=True, inplace=True)

    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    df = df.sort_values(by=['park_name'])

    return df[['park_code', 'park_name', 'park_name_stripped',
               'states', 'lat', 'long']]

def read_park_sites_web(df_api):
    '''
    Read the list of 419 units/parks managed by the National Park
    Service from nps.gov and saved in an Excel file by the
    nps_get_park_sites_web.py script into a dataframe.

    Parameters
    ----------
    df_api : pandas DataFrame
        Dataframe of data from api in which to lookup park code.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park site data.
    '''

    filename = '_reference_data/nps_park_sites_web.xlsx'
    df = pd.read_excel(filename, header=0)

    # MLK Historic Park park name is ambiguous and makes park name
    # matching impossible, replace with more specific name.
    df.loc[df.park_name == "Martin Luther King", 'park_name'] = "Martin Luther King National Historic Park"

    # Find the park code for each park in the df_master dataframe by
    # matching it to the park in the df_api dataframe.
    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))
    df['park_code'] = df.park_name_stripped.apply(
                      lambda x: lookup_park_code(x, df_api))

    return df

def lookup_park_code(park_name, df_lookup):
    '''
    Each park is assigned a four character park code that uniquely
    identifies it. The park code for each park is available from the
    NPS API. This function accepts a park name and returns the park code
    after looking in up in the API dataframe.

    Parameters
    ----------
    park_name : str
        Park name to lookup the code for.
    df_lookup : pandas DataFrame
        Dataframe of park names and codes.

    Returns
    -------
    park_code : str
        Park code that matches the park name.
    '''

    df = df_lookup

    # Use SequenceMatcher to find the best park name match.
    df['name_match'] = df['park_name_stripped'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       park_name.lower()).ratio())
    park_code = df.loc[df['name_match'].idxmax()].park_code

    # Although Kings Canyon NP and Sequoia NP are separate parks, they
    # are managed together and share the same park code.
    if park_name.lower().find('kings canyon') > -1: park_code = 'seki'
    if park_name.lower().find('sequoia') > -1: park_code = 'seki'

    # Fort Caroline National Memorial is a part of the Timucuan
    # Ecological and Hitoric Preserve (FL). Vistor date and acreage for
    # both should be combined.
    if park_name.lower().find('caroline') > -1: park_code = 'timu'

    # Lake Chelan NRA and Ross Lake NRA are both part of the North
    # Cascades National Park Service Complex. Visitor data and acreage
    # for all three areas should be combined.
    if park_name.lower().find('chelan') > -1: park_code = 'noca'
    if park_name.lower().find('ross lake') > -1: park_code = 'noca'

    # The John D. Rockefeller, Jr. Memorial Parkway is in Grand Teton
    # National Park (WY) and does not have its own park code. Visitor
    # data and acreage should not be combined.
    if park_name.lower().find('john d. rockefeller') > -1: park_code = 'xxx1'

    # World War II Valor in the Pacific National Monument split into
    # three parks in 3/2019 - Pearl Harbor National Memorial (HI)
    # (maintains the valr code), Aleutian Islands World War II National
    # Monument (AK), and Tule Lake National Monument (CA)(tule). Tule
    # Lake is on the list of official park units, Aleutian Islands is
    # under 'Related Areas' and not on the official list.
    if park_name.lower().find('valor') > -1: park_code = 'valr'

    # The National World War I Memorial is a part of the National Mall
    # and Memorial Parks (DC).
    if park_name.lower() == "world war i memorial": park_code = 'nama'
    if park_name.lower().startswith("world war i "): park_code = 'nama'

    return park_code

def read_wikipedia_data(df_api):
    '''
    This function reads the park name and date established from the
    Excel file created by the nps_get_wikipedia.py script, looks up
    the correct park code in the paramter dataframe and returns a
    dataframe containing the park code and date established. The date
    established is currently only available for National Parks.

    Parameters
    ----------
    df_api : pandas DataFrame
        Dataframe for park code lookup.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park code and date established.
    '''

    filename = '_reference_data/wikipedia_date_established.csv'
    df = pd.read_csv(filename, header=0)

    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    # Lookup the correct park code for the park name.
    df['park_code'] = df.park_name_stripped.apply(
                      lambda x: lookup_park_code(x, df_api))

    # Remove Seqoia and Kings Canyon NPs from the dataframe. They share
    # the same park code but have different established dates which will
    # be assigned after merge.
    df = df[df.park_code != 'seki']

    df.date_established = pd.to_datetime(df.date_established)

    return df[['park_code', 'date_established']]

def read_acreage_data(df_api):
    '''
    This function reads the park size data from a report downloaded from
    nps.gov, looks up the correct park code for each park in the
    parameter dataframe and returns a dataframe containing the park code
    and park size in acres.

    Parameters
    ----------
    df_api : pandas DataFrame
        Dataframe for park code lookup.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park code and park size.
    '''

    filename = '_acreage_data/NPS-Acreage-12-31-2018.xlsx'
    df = pd.read_excel(filename, skiprows=1)
    df = df[pd.notnull(df['State'])]
    df = df.rename({'Gross Area Acres': 'gross_area_acres',
                    'Area Name': 'park_name'}, axis='columns')

    # Make some park name replacements to make matching the park name
    # to the df_api dataframe to find the park code work correctly.
    df['park_name'].replace(
        {"C & O":"Chesapeake & Ohio",
         "FDR":"Franklin Delano Roosevelt",
         "FRED-SPOTS":"Fredericksburg & Spotsylvania",
         "FT SUMTER":"Fort Sumter and Fort Moultrie",
         "JDROCKEFELLER":"John D. Rockefeller",
         "NATIONAL MALL":"National Mall and Memorial Parks",
         "OCMULGEE":"Ocmulgee Mounds",
         "RECONSTRUCTION ERA NM":"RECONSTRUCTION ERA NHP",
         "SALT RVR BAY NHP":
             "Salt River Bay National Historical Park and Ecological Preserve",
         "T ROOSEVELT":"Theodore Roosevelt",
         "WWII":"World War II",
         " NHP":" National Historical Park",
         " NHS":" National Historical Site",
         " NMP":" National Military Park",
         " NRA":" National Recreation Area",
         " NSR":" National Scenic River",
         " NS RIVERWAYS":" National Scenic Riverways",
         " NS TRAIL":" National Scenic Trail",
         " NS":" National Seashore",
         " RVR ":" River "},
        regex=True, inplace=True)

    df['park_name_stripped'] = df.park_name.apply(
                                   lambda x: strip_park_name(x))

    # Lookup the correct park code for the park name.
    df['park_code'] = df.park_name_stripped.apply(
                      lambda x: lookup_park_code(x, df_api))

    # Sum acreage data for parks with the same park code.
    df = df.groupby(['park_code'], as_index=False).sum()

    return df[['park_code', 'gross_area_acres']]

def read_visitor_data(df_api):
    '''
    This function reads the park visitor data from a report downloaded
    from nps.gov, and saved in an Excel file by the
    nps_read_visitor_data.py script, into a dataframe. It then looks up
    the correct park code for each park in the parameter dataframe and
    returns a dataframe containing the park code and park visits per
    year for the years 1904 - 2018.

    Parameters
    ----------
    df_api : pandas DataFrame
        Dataframe for park code lookup.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park code and visits per year.
    '''

    filename = '_visitor_data/annual_visitors_by_park_1904_2018.xlsx'
    df = pd.read_excel(filename)

    # Exclude certain parks not in the list of 419.
    exclude_list = ["John F. Kennedy Center For Pa", "National Visitor Center",
                    "Klondike Gold Rush NHP Seattle", "Oklahoma City NMEM"]
    df = df[~(df.park_name.isin(exclude_list))]

    # Make some park name replacements to make matching the park name
    # to the df_api dataframe to find the park code work correctly.
    df['park_name'].replace(
        {"Fort Sumter":"Fort Sumter and Fort Moultrie",
         "Longfellow":"Longfellow House Washington's Headquarters",
         "Ocmulgee":"Ocmulgee Mounds",
         "President's Park":"President's Park (White House)",
         " EHP":"Ecological & Historic Preserve",
         " NHP":" National Historical Park",
         " NHS":" National Historical Site",
         " NMEM":" National Memorial",
         " NMP":" National Military Park",
         " NRA":" National Recreation Area",
         " NSR":" National Scenic River",
         " NS":" National Seashore"},
        regex=True, inplace=True)

    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    # Lookup the correct park code for the park name.
    df['park_code'] = df.park_name_stripped.apply(
                      lambda x: lookup_park_code(x, df_api))

    df.drop(columns=['park_name', 'park_name_stripped'], inplace=True)

    # Sum visitor data for parks with the same park code.
    df = df.groupby(['park_code'], as_index=False).sum()

    return df

def print_debug(df1_name, df1, df2_name, df2):
    '''
    Print some debug information.
    '''

    print("**** DEBUG: {} and {} ****".format(df1_name, df2_name))
    print("-- {}: {}".format(df1_name, df1.shape))
    print("-- {}: {}\n".format(df2_name, df2.shape))
    print("-- {} dupes: ".format(df1_name))
    df1_dupes = (df1[df1.duplicated(['park_code'], keep=False)]
                .sort_values(by=['park_code']))
    print(df1_dupes,"\n")
    print("-- {} dupes: ".format(df2_name))
    df2_dupes = (df2[df2.duplicated(['park_code'], keep=False)]
                .sort_values(by=['park_code']))
    print(df2_dupes,"\n")
    print("-- Park codes in {}, but not in {}:".format(df1_name, df2_name))
    df1_not_in_df2 = set(sorted((x for x in list(df1.park_code)
                     if x not in list(df2.park_code))))
    print(df1_not_in_df2)
    print("Length: {}\n".format(len(df1_not_in_df2)))
    print("-- Park codes in {}, not in {}:".format(df2_name, df1_name))
    df2_not_in_df1 = set(sorted((x for x in list(df2.park_code)
                     if x not in list(df1.park_code))))
    print(df2_not_in_df1)
    print("Length: {}\n".format(len(df2_not_in_df1)))

def main():
    pd.set_option('display.max_rows', 1000)
    debug = True

    # Read the NPS API data from file into a dataframe.
    df_api = read_park_sites_api()

    # Read the nps.gov National Park System Unit/Park list data from
    # file into a dataframe and merge it with the nps api dataframe.
    df_master = read_park_sites_web(df_api)
    if debug: print_debug('df_master', df_master, 'df_api', df_api)
    df_master = pd.merge(df_master[['park_name', 'park_code', 'designation']],
                         df_api[['park_code', 'states', 'lat', 'long']],
                         how='left', on='park_code')

    # Read the Wikipedia national park date established data from file
    # into a dataframe and merge it with the master dataframe.
    df_estab = read_wikipedia_data(df_api)
    df_master = pd.merge(df_master, df_estab, how='left', on='park_code')

    # Kings Canyon and Sequoia National Parks share the same park code
    # but were established on separate dates. Assign these dates.
    df_master.loc[df_master.park_name == "Kings Canyon National Park", 'date_established'] = pd.to_datetime('1940-03-04')
    df_master.loc[df_master.park_name == "Sequoia National Park", 'date_established'] = pd.to_datetime('1890-09-25')

    # Read the NPS Acreage report data from file into a dataframe and
    # merge it with the master dataframe.
    df_acreage = read_acreage_data(df_api)
    if debug: print_debug('df_master', df_master, 'df_acreage', df_acreage)
    df_master = pd.merge(df_master, df_acreage, how='left', on='park_code')

    # Read the NPS Visitor Use Statistics report from file into a
    # dataframe and merge it with the master dataframe.
    df_visitor = read_visitor_data(df_api)
    if debug: print_debug('df_master', df_master, 'df_visitor', df_visitor)
    df_master = pd.merge(df_master, df_visitor, how='left', on='park_code')

    # Sort and save the master dataframe to an Excel file.
    df_master = df_master.sort_values(by=['park_name']).reset_index(drop=True)
    df_master.to_excel('nps_parks_master_df.xlsx')

if __name__ == '__main__':
    main()
