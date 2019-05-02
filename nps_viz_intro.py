'''Create visualizations to introduce readers to the National Parks.

This script generates the following visualizations to introduce readers
to the National Park Service.
1) A choropleth map of the United States with state color corresponding
   to the number of parks in that state.
   - Output file = nps_parks_state_choropleth_map.html
2) A bar chart of the number of parks in each year since 1904.
   - Output file = nps_parks_num_parks_per_year.html

This script requires the following libraries: argparse, pandas, folium,
    operator, functools, collections, branca.colormap, geopandas.

Dependencies:
    * Run the script, nps_create_master_df.py to create the file,
      nps_parks_master_df.xlsx.

This script contains the following functions:
    * get_state_color : Determine correct state color based on number
      of parks.
    * create_state_count_choropleth : Create park count choropleth.
    * plot_num_parks_per_year : Create bar chart of the number of parks
      in the system in each year.
'''

import argparse
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


def create_state_count_choropleth(df):
    ''' Create a cholorpleth U.S. map of number of parks per state.

    This function counts the number of parks per state and stores the
    result in a dataframe. Then it creates a linear color map using the
    range of parks per state. The function then reads in a GeoJSON file
    of the United States and merges this with the parks per state
    dataframe. These objects are then used to create a choropleth map
    of the United States with state color based on the number of parks
    in that state. If no parks in a state, it will be gray.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of all parks to add to the map.

    Returns
    -------
    map : Folium map object
      Folium map with choropleth color added.
    '''

    # Create a two-column dataframe of state and a count of the number
    # of parks in that state.
    state_list = df["states"].apply(lambda x: x.split(","))
    state_list = reduce(operator.add, state_list)
    parks_per_state = (pd.DataFrame
                       .from_dict(Counter(state_list), orient="index")
                       .reset_index())
    parks_per_state = (parks_per_state
                      .rename(columns={"index":"state", 0:"park_count"}))

    # Create the color map.
    color_scale = LinearColormap(["yellow", "green", "blue"],
                                 vmin=parks_per_state['park_count'].min(),
                                 vmax=parks_per_state['park_count'].max())
    color_scale.caption = "Number of National Parks per state"

    # Create a dataframe from the json file using GeoPandas.
    geo_df = gpd.read_file("_reference_data/us-states.json")
    geo_df = geo_df.merge(parks_per_state, left_on="id",
                          right_on="state", how="left").fillna(0)

    # Find the center of the data and create an empty map.
    centroid = geo_df.geometry.centroid
    map = folium.Map(location = [centroid.y.mean(), centroid.x.mean()],
                     zoom_start = 3)

    # Color each state based on the number of parks in it.
    folium.GeoJson(
        data = geo_df[["geometry", "name", "state", "park_count"]],
        name = "United States of America",
        style_function = lambda x: {
            "fillColor" : get_state_color(x, parks_per_state, color_scale),
            "fillOpacity" : 0.7,
            "color" : "black",
            "line_opacity" : 0.5,
            "weight" : 0.5
        },
        tooltip = folium.features.GeoJsonTooltip(
            fields=["name","park_count",],
            aliases=["State","# of parks"])
    ).add_to(map)

    # Add color scale legend.
    map.add_child(color_scale)

    return map

def plot_num_parks_per_year(df):
    years = [str(i) for i in range(1904, 2019)]
    #Want count of parks founded in each year (bar) and total number of parks in the system in each year (line)
    for year in years:
         print ('****', year)
         #print(df[df[year] > 0 & pd.notnull(df[year])])
         print(df[df[year] > 0 & pd.notnull(df[year])].count())
    #nps_parks_num_parks_per_year.html

def main():
    # Read in the parks master dataframe from Excel.
    df = pd.read_excel("nps_parks_master_df.xlsx", header=0)

    # The user can specify the set of parks to map using the command
    # line parameter, 'parkset'. If no parameter specified, all park
    # sites are added to the map.
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--parkset", type=str,
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
        print("Creating maps for the park set, '"
              + args.parkset + "'.")
    else:
        map_df = df
        print("Creating maps for all NPS sites.")

    # Create the state park count choropleth and save to a file.
    #state_map = create_state_count_choropleth(map_df)
    #state_map.save("_output/nps_parks_state_choropleth_map.html")

    # Plot the number of parks in the systeam each year.
    plot_num_parks_per_year(map_df)

    # Plot the total number of parks per year and number
    # established that year.
    plot_num_parks_num_established(map_df)

if __name__ == "__main__":
    main()
