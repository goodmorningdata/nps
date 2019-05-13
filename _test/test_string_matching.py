from Levenshtein import distance
from difflib import SequenceMatcher
import pandas as pd

def strip_park_name(park_name):
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
    filename = '../_reference_data/nps_park_sites_api.xlsx'
    df = pd.read_excel(filename, header=0)

    exclude_park_codes = ['afam', 'alka', 'anch', 'alca', 'aleu', 'amme',
                          'anac', 'armo', 'attr', 'auca', 'balt', 'bawa',
                          'blrn', 'cali', 'crha', 'came', 'cahi', 'cajo',
                          'chva', 'cbpo', 'cbgn', 'cwdw', 'coal', 'colt',
                          'xrds', 'dabe', 'dele', 'elte', 'elca', 'elis',
                          'erie', 'esse', 'fati', 'fodu', 'fofo', 'glec',
                          'glde', 'grfa', 'grsp', 'guge', 'haha', 'jame',
                          'hurv', 'inup', 'iafl', 'iatr', 'blac', 'jthg',
                          'juba', 'keaq', 'klse', 'lecl', 'loea', 'maac',
                          'mide', 'migu', 'mihi', 'mopi', 'auto', 'mush',
                          'avia', 'npnh', 'neen', 'pine', 'nifa', 'noco',
                          'oire', 'okci', 'olsp', 'oreg', 'ovvi', 'oxhi',
                          'para', 'poex', 'prsf', 'rist', 'roca', 'safe',
                          'scrv', 'semo', 'shvb', 'soca', 'tecw', 'qush',
                          'thco', 'tosy', 'trte', 'waro', 'whee', 'wing',
                          'york']
    df = df[~(df.park_code.isin(exclude_park_codes))]

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

def lookup_park_code(park_name, df_lookup):
    df = df_lookup

    print("** In lookup_park_code")
    print("park_name = {}".format(park_name))

    # Use SequenceMatcher to find the best park name match.
    df['name_match'] = df['park_name_stripped'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       park_name.lower()).ratio())
    park_code = df.loc[df['name_match'].idxmax()].park_code

    if park_name.lower().find('kings canyon') > -1: park_code = 'seki'
    if park_name.lower().find('sequoia') > -1: park_code = 'seki'

    # These are the parks with no code found in the API.
    if park_name.lower().find('caroline') > -1: park_code = 'xxx1'
    if park_name.lower().find('john d. rockefeller') > -1: park_code = 'xxx2'
    if park_name.lower().find('chelan') > -1: park_code = 'xxx3'
    if park_name.lower().find('ross lake') > -1: park_code = 'xxx4'
    if park_name.lower().find('valor') > -1: park_code = 'xxx5'
    if park_name.lower() == "world war i memorial": park_code = 'xxx6'
    if park_name.lower().startswith("world war i "): park_code = 'xxx6'

    print(df.sort_values(by=['name_match']))

    return park_code

def main():
    df_lookup = read_park_sites_api()
    pd.set_option('display.max_rows', 1000)
    #print(df_lookup)

    print('**** Matching')
    to_match = "Oklahoma City NMEM"
    print('Park Name: ', to_match)

    # Mimics fixes to visitor dataframe.
    to_match = (
        to_match.replace("Fort Sumter", "Fort Sumter and Fort Moultrie")
                .replace("Longfellow",
                         "Longfellow House Washington's Headquarters")
                .replace("Ocmulgee", "Ocmulgee Mounds")
                .replace("President's Park", "President's Park (White House)")
                .replace(" EHP", "Ecological & Historic Preserve")
                .replace(" NHP", " National Historical Park")
                .replace(" NHS", " National Historical Site")
                .replace(" NMEM", " National Memorial")
                .replace(" NMP", " National Military Park")
                .replace(" NRA", " National Recreation Area")
                .replace(" NSR", " National Scenic River")
                .replace(" NS", " National Seashore"))

    # Mimics fixes to acreage dataframe.
    # to_match = (to_match.replace("C & O", "Chesapeake & Ohio")
    #     .replace("FDR","Franklin Delano Roosevelt")
    #     .replace("FRED-SPOTS","Fredericksburg & Spotsylvania")
    #     .replace("FT SUMTER", "Fort Sumter and Fort Moultrie")
    #     .replace("JDROCKEFELLER", "John D. Rockefeller")
    #     .replace("NATIONAL MALL", "National Mall and Memorial Parks")
    #     .replace("OCMULGEE", "Ocmulgee Mounds")
    #     .replace("RECONSTRUCTION ERA NM", "RECONSTRUCTION ERA NHP")
    #     .replace("SALT RVR BAY NHP",
    #         "Salt River Bay National Historical Park and Ecological Preserve")
    #     .replace("T ROOSEVELT", "Theodore Roosevelt")
    #     .replace("WWII", "World War II")
    #     .replace(" NHP", " National Historical Park ")
    #     .replace(" NHS", " National Historic Site ")
    #     .replace(" NMP", " National Military Park")
    #     .replace(" NRA", "National Recreation Area")
    #     .replace(" NSR", " National Scenic River")
    #     .replace(" NS RIVERWAYS", " National Scenic Riverways")
    #     .replace(" NS TRAIL", " National Scenic Trail")
    #     .replace(" NS", " National Seashore")
    #     .replace(" RVR ", " River "))

    park_name = strip_park_name(to_match)
    print('Stripped Park Name: ', park_name)

    code = lookup_park_code(park_name, df_lookup)
    print('Actual Match: {}'.format(code))

if __name__ == '__main__':
    main()
