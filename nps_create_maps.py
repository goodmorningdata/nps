'''Create Folium map of National Park Service sites.

This script allows the user to...

The script creates an html file as output named
"nps_parks_map.html".

This script requires the following libraries: pandas, folium.

Dependencies:

    *

This script contains the following functions:

    * create_map :
    * add_map_location :

'''

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
                     #tiles = 'Stamen Toner')
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
                                            prefix='fa',                        icon=icon),
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
                'color' : ['darkgreen', 'darkblue', 'beige', 'lightblue',
                           'lightblue', 'beige', 'red', 'blue', 'beige',
                           'beige', 'red', 'orange', 'orange'],
                'icon' : ['tree', 'monument', 'pagelines', 'water', 'water',
                          'sign', 'university', 'monument', 'pagelines',
                          'road', 'univeristy', 'map-marker-alt', 'orange']
              }
    )

    park_map = create_map()

    # TODO - Allow user to specify park_set as a command line argument.
    map_park_set = 'National Park'
    #map_park_set = 'National Monument'
    #map_park_set = ''

    if map_park_set:
        map_df = df[df.park_set == map_park_set]
    else: map_df = df

    # Add each location in the park set dataframe to the map.
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

    park_map.save('nps_parks_map.html')

if __name__ == '__main__':
    main()
