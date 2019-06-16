'''
This script creates a set of Folium choroplth maps using NPS data
available from their website and API, and from Wikipedia.

The following visualizations are created:
1) A Folium choropleth map of the United States with state color
   corresponding to the number of parks in that state.

Required Libraries
------------------
argparse, pandas, folium, operator, geopandas, functools, collections,
and branca.colormap.

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
'''

from nps_shared import *
import pandas as pd
import folium
import operator
import geopandas as gpd
from functools import reduce
from collections import Counter
from branca.colormap import LinearColormap

def get_state_color(feature, df, color_scale):
    '''
    This function extracts the state from the GeoJson feature, finds the
    number of parks in that state, and then returns the correct color
    for that state using the color scale. If there are no parks in
    the state, the color, "lightgray", is returned.

    Parameters
    ----------
    feature : dict
      GeoJson feature for each state in the data.

    df : Pandas DataFrame
      DataFrame of states and their park count.

    color_scale : LinearColormap
      Parks per state color scale.

    Returns
    -------
    color : str
      Html color string.
    '''

    state = feature["properties"]["state"]
    row = df.loc[df["state"] == state].park_count.values

    if row.size > 0:
        return color_scale(row[0])
    else:
        return "lightgray"


def create_state_count_choropleth(df, designation):
    '''
    This function counts the number of parks per state and stores the
    result in a dataframe. Then it creates a linear color map using the
    range of parks per state. The function then reads in a GeoJSON file
    of the United States and merges this with the parks per state
    dataframe. These objects are then used to create a choropleth map
    of the United States with state color based on the number of parks
    in that state. If there are no parks in a state, it will be gray.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of all parks to add to the map.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    map : Folium map object
      Folium map with choropleth color added.
    '''

    # Create a two-column dataframe of state and a count of the number
    # of parks in that state.
    state_list = df['states'].apply(lambda x: x.split(','))
    state_list = reduce(operator.add, state_list)
    parks_per_state = (pd.DataFrame
                       .from_dict(Counter(state_list), orient='index')
                       .reset_index())
    parks_per_state = (parks_per_state
                      .rename(columns={'index':'state', 0:'park_count'}))

    # Create the color map.
    color_scale = LinearColormap(['yellow', 'green', 'blue'],
                                 vmin=parks_per_state['park_count'].min(),
                                 vmax=parks_per_state['park_count'].max())
    color_scale.caption = ("Number of parks per state ({})"
                           .format(designation))

    # Create a dataframe from the json file using GeoPandas.
    df_geo = gpd.read_file('_reference_data/us-states.json')
    df_geo = df_geo.merge(parks_per_state, left_on='id',
                          right_on='state', how='left').fillna(0)

    # Find the center of the data and create an empty map.
    centroid = df_geo.geometry.centroid
    map = folium.Map(location = [centroid.y.mean(), centroid.x.mean()],
                     zoom_start = 3)

    # Color each state based on the number of parks in it.
    folium.GeoJson(
        data = df_geo[['geometry', 'name', 'state', 'park_count']],
        name = 'United States of America',
        style_function = lambda x: {
            'fillColor' : get_state_color(x, parks_per_state, color_scale),
            'fillOpacity' : 0.7,
            'color' : 'black',
            'line_opacity' : 0.5,
            'weight' : 0.5
        },
        tooltip = folium.features.GeoJsonTooltip(
            fields=['name','park_count',],
            aliases=["State","# of parks"])
    ).add_to(map)

    # Add color scale legend.
    map.add_child(color_scale)

    # Save choropleth to file.
    filename = ('nps_state_count_choropleth_'
               + designation.lower().replace(' ','_') + '.html')
    map.save('_output/' + filename)

    return map

def main():
    df_park, designation = get_parks_df(warning=['state'])

    # Parks not missing state.
    df_park_states = df_park[~df_park.states.isnull()]

    # Map #1 - Create the state park count choropleth and save to a file.
    state_map = create_state_count_choropleth(df_park_states, designation)

if __name__ == "__main__":
    main()
