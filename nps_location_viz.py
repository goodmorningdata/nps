'''Create Folium maps of National Park Service data.

This script creates a map of the United States with a set of park site
  locations marked by icons. The command line argument, "parkset", set
  by the flag, "-m", allows the user to specify the set of park sites
  to add to the map. If no parameter specified, all NPS site locations
  are added to the map.

The script creates an html file as output: nps_parks_map_location.html

This script requires the following libraries: argparse, pandas, folium.

Dependencies:

    * Run the script, nps_create_master_df.py to create the file,
      nps_parks_master_df.xlsx.

This script contains the following functions:

    * create_map : creates an empty Folium map.
    * add_park_locations_to_map : Adds park location markers to map.
'''

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

def add_park_locations_to_map(map, df):
    ''' Add park location markers to a map.

    This function adds all locations in the dataframe to the map. Icon
    type and color is dependent on park set assigned to each site.

    Parameters
    ----------
    map : Folium map object
      Folium map to add location markers to.

    df : Pandas DataFrame
      DataFrame of all park locations to add to the map.

    Returns
    -------
    map : Folium map object
      Folium map with location markers added.
    '''

    # Create a dataframe of park sets with assigned icons and colors.
    icon_df = pd.DataFrame(
              {'park_set' : ['National Park', 'National Monument',
                             'National Preserve or Reserve',
                             'National Lakeshore or Seashore',
                             'National River', 'National Trail',
                             'National Historic Site', 'National Memorial',
                             'National Recreation Area', 'National Parkway',
                             'National Heritage Area', 'Affiliated Area',
                             'Other'],
                'color' : ['green', 'lightgreen', 'beige', 'lightblue',
                           'lightblue', 'beige', 'red', 'red', 'beige',
                           'beige', 'red',  'orange', 'orange'],
                'icon' : ['tree', 'tree', 'pagelines', 'tint', 'tint',
                          'pagelines', 'university', 'university', 'pagelines',
                          'road', 'university', 'map-marker', 'map-marker']
              })

    for _, row in df[~df.lat.isnull()].iterrows():

        # Create popup with link to park website.
        popup_string = ('<a href="'
                        + 'https://www.nps.gov/' + row.park_code
                        + '" target="_blank">'
                        + row.park_name + '</a>').replace("'", r"\'")
        popup_html = folium.Html(popup_string, script=True)

        # Assign color and graphic to icon.
        icon_df_row = icon_df[icon_df.park_set == row.park_set]
        map_icon = folium.Icon(color=icon_df_row.values[0][1],
                               prefix='fa',
                               icon=icon_df_row.values[0][2])

        marker = folium.Marker(location = [row.lat, row.long],
                               icon = map_icon,
                               popup = folium.Popup(popup_html)
                              ).add_to(map)

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
        print("Creating park location map for the park set, '"
              + args.parkset + "'.")
    else:
        map_df = df
        print("Creating park location map for all NPS sites.")

    print("Creating park location map for the park set, '"
          + args.parkset + "'.")
    park_map = create_map()
    park_map = add_park_locations_to_map(park_map, map_df)
    park_map.save('_output/nps_parks_map_location.html')

if __name__ == '__main__':
    main()
