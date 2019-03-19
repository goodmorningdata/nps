'''Create master dataframe of National Park Service park data.

This script allows the user to create an excel spreadsheet of all of the
National Park Service sites with relevant data to be used by reporting
tools. NPS Sites include National Parks, Monuments, Historic Sites, etc.
General park data, location, acreage, and visitation data are included.

The script creates an Excel file as output named
"nps_df_parks_master.xlsx" with column headers. Columns include:
park_code, park_name, designation, states, lat, long, gross_area_acres,
and columns 2008-2017 of total park visitors.

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

def add_map_location(map, name, lat, long, icon, color):
    popup_string = '<a href="https://www.nps.gov"target"_blank">Test</a>'
    marker = folium.Marker(location=[lat, long],
                           icon=folium.Icon(color=color,
                                            prefix='fa',                        icon=icon),
                           #popup = folium.Popup(name,
                            #    parse_html=True))
                           popup = folium.Popup(popup_string)
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
    #map_park_set = 'National Park'
    map_park_set = 'National Monument'
    #map_park_set = ''

    if map_park_set:
        map_df = df[df.park_set == map_park_set]
    else: map_df = df

    for _, row in map_df[~map_df.lat.isnull()].iterrows():
        icon_df_row = icon_df[icon_df.park_set == row.park_set]
        park_map = add_map_location(park_map, row.park_name,
                                    row.lat, row.long,
                                    icon_df_row.values[0][2],
                                    icon_df_row.values[0][1])

    park_map.save('nps_parks_map.html')

if __name__ == '__main__':
    main()
