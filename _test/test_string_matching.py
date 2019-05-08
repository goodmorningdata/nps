from Levenshtein import distance
from difflib import SequenceMatcher
import pandas as pd

def strip_park_name(park_name):
    designation_start = park_name.lower().find('national')
    if designation_start > 0:
        park_name = park_name[:designation_start]

    designation_start = park_name.lower().find('memorial')
    if designation_start > 0:
        park_name = (park_name.replace('Memorial', '')
                              .replace('MEMORIAL', ''))

    park_name = (park_name.replace('N RVR & RA','')
                          .replace('N REC RIVER','')
                          .replace('N. SCENIC RIVER','')
                          .replace('N PRESERVE','')
                          .replace('NS RIVERWAYS','')
                          .replace('NM of America','')
                          .replace('Ecological & Historic Preserve','')
                          .replace('Ecological and Historic Preserve',''))

    return park_name.rstrip()

def read_park_sites_api():
    filename = '../_reference_data/nps_park_sites_api.xlsx'
    df = pd.read_excel(filename, header=0)
    pd.set_option('display.max_rows', 1000)
    df = df.sort_values(by=['park_name'])

    df['park_name_stripped'] = df.park_name.apply(
                               lambda x: strip_park_name(x))

    return df[['park_code', 'park_name', 'park_name_stripped']]

def lookup_park_code(park_name, df_lookup):
    df = df_lookup

    # Use SequenceMatcher to comapre the stripped park names and find
    # the best match.
    df['name_match'] = df['park_name_stripped'].apply(
                       lambda x: SequenceMatcher(None, x.lower(),
                       park_name.lower()).ratio())
    park_code = df.loc[df['name_match'].idxmax()].park_code
    print(df)

    # The park names for the following parks differ so greatly from the
    # name to match to, that they must be assigned directly.
    if park_name.lower() == "arlington house": park_code = 'arho'
    if park_name.lower() in ["kings canyon", "sequoia"]: park_code = 'seki'
    if park_name.lower() == "white house" : park_code = 'whho'
    if park_name.lower() == "fdr": park_code = 'frde'
    if park_name.lower() == "gateway nra": park_code = 'gate'
    if park_name.lower() == "g w": park_code = 'gwmp'
    if park_name.lower() == "martin l king, jr, nhp": park_code = 'malu'
    if park_name.lower() == "martin luther king, jr. nhp": park_code = 'malu'
    if park_name.lower() == "t roosevelt np": park_code = 'thro'
    if park_name.lower().startswith("fred-spots"): park_code = 'frsp'
    if park_name.lower().startswith("lbj"): park_code = 'lyba'
    if park_name.lower().endswith("wwii"): park_code = 'wwii'
    if park_name.lower().find("sumter") > -1: park_code = 'fosu'
    if park_name.lower().find("longfellow") > -1: park_code = 'long'

    # These are the parks with no code found in the API.
    if park_name.lower().find('caroline') > -1: park_code = 'xxx1'
    if (park_name.lower().find('john d. rockefeller') > -1 or
        park_name.lower().find('jdrockefeller') > -1): park_code = 'xxx2'
    if park_name.lower().find('chelan') > -1: park_code = 'xxx3'
    if park_name.lower().find('ross lake') > -1: park_code = 'xxx4'
    if park_name.lower().find('valor') > -1: park_code = 'xxx5'
    if park_name.lower().find('world war i ') > -1: park_code = 'xxx6'
    if park_name.lower() == "world war i": park_code = 'xxx6'
    if park_name.lower() == "john f. kennedy center for pa": park_code = 'xxx7'

    # Stripping park name does not work for all data sets for National
    # Park of American Samoa, so assign directly.
    if park_name.lower().find('samoa') > -1: park_code = 'npsa'

    return park_code

def main():
    df_lookup = read_park_sites_api()
    #print(df_lookup)
    print('****')
    to_match = "Timucuan Ecological and Historic Preserve"
    #to_match = "American Memorial Park"
    #to_match = "National Mall and Memorial Parks"
    print('Park Name: ', to_match)

    park_name = strip_park_name(to_match)
    print('Stripped Park Name: ', park_name)

    code = lookup_park_code(park_name, df_lookup)
    print('Actual Match: {}'.format(code))

if __name__ == '__main__':
    main()
