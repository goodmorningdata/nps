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
3) Read significant park dates from a manually created file and merge
   with the master dataframe.
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
3) Run the script, nps_get_wikipedia_presidents.py, to create the file,
   'wikipedia_list_of_presidents.csv'.
4) Download the most recent acreage report from the nps website at:
   https://www.nps.gov/subjects/lwcf/acreagereports.htm Calendar
   Year Reports, Year = 2018. Place this file in the '_acreage_data'
   directory of this project.
5) Run the script, nps_read_visitor_data.py to create the file:
   annual_visitors_by_park_1904_2018.xlsx.
'''

import pandas as pd
from difflib import SequenceMatcher

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
                          'juba', 'keaq', 'klse', 'lecl', 'loea',
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

    df = df.sort_values(by=['park_name'])

    return df[['park_code', 'park_name', 'states', 'lat', 'long']]

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
    df.loc[df.park_name == "Martin Luther King", 'park_name'] = (
        "Martin Luther King National Historic Park")

    # Replace name to provide more information.
    df['park_name'].replace(
        {"John D. Rockefeller":"John D. Rockefeller National Parkway"},
        regex=True, inplace=True)

    # Find the park code for each park in the df_master dataframe by
    # matching it to the park in the df_api dataframe.
    df['park_code'] = df.park_name.apply(
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
    df['name_match'] = df['park_name'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       park_name.lower()).ratio())

    park_code = df.loc[df['name_match'].idxmax()].park_code

    # Name matching does not work for these so assign directly.
    if park_name.lower().find('katmai') > -1: park_code = 'katm'
    if park_name.lower().find('glacier bay') > -1: park_code = 'glba'
    if park_name.lower().find('denali') > -1: park_code = 'dena'
    if park_name.lower().find('aniakchak') > -1: park_code = 'ania'

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
    # and Memorial Parks (DC), but it is listed separately on the web
    # list.
    if park_name.lower() == "world war i memorial": park_code = 'xxx2'
    if park_name.lower().startswith("world war i "): park_code = 'xxx2'

    return park_code

def read_park_dates(df_api):
    '''
    This function reads an Excel file of park dates - date of park
    creation, date of national monument creation, and date of national
    park creation into a dataframe and looks up the correct park code
    for each park.

    Parameters
    ----------
    df_api : pandas DataFrame
        Dataframe of data from api in which to lookup park code.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park dates.
    '''

    filename = '_reference_data/nps_park_dates.xlsx'
    df = pd.read_excel(filename, header=1)
    df.entry_date = pd.to_datetime(df.entry_date, errors='coerce')
    df.nm_date = pd.to_datetime(df.nm_date, errors='coerce')
    df.np_date = pd.to_datetime(df.np_date, errors='coerce')

    return df[['park_name', 'entry_date', 'nm_date', 'np_date']]

def read_wikipedia_list_of_presidents():
    '''
    This function reads president name and start and end term dates
    from the Excel file created by the nps_get_wikipedia_data.py script,
    and adds them to a dataframe.

    Parameters
    ----------
    None

    Returns
    -------
    df : pandas DataFrame
        Dataframe of president name and term dates.
    '''

    filename = '_reference_data/wikipedia_list_of_presidents.csv'
    df_pres = pd.read_csv(filename, header=0)
    df_pres.start_date = pd.to_datetime(df_pres.start_date)
    df_pres.end_date = pd.to_datetime(df_pres.end_date)

    return df_pres

def assign_president(date, df_pres):
    '''
    This function finds the president in office on the parameter date.

    Parameters
    ----------
    date : datetime
        Date for which to find president in office for.
    df_pres : pandas DataFrame
        Dataframe of president term start and end dates.

    Returns
    -------
    president_name : str
        President name.
    president_end_date : datetime
        End date of president's term.
    '''

    if pd.isnull(date):
        president_name = ''
        president_end_date = ''
    else:
        president_row = (df_pres[(df_pres.start_date <= date)
                         & (df_pres.end_date > date)])
        president_name = president_row.president.tolist()[0]
        president_end_date = pd.to_datetime(president_row.end_date.tolist()[0])
        if president_name == 'Grover Cleveland':
            president_end_date = pd.to_datetime('1889-03-04')

    return [president_name, president_end_date]

def lookup_park_name(park_name, df_master):
    '''
    Find the park name in the master dataframe that best matches the
    parameter park name.

    Parameters
    ----------
    park_name : str
        Park name to find a match for.
    df_master : pandas DataFrame
        Dataframe for park name lookup.

    Returns
    -------
    best_match : str
        Park name that best matches the parameter.
    '''

    df = df_master
    df['name_match'] = df['park_name'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       park_name.lower()).ratio())

    best_match = df.loc[df['name_match'].idxmax()].park_name

    return best_match

def read_acreage_data(df_master):
    '''
    This function reads the park size data from a report downloaded from
    nps.gov, looks up the matching park name for each park in the
    master dataframe, and returns a dataframe containing the park name
    and park size in acres, square miles, and square meters.

    Parameters
    ----------
    df_master : pandas DataFrame
        Dataframe for park name lookup.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park code and park size.
    '''

    filename = '_reference_data/NPS-Acreage-12-31-2018.xlsx'
    df = pd.read_excel(filename, skiprows=1)
    df = df[pd.notnull(df['State'])]
    df = df.rename({'Gross Area Acres': 'gross_area_acres',
                    'Area Name': 'park_name'}, axis='columns')

    # Updates to make park name matching work correctly.
    df['park_name'].replace(
        {"C & O":"Chesapeake & Ohio",
         "ARL HOUSE, R E LEE MEM":"Arlington House",
         "FRED-SPOTS":"Fredericksburg and Spotsylvania",
         "FT SUMTER":"Fort Sumter and Fort Moultrie",
         "SALT RVR BAY NHP":("Salt River Bay National Historical Park and " "Ecological Preserve"),
         "T ROOSEVELT NP":"Theodore Roosevelt National Park",
         "RECONSTRUCTION ERA NM":"Reconstruction Era National Historical Park",
         "NATIONAL MALL":"National Mall and Memorial Parks",
         "NATIONAL WWII MEMORIAL":"World War II Memorial",
         "CORAL REEF":"Coral Reef National Monument",
         "WWII VALOR IN THE PACIFIC NM":"Pearl Harbor National Memorial",
         "FDR":"Franklin Delano Roosevelt",
         " NRA":" National Recreation Area",
         " NHS":" National Historic Site",
         " NHP":" National Historic Park",
         " NSR":" National Scenic Riverway",
         " NMP":" National Military Park"},
        regex=True, inplace=True
    )

    # Look up the matching park name in the master dataframe.
    df['park_name'] = df.park_name.apply(
                      lambda x: lookup_park_name(x, df_master))

    # Add square miles and square meters columns for reporting.
    df = df[['park_name', 'gross_area_acres']]
    df['gross_area_square_miles'] = df.gross_area_acres * 0.0015625
    df['gross_area_square_meters'] = df.gross_area_acres * 4046.86

    # Sum acreage data for parks with the same park name.
    df = df.groupby(['park_name'], as_index=False).sum()

    return df

def read_visitor_data(df_master):
    '''
    This function reads the park visitor data from a report downloaded
    from nps.gov, looks up the matching park name for each park in the
    master dataframe, and returns a dataframe containing the park name
    and park visits per year for the years 1904 - 2018.

    Parameters
    ----------
    df_master : pandas DataFrame
        Dataframe for park name lookup.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park code and visits per year.
    '''

    filename = '_reference_data/annual_visitors_by_park_1904_2018.xlsx'
    df = pd.read_excel(filename)

    # Exclude certain parks not in the list of 419.
    exclude_list = ["John F. Kennedy Center For Pa", "National Visitor Center",
                    "Klondike Gold Rush NHP Seattle", "Oklahoma City NMEM"]
    df = df[~(df.park_name.isin(exclude_list))]

    # Make some park name replacements to make matching the park name
    # to the df_api dataframe to find the park code work correctly.
    df['park_name'].replace(
        {"NP & PRES":"National Park",
         "Fort Sumter":"Fort Sumter and Fort Moultrie",
         "Longfellow":"Longfellow House - Washington's Headquarters",
         "President's Park":"White House",
         "Theodore Roosevelt NP":"Theodore Roosevelt National Park",
         "World War II Valor in the Pacific":"Pearl Harbor",
         "Whiskeytown":"Whiskeytown-Shasta-Trinity",
         " NHP":" National Historical Park",
         " NHS":" National Historical Site",
         " NMP":" National Military Park",
         " NRA":" National Recreation Area"},
        regex=True, inplace=True
    )

    # Look up the matching park name in the master dataframe.
    df['park_name'] = df.park_name.apply(
                      lambda x: lookup_park_name(x, df_master))

    # Sum visitor data for parks with the same park name.
    df = df.groupby(['park_name'], as_index=False).sum()

    return df

def print_debug(df1_name, df1, df2_name, df2, join_type):
    '''
    Print some debug information.
    '''

    print("**** DEBUG: {} and {} ****".format(df1_name, df2_name))
    print("-- {}: {}".format(df1_name, df1.shape))
    print("-- {}: {}\n".format(df2_name, df2.shape))
    print("-- {} dupes, join type: {}: ".format(df1_name, join_type))
    if join_type == 'park_code':
        df1_dupes = (df1[df1.duplicated(['park_code'], keep=False)]
                    .sort_values(by=['park_code']))
    else:
        df1_dupes = (df1[df1.duplicated(['park_name'], keep=False)]
                    .sort_values(by=['park_name']))
    print(df1_dupes,"\n")

    print("-- {} dupes, join_type: {}: ".format(df2_name, join_type))
    if join_type == 'park_code':
        df2_dupes = (df2[df2.duplicated(['park_code'], keep=False)]
                    .sort_values(by=['park_code']))
    else:
        df2_dupes = (df2[df2.duplicated(['park_name'], keep=False)]
                    .sort_values(by=['park_name']))
    print(df2_dupes,"\n")

    print("-- Parks in {}, but not in {}:".format(df1_name, df2_name))
    if join_type == 'park_code':
        df1_not_in_df2 = set(sorted((x for x in list(df1.park_code)
                         if x not in list(df2.park_code))))
    else:
        df1_not_in_df2 = set(sorted((x for x in list(df1.park_name)
                         if x not in list(df2.park_name))))
    print(df1_not_in_df2)
    print("Length: {}\n".format(len(df1_not_in_df2)))

    print("-- Parks in {}, not in {}:".format(df2_name, df1_name))
    if join_type == 'park_code':
        df2_not_in_df1 = set(sorted((x for x in list(df2.park_code)
                         if x not in list(df1.park_code))))
    else:
        df2_not_in_df1 = set(sorted((x for x in list(df2.park_name)
                         if x not in list(df1.park_name))))
    print(df2_not_in_df1)
    print("Length: {}\n".format(len(df2_not_in_df1)))

def main():
    pd.set_option('display.max_rows', 1000)
    debug = True

    # Read the NPS API data from file into a dataframe.
    df_api = read_park_sites_api()

    # Merge the nps.gov NPS Unit/Park list with the NPS API dataframe.
    df_master = read_park_sites_web(df_api)
    if debug: print_debug('df_master', df_master, 'df_api', df_api, 'park_code')
    df_master = pd.merge(df_master[['park_name', 'park_code', 'designation']],
                         df_api[['park_code', 'states', 'lat', 'long']],
                         how='left', on='park_code')

    # Assign states to two parks not available through API.
    df_master.loc[df_master.park_name ==
        "John D. Rockefeller National Parkway", 'states'] = 'WY'
    df_master.loc[df_master.park_name ==
        "World War I Memorial", 'states'] = 'DC'

    # Read manually created Excel file to get park dates.
    df_dates = read_park_dates(df_api)
    df_master = pd.merge(df_master, df_dates, how='left', on='park_name')

    # Read list of presidents and term start and end dates.
    df_pres = read_wikipedia_list_of_presidents()

    # Assign president at time of park creation.
    df_master[['president', 'president_end_date']] = df_master.apply(
        lambda row: pd.Series(assign_president(row.entry_date, df_pres)),
        axis=1
    )

    # Assign president at time of National Monument creation.
    df_master[['president_nm', 'president_nm_end_date']] = df_master.apply(
        lambda row: pd.Series(assign_president(row.nm_date, df_pres)),
        axis=1
    )

    # Assign president at time of National Park creation.
    df_master[['president_np', 'president_np_end_date']] = df_master.apply(
        lambda row: pd.Series(assign_president(row.np_date, df_pres)),
        axis=1
    )

    # Add the NPS Acreage report data to the master df.
    df_acreage = read_acreage_data(df_master)
    if debug: print_debug('df_master', df_master, 'df_acreage', df_acreage, 'park_name')
    df_master = pd.merge(df_master, df_acreage, how='left', on='park_name')

    # Add the NPS Visitor Use Statistics report data to the master df.
    df_visitor = read_visitor_data(df_master)
    if debug: print_debug('df_master', df_master, 'df_visitor', df_visitor, 'park_name')
    df_master = pd.merge(df_master, df_visitor, how='left', on='park_name')

    # Sort and save the master dataframe to an Excel file.
    df_master = df_master.sort_values(by=['park_name']).reset_index(drop=True)
    df_master.to_excel('nps_parks_master_df.xlsx')

if __name__ == '__main__':
    main()
