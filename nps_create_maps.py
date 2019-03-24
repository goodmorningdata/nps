'''Create Folium map of National Park Service sites.

This script allows the user to create a map of the United States with a
  set of park site locations marked by icons.

The script creates an html file as output named
  "nps_parks_map.html".

This script requires the following libraries: math, argparse, pandas,
  folium.

Dependencies:

    * Run the script, nps_create_master_df.py to create the file,
      nps_parks_master_df.xlsx.

This script contains the following functions:

    * create_map : creates a Folium map.
    * add_map_location : adds NPS site locations to the map.
'''

import math
import argparse
import pandas as pd
import folium

def create_map():
    '''
    Creates a Folium map.

    This function creates a Folium map object, centered on the lat/long
    center of the lower 48 states.

    Parameters
    ----------
    None

    Returns
    -------
    map : Folium map object
      Folium map ready for park location addition.
    '''

    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48,
                     zoom_start = 4,
                     control_scale = True,
                     tiles = 'Stamen Terrain')
    return map

def add_map_location(map, lat, long, icon, color, popup):
    '''
    Adds locations to the Folium map object.

    This function adds park locations to the Folium map at the latitude
    and longitude specified in the parameters. Locations will be
    marked with an icon (using Font Awesome icons:
    https://fontawesome.com/icons?d=gallery&m=free), and an icon color.
    The icon will show a popup message on click with clickable link.

    Parameters
    ----------
    map : Folium map object
      Map on which to plot the location.
    lat : float
      Latitude of location to plot.
    long : float
      Longitude of location to plot.
    icon : str
      Font Awesome icon to mark location.
    color : str
      Icon color.
    popup : str
      String of html to add link to popup.

    Returns
    -------
    map : Folium map object
      Map object with new location added.
    '''

    popup_html = folium.Html(popup, script=True)
    marker = folium.Marker(location = [lat, long],
                           icon = folium.Icon(color=color,
                                              prefix='fa',
                                              icon=icon),
                           popup = folium.Popup(popup_html)
                           ).add_to(map)

    return map

def main():
    # Read in the park master dataframe.
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    # Assign map icons and colors to park sets.
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
              }
    )

    # The user can specify the set of parks to map using the command
    # line parameter, parkset. If no parameter specified, all park sites
    # should be added as locations to the map.
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--parkset', type=str,
           help = "Set of parks for which to display locations. If not \
                  specified, all park sites will be mapped.\
                  Possible values are: 'National Park', 'National Monument', \
                    'National Preserve or Reserve', 'National Lakeshore or \
                     Seashore', 'National River', 'National Trail', 'National \
                     Historic Site', 'National Memorial', 'National Recreation \
                     Area', 'National Parkway', 'National Heritage Area', \
                    'Affiliated Area', 'Other'")
    parser.add_argument('-m', '--maptype', type=str,
           help = "Type of map to produce. Possible values are: 'loc' or \
                  location' = park Location map; 'area' or 'acreage' = park \
                  area map; 'visitor' or 'visits' = park visitation map.")
    args = parser.parse_args()

    if args.parkset:
        map_df = df[df.park_set == args.parkset]
    else: map_df = df

    park_map = create_map()

    if args.maptype and args.maptype in ['area','acreage']:
        # If command-line option specifies a park area map, add each
        # park to the map with a circle approximating its size.
        #folium.Popup(row.park_name.replace("'", r"\'"))
        for _, row in map_df[~map_df.lat.isnull()].iterrows():
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
            ).add_to(park_map)
        park_map.save('nps_parks_map_area.html')
        map_df[['park_code', 'park_name', 'gross_area_acres', 'gross_area_square_miles']].sort_values(by=['gross_area_acres']).to_excel('nps_parks_sorted_by_size.xlsx', index=False)
    else:
        # If command-line option not specified or is type = 'location'
        # or 'loc', add each location in the park set df to the map.
        for _, row in map_df[~map_df.lat.isnull()].iterrows():
            icon_df_row = icon_df[icon_df.park_set == row.park_set]
            popup_string = ('<a href="'
                            + 'https://www.nps.gov/' + row.park_code
                            + '" target="_blank">'
                            + row.park_name + '</a>').replace("'", r"\'")
            park_map = add_map_location(park_map, row.lat, row.long,
                                        icon_df_row.values[0][2],
                                        icon_df_row.values[0][1],
                                        popup_string)

        park_map.save('nps_parks_map_location.html')

if __name__ == '__main__':
    main()
