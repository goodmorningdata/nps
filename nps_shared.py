'''
'''
import pandas as pd
import argparse
import seaborn as sns

# Use Seaborn formatting for plots and set color palette.
sns.set()
#sns.set_palette('Paired')
sns.set_palette('Dark2')

us_state_abbrev = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'DC': 'District of Columbia',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'AS': 'American Samoa',
    'GU': 'Guam',
    'MP': 'Northern Mariana Islands',
    'PW': 'Palau',
    'PR': 'Puerto Rico',
    'VI': 'U.S. Virgin Islands'
}

def get_parks_df(warning=['None']):
    '''
    This function is used by all the visualization scripts to read in
    the master dataframe, read the command line designation parameter,
    filter the dataframe by designation, and print warning messages.

    Parameters
    ----------
    warning : list
      List of warnings to check dataframe for.

    Returns
    -------
    df_park : Pandas dataframe
      Master dataframe filtered by designation.

    designation : str
      Designation command line parameter.
    '''

    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    # The user can specify the set of parks to map using the command
    # line parameter, 'designation'. If no parameter specified, all
    # park sites are added to the map.
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--designation', type=str,
        help = "Set of parks for which to display locations. If not \
                specified, all park sites will be mapped.\
                Possible values are: 'International Historic Sites',\
                'National Battlefields', 'National Battlefield Parks',\
                'National Battlefield Sites', 'National Military Parks',\
                'National Historical Parks', 'National Historic Sites',\
                'National Lakeshores', 'National Memorials',\
                'National Monuments', 'National Parks', 'National Parkways',\
                'National Preserves', 'National Reserves',\
                'National Recreation Areas', 'National Rivers',\
                'National Wild and Scenic Rivers and Riverways',\
                'National Scenic Trails', 'National Seashores',\
                'Other Designations'")
    args = parser.parse_args()

    # Filter the dataframe based on designation and remind user which
    # park designations will be in the visualizations.
    if args.designation:
        df_park = df[df.designation == args.designation]
        print("\nCreating visualizations for the park designation, {}."
             .format(args.designation))
        designation = args.designation
    else:
        df_park = df
        print("\nCreating visualizations for all NPS sites.")
        designation = "All Parks"

    # Check for missing location data.
    if 'location' in warning:
        missing_location = df_park[df_park.lat.isnull()].park_name
        if missing_location.size:
            print("\n** Warning ** ")
            print("Park sites with missing lat/long from API, so no location "
                  "available. These park sites will not be added to maps:")
            print(*missing_location, sep=', ')
            print("** Total parks missing location: {}"
                 .format(len(df_park[df_park.lat.isnull()].park_name)))

    # Check for missing park size data.
    if 'size' in warning:
        missing_size = df_park[df_park.gross_area_acres.isnull()].park_name
        if missing_size.size:
            print("\n** Warning **")
            print("Park sites not included in NPS Acreage report, so no park "
                  "size available. These park sites will not be added to the " "maps or plots:")
            print(*missing_size, sep=', ')
            print("** Total parks missing size data: {}"
                 .format(len(missing_size)))

    # Check for missing visitor data.
    if 'visitor' in warning:
        missing_visitor = df_park[df_park[2018].isnull()].park_name
        if missing_visitor.size:
            print("\n** Warning **")
            print("Park sites not included in the NPS Visitor Use Statistics "
                  "report, so no park visit data available. These park sites "
                  "will not be added to the map or plots:")
            print(*missing_visitor, sep=', ')
            print("** Total parks missing visit data: {}"
                 .format(len(missing_visitor)))

    # Check for missing state.
    if 'state' in warning:
        missing_state = df_park[df_park.states.isnull()].park_name
        if missing_state.size:
            print("\n** Warning ** ")
            print("Park sites with missing state from API. These park sites "
                  "will not be counted in the chloropleth maps.")
            print(*missing_state, sep=', ')
            print("Total parks missing state: {}"
                 .format(len(df_park[df_park.states.isnull()].park_name)))

    print("")

    return df_park, designation

def set_filename(name, type='', designation=''):
    name = (name.lower().replace(' ','_').replace(',','')
                        .replace('.','').replace('(','').replace(')',''))

    filename = '_output/' + name
    if len(designation) > 0:
        filename = filename + '_' + designation.lower().replace(' ','_')
    filename = filename + '.' + type

    return filename

def set_title(name, designation):
    title = (name
            + " ({})".format(designation.lower())
            )

    return title
