import pandas as pd
import argparse
import seaborn as sns

# Use Seaborn formatting for plots and set color palette.
sns.set()
sns.set_palette('Paired')

def get_parks_df(warning=None):
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
        print("\nCreating visualizations for the park designation, {}.\n"
              .format(args.designation))
        designation = args.designation
    else:
        df_park = df
        print("\nCreating visualizations for all NPS sites.\n")
        designation = "All Parks"

    # Check for missing location data.
    if 'location' in warning:
        missing_location = df_park[df_park.lat.isnull()].park_name
        if missing_location.size:
            print("** Warning ** ")
            print("Park sites with missing lat/long from API, so no location "
                  "available. These park sites will not be added to any "
                  "map visualizations:")
            print(*missing_location, sep=', ')
            print("** Total parks missing location: {}"
                 .format(len(df_park[df_park.lat.isnull()].park_name)))

    # Check for missing park size data.
    if 'size' in warning:
        missing_loc = df_park[df_park.lat.isnull()].park_name
        if missing_loc.size:
            print("\n** Warning ** ")
            print("Park sites with missing lat/long from API, so no location "
                  "available. These park sites will not be added to the map:")
            print(*missing_loc, sep=', ')
            print("** Total parks missing location: {}"
                 .format(len(missing_loc)))
            df_park = df_park[~df_park.lat.isnull()]

    print("")

    return df_park, designation
