'''Create a Folium map of National Park Service site sizes.

This script creates a map of the United States with NPS sites marked
  with a circle corresponding to the site's size. The command line
  argument, "parkset", set by the flag, "-m", allows the user to specify
  the set of park sites to add to the map. If no parameter specified,
  all NPS site locations are added to the map.

The script creates three output files:
    1) nps_parks_map_area.html - map with park area circles.
    2) nps_parks_sorted_by_size.xlsx - list of parks and size.
    3) nps_parks_sorted_by_size.html - list of parks and size.

This script requires the following libraries: math, argparse, pandas,
  folium.

Dependencies:

    * Run the script, nps_create_master_df.py to create the file,
      nps_parks_master_df.xlsx.

This script contains the following functions:

    * create_map : creates an empty Folium map.
    * add_park_area_circles_to_map : Adds circle markers corresponding
      to park area to map.
'''

import math
import argparse
import pandas as pd
import folium

def create_map():
    ''' Create an empty Folium map.

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

def add_park_area_circles_to_map(map, df):
    ''' Add park area circle markers to a map.

    This function adds a circle marker for each park in the parameter
    dataframe to the map. The circle size corresponds to the area of
    the park. The Folium circle marker accepts a radius parameter in
    meters. This radius parameter value was determined by taking the
    area of the park in square meters, dividing it by pi and then taking
    the square root.

    These markers provide the park name and park area in square miles
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

    for _, row in df[~df.lat.isnull()].iterrows():
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
    map_df_export = (df[['park_name', 'gross_area_acres',
                         'gross_area_square_miles']]
                     .sort_values(by=['gross_area_acres'], ascending=False)
                     .reset_index(drop=True))
    map_df_export.index += 1
    export_cols = {'park_name': 'Park Name',
                   'gross_area_acres': 'Size (acres)',
                   'gross_area_square_miles': 'Size (square miles)'}
    map_df_export = map_df_export.rename(columns=export_cols)
    map_df_export.to_excel('_output/nps_parks_sorted_by_size.xlsx',
                           index=False)
    map_df_export.to_html('_output/nps_parks_sorted_by_size.html',
                          justify='left',
                          classes='table-park-list',
                          float_format=lambda x: '{:,.2f}'.format(x))

    return map

def main():
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    parser = argparse.ArgumentParser()

    # The user can specify the set of parks to map using the command
    # line parameter, 'parkset'. If no parameter specified, all park
    # sites are added to the map.
    parser.add_argument('-p', '--parkset', type=str,
           help = "Set of parks for which to display locations. If not \
                  specified, all park sites will be mapped.\
                  Possible values are: 'National Park', 'National Monument', \
                  'National Preserve or Reserve', 'National Lakeshore or \
                  Seashore', 'National River', 'National Trail', 'National \
                  Historic Site', 'National Memorial', 'National Recreation \
                  Area', 'National Parkway', 'National Heritage Area', \
                  'Affiliated Area', 'Other'")

    args = parser.parse_args()

    if args.parkset:
        map_df = df[df.park_set == args.parkset]
        print("Creating park size map for the park set, '"
              + args.parkset + "'.")
    else:
        map_df = df
        print("Creating park size map for all NPS sites.")

    park_map = create_map()
    park_map = add_park_area_circles_to_map(park_map, map_df)
    park_map.save('_output/nps_parks_map_area.html')

if __name__ == '__main__':
    main()
