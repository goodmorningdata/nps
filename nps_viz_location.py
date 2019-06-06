'''
This script creates a map of the United States with a set of park site
locations marked by icons. The map is created using the Python library,
Folium. The command line argument, "designation", set by the flag, "-d",
allows the user to specify the set of park designations to add to the
map. If no parameter specified, all NPS  site locations are added to
the map. The map is saved to the html file, nps_parks_map_location.html

Required Libraries
------------------
argparse, pandas, folium

Dependencies
------------
1) Run the script, nps_create_master_df.py, to create the file
   nps_parks_master_df.xlsx.
'''

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

def add_park_locations_to_map(map, df):
    '''
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
    df_icon = pd.DataFrame(
              {'designation' : ['International Historic Sites',
              'National Battlefields', 'National Battlefield Parks',
              'National Battlefield Sites', 'National Military Parks', 'National Historical Parks', 'National Historic Sites',
              'National Lakeshores', 'National Memorials',
              'National Monuments', 'National Parks', 'National Parkways', 'National Preserves', 'National Reserves',
              'National Recreation Areas', 'National Rivers',
              'National Wild and Scenic Rivers and Riverways',
              'National Scenic Trails', 'National Seashores',
              'Other Designations'],
              'color' : ['beige', 'black', 'black', 'black', 'black', 'beige',
                        'beige', 'blue', 'red', 'lightgreen', 'green', 'brown',
                        'lightgreen','lightgreen', 'lightgreen', 'blue',
                        'blue', 'beige', 'blue', 'orange'],
              'icon' : ['map-marker', 'map-marker', 'map-marker', 'map-marker',
                       'map-marker', 'map-marker', 'map-marker', 'map-marker', 'map-marker', 'map-marker', 'tree', 'map-marker', 'map-marker', 'map-marker', 'map-marker', 'map-marker', 'map-marker', 'map-marker', 'map-marker', 'map-marker']
              })

    for _, row in df.iterrows():
        # Create popup with link to park website.
        popup_string = ('<a href="'
                        + 'https://www.nps.gov/' + row.park_code
                        + '" target="_blank">'
                        + row.park_name + '</a>').replace("'", r"\'")
        popup_html = folium.Html(popup_string, script=True)

        # Assign color and graphic to icon.
        df_icon_row = df_icon[df_icon.designation == row.designation]
        map_icon = folium.Icon(color=df_icon_row.values[0][1],
                               prefix='fa',
                               icon=df_icon_row.values[0][2])

        marker = folium.Marker(location = [row.lat, row.long],
                               icon = map_icon,
                               popup = folium.Popup(popup_html)
                              ).add_to(map)

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
        print("\nCreating park location map for the park designation, {}."
              .format(args.designation))
    else:
        df_park = df
        print("\nCreating park location map for all NPS sites.")

    # Check for parks missing location and remove from dataframe.
    missing_location = df_park[df_park.lat.isnull()].park_name
    if missing_location.size:
        print("** Warning ** ")
        print("Park sites with missing lat/long from API, so no location "
              "available. These park sites will not be added to the map.")
        print(*missing_location, sep=', ')
        print("Total parks missing location: {}"
              .format(len(df_park[df_park.lat.isnull()].park_name)))
        df_park = df_park[~df_park.lat.isnull()]
        print("")

    park_map = create_map()
    park_map = add_park_locations_to_map(park_map, df_park)
    park_map.save('_output/nps_parks_map_location.html')

if __name__ == '__main__':
    main()
