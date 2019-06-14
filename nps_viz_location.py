'''
This script creates a set of visualizations using the location data
(lat, long, state) available for each park from the NPS API. The command
line argument, "designation", set by the flag, "-d", allows the user to
specify the set of park designations to add to the map. If no parameter
specified, all NPS  site locations are added to the visualizations.

The following visualizations are created:
1) A Folium map with park location mapped as an icon. Each icon has as
   a clickable popup that tells the park name and links to the nps.gov
   page for the park.
   - Output file = nps_parks_map_location_{designation}.html

2) Plots including:
   Plot #1 - Parks per state bar chart.

Required Libraries
------------------
argparse, pandas, folium

Dependencies
------------
1) Run the script, nps_create_master_df.py, to create the file
   nps_parks_master_df.xlsx.
'''

from nps_shared import *
import pandas as pd
import folium
import operator
import seaborn as sns
import matplotlib.pyplot as plt
from functools import reduce
from collections import Counter

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
    colors = ['lightgreen'] * 20
    colors[10] = 'green'
    icons = ['map-marker'] * 20
    icons[10] = 'tree'

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
              'color' : colors,
              'icon' : icons
              })

    for _, row in (df[~df.lat.isnull()]
        .sort_values(by='designation', ascending=False).iterrows()):
        # Create popup with link to park website.
        if ~(row.park_code[:3] == 'xxx'):
            popup_string = ('<a href="'
                           + 'https://www.nps.gov/' + row.park_code
                           + '" target="_blank">'
                           + row.park_name + '</a>').replace("'", r"\'")
        else:
            popup_string = row.park_name

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

def plot_parks_per_state(df, designation):
    '''
    This function plots the number of parks per state in the parameter
    dataframe as a bar plot.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of all park locations to plot.

    designtation : str
      Designation of parks in the dataframe.

    Returns
    -------
    map : Folium map object
      Folium map with location markers added.
    '''

    # Create dataframe of state and count of park in each state.
    state_list = df['states'].apply(lambda x: x.split(','))
    state_list = reduce(operator.add, state_list)
    parks_per_state = (pd.DataFrame
        .from_dict(Counter(state_list), orient='index')
        .reset_index())
    parks_per_state = (parks_per_state
        .rename(columns={'index':'state', 0:'park_count'}))
    parks_per_state['state_name'] = (
        parks_per_state.state.replace(us_state_abbrev))
    parks_per_state.sort_values(by='state_name', ascending=False, inplace=True)

    # Horizontal bar plot of number of parks in each state.
    title = "Number of parks per state ({})".format(designation)
    filename = ('parks_per_state_' + designation.lower()
                    .replace(' ','_') + '.png')

    fig, ax = plt.subplots(figsize=(8,6))
    plt.barh(parks_per_state.state_name, parks_per_state.park_count, alpha=0.8)
    ax.set_title("Number of Parks per state ({})".format(designation))
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.show()

    # Save plot to file.
    fig.savefig('_output/' + filename)

def main():
    df_park, designation = get_parks_df(warning=['location'])

    # Map #1 - Plot park locations and save map to html file.
    park_map = create_map()
    park_map = add_park_locations_to_map(park_map, df_park)
    filename = ('_output/nps_parks_map_location_'
               + designation.lower().replace(' ','_') + '.html')
    park_map.save(filename)

    # Plot #1 - Parks per state bar chart.
    plot_parks_per_state(df_park, designation)

if __name__ == '__main__':
    main()
