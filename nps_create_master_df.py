''' Create master dataframe of National Park Service site data.

This script creates a dataframe of all data collected by this project
about the NPS official units.
1. Read the data available from the api. This source provides the four
   character code that uniquely identifies each park, the list of state
   codes the park is in, and the latitude and longitiude of the park.
2. Merge the api data with the list of official park units available
   on nps.gov. This source provides the official list of units, the park
   name, and park designation.

Required libraries: pandas, SequenceMatcher

Dependencies:
    * Run the script, nps_get_park_sites_web.py, to create the file,
      'nps_park_sites_web.xlsx'.
    * Run the script, nps_get_park_sites_api.py, to create the file,
      'nps_park_sites_api.xlsx'.
    * Run the script, nps_get_wikipedia_data.py, to create the file,
      'wikipedia_date_established.xlsx'.
    * Download the most recent acreage report from the nps website at:
      https://www.nps.gov/subjects/lwcf/acreagereports.htm Calendar
      Year Reports, Year = 2018. Place this file in the '_acreage_data'
      directory of this project.
    * Run the script, nps_read_visitor_data.py to create the file:
      annual_visitors_by_park_1904_2018.xlsx.
'''

import pandas as pd
from difflib import SequenceMatcher

def strip_park_name(park_name):
    ''' Strip unnecessary text from park name.

    Park names for the same park may be slightly different between
    sources, making matching them difficult. This function strips
    designation from the park name to improve the chance of matching.

    Parameters
    ----------
    park_name : str : Park name to strip of designations.

    Returns
    -------
    park_name : str : Stripped park name.
    '''

    # designation_start = park_name.lower().find('national')
    # if designation_start > 0:
    #     park_name = park_name[:designation_start]
    #
    # designation_start = park_name.lower().find('memorial')
    # if designation_start > 0:
    #     park_name = (park_name.replace('Memorial', '')
    #                           .replace('MEMORIAL', ''))
    #
    # park_name = (park_name.replace('N RVR & RA','')
    #                       .replace('N REC RIVER','')
    #                       .replace('N. SCENIC RIVER','')
    #                       .replace('N PRESERVE','')
    #                       .replace('NS RIVERWAYS','')
    #                       .replace('NM of America','')
    #                       .replace('Ecological & Historic Preserve',''))

    return park_name.rstrip()

def read_park_sites_api():
    ''' Read list of park sites from the NPS API source.

    Read the list of park sites and associated data pulled from the
    NPS API and saved in an Excel file by the nps_get_park_sites_api.py
    script into a dataframe.

    Parameters
    ----------
    None

    Returns
    -------
    df : pandas DataFrame : Dataframe of park site data.
    '''

    filename = '_reference_data/nps_park_sites_api.xlsx'
    df = pd.read_excel(filename, header=0)

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
                          'noco', 'oire', 'okci', 'olsp', 'oreg', 'ovvi', 'oxhi', 'para', 'poex', 'prsf', 'rist', 'roca',
                          'safe', 'scrv', 'semo', 'shvb', 'soca', 'tecw',
                          'qush', 'thco', 'tosy', 'trte', 'waro', 'whee',
                          'wing', 'york']
    print(df.shape)
    df = df[~(df.park_name in exclude_park_codes)]
    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))
    print(df.shape)

    return df[['park_code', 'park_name', 'park_name_stripped',
               'states', 'lat', 'long']]

def read_park_sites_web(df_api):
    ''' Read list of park sites from the nps.gov web source.

    Read the list of park sites extracted from nps.gov and saved
    in an Excel file by the nps_get_park_sites_web.py script into a
    dataframe.

    Parameters
    ----------
    None

    Returns
    -------
    df : pandas DataFrame : Dataframe of park site data.
    '''

    filename = '_reference_data/nps_park_sites_web.xlsx'
    df = pd.read_excel(filename, header=0)

    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    # Find the park code for each park in the df_master dataframe by
    # matching it to the park in the df_api dataframe.
    df['park_code'] = df.park_name_stripped.apply(
                      lambda x: lookup_park_code(x, df_api))

    return df

