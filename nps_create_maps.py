'''Create Folium map of National Park Service sites.

This script allows the user to create a map of the United States with a
  set of park site locations marked by icons.

The script creates an html file as output named
  "nps_parks_map_location.html", if location map type is chosen, or
  "nps_parks_map_area.htl", if nps_parks_map_area.html if area map type
  is chosen. Additionaly, if area map type is chosen, a table of park
  names and size sorted by size is exported to an Excel file,
  nps_parks_sorted_by_size.xlsx, and to an html file,
  nps_parks_sorted_by_size.html.

This script requires the following libraries: math, argparse, pandas,
  folium.

Dependencies:

    * Run the script, nps_create_master_df.py to create the file,
      nps_parks_master_df.xlsx.

This script contains the following functions:

    * create_map : creates a Folium map.
    * add_park_locations_to_map : Adds park location markers to map.
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
      Folium map ready for park location addition.
    '''

    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48,
                     zoom_start = 3,
                     control_scale = True,
                     tiles = 'Stamen Terrain')
    return map

def add_park_locations_to_map(map, df):
    ''' Add park location markers to a map.

    This function adds all locations in the This function creates a Folium map object, centered on the lat/long
    center of the lower 48 states.

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

    return map

def add_park_visitor_circles_to_map(map, df):
    ''' Add park visitor circle markers to a map.

    This function adds a circle marker for each park in the parameter
    dataframe to the map. The circle size corresponds to the number of
    visitors to the park.

    These markers provide the park name and number of vistors and the latest year that visitor counts are available for as a tooltip. A tooltip instead of a popup is used for this map because the popup was less sensitive for the circle markers.

    Parameters
    ----------
    map : Folium map object
      Folium map to add circle markers to.

    df : Pandas DataFrame
      DataFrame of all park areas to add to the map.

    Returns
    -------
    map : Folium map object
      Folium map with circle area markers added.
    '''

    for _, row in df[~df.lat.isnull()].iterrows():
        tooltip = (row.park_name.replace("'", r"\'")
                   + ', {:,.0f}'.format(row['2017'])
                   + ' visitors in 2017')
        folium.Circle(
            radius=row['2017']/100,
            location=[row.lat, row.long],
            tooltip=tooltip,
            color='blue',
            fill=True,
            fill_color='blue'
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

    # The user can specify the type of plot to produce using the
    # command line parameter, 'maptype'. If no parameter specified,
    # a location map is created.
    parser.add_argument('-m', '--maptype', type=str,
           help = "Type of map to produce. Possible values are: 'loc' or \
                  location' = park Location map; 'area' or 'acreage' = park \
                  area map; 'visitor' or 'visits' = park visitation map.")
    args = parser.parse_args()

    # Create an empty map
    park_map = create_map()

    if args.parkset:
        map_df = df[df.park_set == args.parkset]
    else: map_df = df

    if args.maptype and args.maptype in ['area', 'acreage']:
        park_map = add_park_area_circles_to_map(park_map, map_df)
        park_map.save('nps_parks_map_area.html')

        # Export a sorted list of parks and their size to both an Excel
        # file and an html file for reference.
        map_df_export = (map_df[['park_name',
                                 'gross_area_acres', 'gross_area_square_miles']]
                         .sort_values(by=['gross_area_acres'], ascending=False)
                         .reset_index(drop=True))
        map_df_export.index += 1
        export_cols = {'park_name': 'Park Name',
                       'gross_area_acres': 'Size (acres)',
                       'gross_area_square_miles': 'Size (square miles)'}
        map_df_export = map_df_export.rename(columns=export_cols)
        map_df_export.to_excel('nps_parks_sorted_by_size.xlsx', index=False)
        map_df_export.to_html('nps_parks_sorted_by_size.html',
                              justify='left',
                              bold_rows=True,
                              float_format=lambda x: '{:,.2f}'.format(x))

    elif args.maptype and args.maptype in ['visitor', 'visits']:
        park_map = add_park_visitor_circles_to_map(park_map, map_df)
        park_map.save('nps_parks_map_visitors.html')

    else:
        park_map = add_park_locations_to_map(park_map, map_df)
        park_map.save('nps_parks_map_location.html')

        # Export a sorted list of parks and their total visitors to both
        # an Excel file and an html file for reference.
        map_df_export = (map_df[['park_name',
                                 'gross_area_acres', 'gross_area_square_miles']]
                         .sort_values(by=['gross_area_acres'], ascending=False)
                         .reset_index(drop=True))
        map_df_export.index += 1
        export_cols = {'park_name': 'Park Name',
                       'gross_area_acres': 'Size (acres)',
                       'gross_area_square_miles': 'Size (square miles)'}
        map_df_export = map_df_export.rename(columns=export_cols)
        map_df_export.to_excel('nps_parks_sorted_by_size.xlsx', index=False)
        map_df_export.to_html('nps_parks_sorted_by_size.html',
                              justify='left',
                              bold_rows=True,
                              classes='table table-blog',
                              float_format=lambda x: '{:,.2f}'.format(x))

if __name__ == '__main__':
    main()
