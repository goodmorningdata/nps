'''Create Folium map of National Park Service sites.

This script allows the user to...

The script creates an html file as output named
"nps_parks_map.html".

This script requires the following libraries: pandas, folium.

Dependencies:

    *

This script contains the following functions:

    *
'''

import pandas as pd
import folium

def create_map():
    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48,
                     zoom_start = 4,
                     control_scale = True,
                     #tiles = 'Stamen Toner')
                     tiles = 'Stamen Terrain')
    return map

def add_map_location(map, popup, lat, long, icon, color):
    popup_html = folium.Html(popup, script=True)
        marker = folium.Marker(location = [lat, long],
                           icon = folium.Icon(color=color,
                                            prefix='fa',                        icon=icon),
                           popup = folium.Popup(popup_html)
                           )
    marker.add_to(map)

    return map

def main():
    # Read in the park master dataframe.
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    # Assign map icons and colors to subsets
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

    for _, row in map_df[~map_df.lat.isnull()].iterrows():
        icon_df_row = icon_df[icon_df.park_set == row.park_set]
        popup_string = ('<a href="'
                        + 'https://www.nps.gov/' + row.park_code
                        + '" target="_blank">'
                        + row.park_name + '</a>').replace("'", r"\'")
        park_map = add_map_location(park_map, popup_string,
                                    row.lat, row.long,
                                    icon_df_row.values[0][2],
                                    icon_df_row.values[0][1])

    park_map.save('nps_parks_map.html')

if __name__ == '__main__':
    main()
