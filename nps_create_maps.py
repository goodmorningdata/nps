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

def add_park_subsets(df):
    '''
    Assign attributes to the different nps site subsets.

    This function...

    Parameters
    ----------
    df : Pandas dataframe

    Returns
    -------
    df : Pandas dataframe
    '''

    national_parks = ['National Park', 'National Park & Preserve',
                      'National and State Parks']
    df.loc[df.designation.isin(national_parks),
          'park_set'] = 'National Park'

    monuments = ['National Monument', 'National Monument & Preserve',
                 'Part of Statue of Liberty National Monument',
                 'National Monument and Historic Shrine',
                 'National Monument of America']
    df.loc[df.designation.isin(monuments),
          ['park_set']] = 'National Monument'

    preserves_reserves = ['National Preserve', 'National Reserve']
    df.loc[df.designation.isin(preserves_reserves),
          ['park_set']] = 'National Preserve or Reserve'

    lakeshores_seashores = ['National Lakeshore', 'National Seashore']
    df.loc[df.designation.isin(lakeshores_seashores),
          ['park_set']] = 'National Lakeshore or Seashore'

    rivers = ['National River & Recreation Area', 'National Scenic River',
              'National River', 'Scenic & Recreational River', 'Wild River',
              'National River and Recreation Area', 'National Scenic Riverway',
              'National Recreational River', 'Wild & Scenic River',
              'National Scenic Riverways', 'National Wild and Scenic River']
    df.loc[df.designation.isin(rivers),
          ['park_set']] = 'National River'

    trails = ['National Scenic Trail', 'National Geologic Trail',
              'National Historic Trail']
    df.loc[df.designation.isin(trails),
          ['park_set']] = 'National Trail'

    historic_sites = ['National Historical Park', 'National Historic Site',
                      'National Historic Area', 'National Historical Reserve',
                      'Part of Colonial National Historical Park',
                      'National Historical Park and Preserve',
                      'National Historical Park and Ecological Preserve',
                      'National Historic District',
                      'Ecological & Historic Preserve',
                      'International Historic Site',
                      'International Park', 'National Battlefield',
                      'National Battlefield Site', 'National Military Park',
                      'National Battlefield Park',
                      'National Historic Landmark District']
    df.loc[df.designation.isin(historic_sites),
          ['park_set']] = 'National Historic Site'

    memorials = ['National Memorial', 'Memorial']
    df.loc[df.designation.isin(memorials),
          ['park_set']] = 'National Memorial'

    recreation_areas = ['National Recreation Area']
    df.loc[df.designation.isin(recreation_areas),
          ['park_set']] = 'National Recreation Area'

    parkways = ['Parkway', 'Memorial Parkway']
    df.loc[df.designation.isin(parkways),
          ['park_set']] = 'National Parkway'

    heritage_areas = ['National Heritage Partnership',  'Heritage Area',
                      'National Heritage Corridor', 'Heritage Center',
                      'Cultural Heritage Corridor', 'National Heritage Area']
    df.loc[df.designation.isin(heritage_areas),
          ['park_set']] = 'National Heritage Area'

    affiliated_areas = ['Affiliated Area']
    df.loc[df.designation.isin(affiliated_areas),
          ['park_set']] = 'Affiliated Area'

    others = ['Park', 'Other']
    df.loc[df.designation.isin(others),
          ['park_set']] = 'Other'

    return df

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

    # Assign icons and colors to subsets
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