def lookup_park_code(park_name, df_lookup):
    ''' Look up the park code for a park using the park name.

    Each park is assigned a four character park code that uniquely
    identifies it. The park code for each park is available from the
    NPS API. This function accepts a park name and returns the park code
    after looking in up in the API dataframe.

    Future work: This can be done in a more elegant manner.

    Parameters
    ----------
    park_name : str : Park name to lookup the code for.
    df_lookup : pandas DataFrame : Dataframe of park names and codes.

    Returns
    -------
    df : pandas DataFrame : Dataframe of park site data.
    '''

    df = df_lookup

    # Use SequenceMatcher to comapre the stripped park names and find
    # the best match.
    df['name_match'] = df['park_name_stripped'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       park_name.lower()).ratio())
    park_code = df.loc[df['name_match'].idxmax()].park_code
    pd.set_option('display.max_rows', 1000)

    # The park names for the following parks differ so greatly from the
    # name to match to or are so similar to another park name, that they
    # must be assigned directly.
    # if park_name.lower() == "arlington house": park_code = 'arho'
    # if park_name.lower() in ["kings canyon", "sequoia"]: park_code = 'seki'
    # if park_name.lower() == "white house" : park_code = 'whho'
    # if park_name.lower() == "fdr": park_code = 'frde'
    # if park_name.lower() == "gateway nra": park_code = 'gate'
    # if park_name.lower() == "g w": park_code = 'gwmp'
    # if park_name.lower() == "martin l king, jr, nhp": park_code = 'malu'
    # if park_name.lower() == "martin luther king, jr. nhp": park_code = 'malu'
    # if park_name.lower() == "t roosevelt np": park_code = 'thro'
    # if park_name.lower().startswith("fred-spots"): park_code = 'frsp'
    # if park_name.lower().startswith("lbj"): park_code = 'lyba'
    # if park_name.lower().endswith("wwii"): park_code = 'wwii'
    # if park_name.lower().find("sumter") > -1: park_code = 'fosu'
    # if park_name.lower().find("longfellow") > -1: park_code = 'long'
    #
    # # These are the parks with no code found in the API.
    # if park_name.lower().find('caroline') > -1: park_code = 'xxx1'
    # if (park_name.lower().find('john d. rockefeller') > -1 or
    #     park_name.lower().find('jdrockefeller') > -1): park_code = 'xxx2'
    # if park_name.lower().find('chelan') > -1: park_code = 'xxx3'
    # if park_name.lower().find('ross lake') > -1: park_code = 'xxx4'
    # if park_name.lower().find('valor') > -1: park_code = 'xxx5'
    # if park_name.lower().find('world war i ') > -1: park_code = 'xxx6'
    # if park_name.lower() == "world war i": park_code = 'xxx6'
    # if park_name.lower() == "john f. kennedy center for pa": park_code = 'xxx7'
    #
    # # Stripping park name does not work for all data sets for National
    # # Park of American Samoa, so assign directly.
    # if park_name.lower().find('samoa') > -1: park_code = 'npsa'

    return park_code

def read_wikipedia_data(df_api):
    ''' Read park established date from file.

    This function reads the park name and date established from the
    Excel file created by the nps_get_wikipedia.py script, looks up
    the correct park code in the paramter dataframe and returns a
    dataframe containing the park code and date established. This date
    established is currently only available for National Parks.

    Parameters
    ----------
    df_api : pandas DataFrame : Dataframe for park code lookup.

    Returns
    -------
    df : pandas DataFrame : Dataframe of park code and date established.
    '''

    filename = '_reference_data/wikipedia_date_established.xlsx'
    df = pd.read_excel(filename, header=0)

    df['park_name_stripped'] = df.park_name.apply(
                                   lambda x: strip_park_name(x))

    df['park_code'] = df.park_name_stripped.apply(
                         lambda x: lookup_park_code(x, df_api))

    return df[['park_code', 'date_established']]

def read_acreage_data(df_api):
    '''
    '''

    filename = '_acreage_data/NPS-Acreage-12-31-2018.xlsx'
    df = pd.read_excel(filename, skiprows=1)
    df = df[pd.notnull(df['State'])]
    df = df.rename({'Gross Area Acres': 'gross_area_acres',
                    'Area Name': 'park_name'}, axis='columns')

    df['park_name_stripped'] = df.park_name.apply(
                                   lambda x: strip_park_name(x))

    df['park_code'] = df.park_name_stripped.apply(
                         lambda x: lookup_park_code(x, df_api))

    df = df.groupby(['park_code'], as_index=False).sum()

    return df[['park_code', 'gross_area_acres']]

def read_visitor_data(df_api):
    '''
    '''

    filename = '_visitor_data/annual_visitors_by_park_1904_2018.xlsx'
    df = pd.read_excel(filename)

    df['park_name_stripped'] = df.park_name.apply(
                                   lambda x: strip_park_name(x))

    df['park_code'] = df.park_name_stripped.apply(
                         lambda x: lookup_park_code(x, df_api))

    df.drop(columns=['park_name', 'park_name_stripped'], inplace=True)

    df = df.groupby(['park_code'], as_index=False).sum()

    return df

def main():
    pd.set_option('display.max_rows', 1000)

    # Read in the list of nps sites from the nps api into a dataframe.
    df_api = read_park_sites_api()

    # Read in the list of nps sites from nps.gov into a dataframe.
    #df_master = read_park_sites_web(df_api)

    # Merge the nps.gov and nps api dataframes.
    #df_master = pd.merge(df_master[['park_name', 'park_code', 'designation']],
#                         df_api[['park_code', 'states', 'lat', 'long']],
#                         how='left', on='park_code')

    # Read in the date established data from Wikipedia into a
    # dataframe. This data is currently only available for National
    # Parks. Merge this dataframe with the master dataframe.
    #df_estab = read_wikipedia_data(df_api)
    #df_master = pd.merge(df_master, df_estab, how='left', on='park_code')

    # Read in the park size data from the NPS acreage report downloaded
    # from nps.gov.
    #df_acreage = read_acreage_data(df_api)
    #df_master = pd.merge(df_master, df_acreage, how='left', on='park_code')

    # Read in the park visitation data from the NPS Annual Summary
    # Report downloaded from nps.gov.
    #df_visitor = read_visitor_data(df_api)
    #df_master = pd.merge(df_master, df_visitor, how='left', on='park_code')

    # Sort and save the master dataframe to an Excel file.
    #df_master = df_master.sort_values(by=['park_name']).reset_index(drop=True)

    #print("*** DF Master Dupes")
    #print(df_master[df_master.duplicated(['park_code'], keep=False)])

    #df_master.to_excel('nps_parks_master_df.xlsx')

if __name__ == '__main__':
    main()
