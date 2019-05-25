'''
This script creates a map of the United States with NPS sites marked
with a circle corresponding to the site's size. The command line
argument, "designation", set by the flag, "-d", allows the user to
specify the set of park sites to add to the map. If no parameter is
specified, all NPS site locations are added to the map.

The script creates three output files:
  1) nps_parks_map_size.html - map with park area circles.
  2) nps_parks_sorted_by_size.xlsx - list of parks and size.
  3) nps_parks_sorted_by_size.html - list of parks and size.

Required Libraries
------------------
math, argparse, pandas, folium

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
'''

import math
import argparse
import pandas as pd
import folium

def create_map():
    '''
    This function creates a Folium map object, centered on the lat/long
    center of the lower 48 states.

    Parameters
    ----------
    None

    Returns
    -------
    map : Folium map object
      Empty Folium map.
    '''

    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48,
                     zoom_start = 3,
                     control_scale = True,
                     tiles = 'Stamen Terrain')

    return map

def add_park_size_circles_to_map(map, df):
    '''
    This function adds a circle marker for each park in the parameter
    dataframe to the map. The circle size corresponds to the area of
    the park. The radius of the circle was calculated by taking the
    area of the park in square meters, dividing it by pi and then taking
    the square root.

    These markers provide the park name and park size in square miles
    as a tooltip. A tooltip instead of a popup is used for this map
    because the popup was less sensitive for the circle markers.

    Parameters
    ----------
    map : Folium map object
      Folium map to add circle markers to.

    df : Pandas DataFrame
      DataFrame of all park visitors to add to the map.

    Returns
    -------
    map : Folium map object
      Folium map with circle area markers added.
    '''

    for _, row in df.iterrows():
        tooltip = (row.park_name.replace("'", r"\'")
                   + ', {:,.0f}'.format(row.gross_area_square_miles)
                   + ' square miles')
        folium.Circle(
            radius=math.sqrt(row.gross_area_square_meters/math.pi),
            location=[row.lat, row.long],
            tooltip=tooltip,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(map)

    # Export a sorted list of parks and their size to both an Excel file
    # and an html file for reference and blog posts.
    park_df_export = (df[['park_name', 'gross_area_acres',
                          'gross_area_square_miles']]
                      .sort_values(by=['gross_area_acres'], ascending=False)
                      .reset_index(drop=True))
    park_df_export.index += 1
    export_cols = {'park_name': 'Park Name',
                   'gross_area_acres': 'Size (acres)',
                   'gross_area_square_miles': 'Size (square miles)'}
    park_df_export = park_df_export.rename(columns=export_cols)
    park_df_export.to_excel('_output/nps_parks_sorted_by_size.xlsx',
                            index=False)
    park_df_export.to_html('_output/nps_parks_sorted_by_size.html',
                           justify='left',
                           classes='table-park-list',
                           float_format=lambda x: '{:,.2f}'.format(x))

    return map

def main():
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
                  'National Battlefield Sites', 'National Military Parks',\ 'National Historical Parks', 'National Historic Sites',\
                  'National Lakeshores', 'National Memorials',\
                  'National Monuments', 'National Parks', 'National Parkways',\ 'National Preserves', 'National Reserves',\
                  'National Recreation Areas', 'National Rivers',\
                  'National Wild and Scenic Rivers and Riverways',\
                  'National Scenic Trails', 'National Seashores',\
                  'Other Designations'")
    args = parser.parse_args()

    # Filter the dataframe based on designation and remind user which
    # park designations will be in the visualizations.
    if args.designation:
        park_df = df[df.designation == args.designation]
        print("\nCreating park size map for the park designation, {}."
              .format(args.designation))
    else:
        park_df = df
        print("\nCreating park size map for all NPS sites.")

    # Check for parks missing location and remove from dataframe.
    missing_loc = park_df[park_df.lat.isnull()].park_name
    if missing_loc.size:
        print("\n** Warning ** ")
        print("Park sites with missing lat/long from API, so no location "
              "available. These park sites will not be added to the map.")
        print(*missing_loc, sep=', ')
        print("Total parks missing location: {}".format(len(missing_loc)))
        park_df = park_df[~park_df.lat.isnull()]

    # Check for parks missing size and remove from dataframe.
    missing_size = park_df[park_df.gross_area_acres.isnull()].park_name
    if missing_size.size:
        print("\n** Warning **")
        print("Park sites not included in NPS Acreage report, so no park "
              "size available. These park sites will not be added to the map.")
        print(*missing_size, sep=', ')
        print("** Total parks missing size: {}".format(len(missing_size)))
        park_df = park_df[~park_df.gross_area_acres.isnull()]

    park_map = create_map()
    park_map = add_park_size_circles_to_map(park_map, park_df)
    park_map.save('_output/nps_parks_map_size.html')

if __name__ == '__main__':
    main()
