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

def add_map_location(map,):
    return map

def main():
    # Read in the park master dataframe.
    df = pd.read_excel('df_master.xlsx', header=0)

    # Create subsets of park designations.
    df = add_park_subsets(df)

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

    # Craete folium map centered on lower 48 center point.
    park_map = create_folium_map()

    if ~(park_set == 'all'):
        map_df = df[df.designation.isin(park_set)]
    else:
        map_df = df

    # Plot each park site on the map
    for _, row in map_df.iterrows():
        marker = folium.Marker(location=[row.lat, row.long],
                               icon=folium.Icon(color='green',
                                                prefix='fa',
                                                icon='tree'),
                               popup = folium.Popup(row.park_name,
                                                    parse_html=True))

        marker.add_to(map)

    add_locations(park_map,
                  df[~df.lat.isnull()],
                  ['National Park'])

    park_map.save('nps_parks_map.html')

if __name__ == '__main__':
    main()
