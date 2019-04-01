'''Create maps and plots of National Park Service visitation data.

This script generates a few visualizations of National Park visitation
data.
1) A Folium map with park location mapped as a circle with size
   dependent on park size. Circles have a tooltip telling the user the
   park name and the size in square miles.
   Output file = nps_parks_map_area.html
2) A table of park sites and sizes in order of size, largest to
   smallest.
   Output files = nps_parks_sorted_by_size.xlsx,
   nps_parks_sorted_by_size.html.
3)

This script requires the following libraries: argparse, pandas, folium.

Dependencies:

    * Run the script, nps_create_master_df.py to create the file,
      nps_parks_master_df.xlsx.

This script contains the following functions:

    * create_map : creates a Folium map.
    * add_park_visitor_circles_to_map : Adds circle markers corresponding
      to park visitors to map.
    * output_visitor_data_to_tables : Output park visitation data to an
      Excel spreadshhet and an html table.
'''

import argparse
import pandas as pd
import folium
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

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
      Empty Folium map.
    '''

    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48,
                     zoom_start = 3,
                     control_scale = True,
                     tiles = 'Stamen Terrain')

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
      Folium map with circle visitor markers added.
    '''

    for _, row in df[~df.lat.isnull()].iterrows():
        tooltip = (row.park_name.replace("'", r"\'")
                   + ', {:,.0f}'.format(row['2018'])
                   + ' visitors in 2018')
        folium.Circle(
            radius=row['2018']/100,
            location=[row.lat, row.long],
            tooltip=tooltip,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(map)

    return map

def plot_visitor_data(df):
    ''' Plot park visitor data.

    This function...

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of all park visitation data to export.

    Returns
    -------
    None
    '''

    fig, ax = plt.subplots()

    for _, row in df[~df.lat.isnull()].iterrows():
        ax.plot(row[10:-1]/1e6, label=row.park_name)

    ax.set_title('Park Visitors by Year')
    ax.set_xticks(ax.get_xticks()[1::5])
    ax.legend(loc='best')
    plt.xticks(rotation=90)
    plt.ylabel('Millions of Visitors')
    plt.show()

def plot_average_visitor_data(df):
    ''' Plot park visitor data.

    This function...

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of all park visitation data to export.

    Returns
    -------
    None
    '''

    fig, ax = plt.subplots()

    ax.plot(df.mean()[6:]/1e6)
    ax.set_title('Average Park Visitors by Year')
    ax.set_ylabel('Millions of Visitors')

    #ax.tick_params(labelbottom=False)
    #ax.set_xticks(ax.get_xticks()[1::5])
    #ax.legend(loc='best')
    #plt.xticks(rotation=90)

    plt.show()

def output_visitor_data_to_tables(df):
    ''' Output park visitor data.

    This function outputs the park visitor data as a table to both an
    Excel spreadsheet and an html file. The data is sorted by size,
    largest first.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of all park visitation data to export.

    Returns
    -------
    None
    '''

    map_df_export = (df[['park_name', '2018']]
                     .sort_values(by=['2018'], ascending=False)
                     .reset_index(drop=True))
    map_df_export.index += 1
    export_cols = {'park_name': 'Park Name',
                   '2018': 'Visitors in 2018'}
    map_df_export = map_df_export.rename(columns=export_cols)
    map_df_export.to_excel('_output/nps_parks_sorted_by_visitors.xlsx',
                           index=True)
    map_df_export.to_html('_output/nps_parks_sorted_by_visitors.html',
                          justify='left',
                          classes='table-park-list',
                          float_format=lambda x: '{:,.2f}'.format(x))

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

    args = parser.parse_args()

    if args.parkset:
        map_df = df[df.park_set == args.parkset]
        print("Creating park visitation map for the park set, '"
              + args.parkset + "'.")
    else:
        map_df = df
        print("Creating park visitation map for all NPS sites.")

    park_map = create_map()
    park_map = add_park_visitor_circles_to_map(park_map, map_df)
    park_map.save('_output/nps_parks_map_visitors.html')

    #plot_visitor_data(map_df)
    plot_average_visitor_data(map_df)

    output_visitor_data_to_tables(map_df)

if __name__ == '__main__':
    main()
