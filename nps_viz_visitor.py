'''Create maps and plots of National Park Service visitation data.

Park visitation data is available starting fro 1979 from the nps.gov.

This script generates the following visualizations of National Park
visitation data.
1) A Folium map with park location mapped as a circle with size
   dependent on number of park visits in the most recent year that the
   data is available. Circle markers have a tooltip telling the user
   the park name and the number of visits.
   - Output file = nps_parks_map_visits.html
2) A table of park visits in order of total, greatest number of visits
   to smallest.
   - Output files = nps_parks_sorted_by_visits.xlsx,
                    nps_parks_sorted_by_visits.html.
3)

This script requires the following libraries: argparse, pandas, folium,
    matplotlib.

Dependencies:

    * Run the script, nps_create_master_df.py to create the file,
      nps_parks_master_df.xlsx.
    * Run the script, nps_read_population_data.py to create the file,
      us_est_1970-2017.xlsx.

This script contains the following functions:

    * create_map : creates a Folium map.
    * add_park_visits_circles_to_map : Adds circle markers corresponding
      to park visits to map.
    * plot_park_visits : Creates a plot of park visits from 1979-2018.
    * plot_total_park_visits :
    * output_visits_data_to_tables : Output park visitation data to an
      Excel spreadshhet and an html table.
'''

import argparse
import pandas as pd
import folium
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

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

def add_park_visits_circles_to_map(map, df):
    '''
    This function adds a circle marker for each park in the parameter
    dataframe to the map. The circle size corresponds to the number of
    visits to the park in the most recent calendar year that the data
    is available.

    These markers provide the park name and number of vists as a
    tooltip. A tooltip instead of a popup is used for this map because
    the popup was less sensitive for the circle markers.

    Parameters
    ----------
    map : Folium map object
      Folium map to add circle markers to.

    df : Pandas DataFrame
      DataFrame of parks to add to the map.

    Returns
    -------
    map : Folium map object
      Folium map with circle visit markers added.
    '''

    for _, row in df[~df.lat.isnull()].iterrows():
        tooltip = (row.park_name.replace("'", r"\'")
                   + ', {:,.0f}'.format(row['2018'])
                   + ' visits in 2018')
        folium.Circle(
            radius=row['2018']/100,
            location=[row.lat, row.long],
            tooltip=tooltip,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(map)

    return map

def read_census_data():
    '''
    Read census population data from the Excel file,
    us_est_1970-2017.xlsx, created by the script,
    nps_read_population_data.py, into a dataframe to be used for
    plotting.

    Parameters
    ----------
    None

    Returns
    -------
    pop_df : Pandas DataFrame
      DataFrame of U.S. population by year and state (when available)
    '''

    pop_df = pd.read_excel(
             '_census_data/us_est_1970-2017.xlsx',
              header=0, index=False)
    pop_df = pop_df.groupby('year').sum()

    return pop_df

def plot_visits_by_park(df):
    '''
    Plot park visits from 1979-2017 for each park in the
    parameter dataframe. This is not a very helpful plot as plotting
    even just national parks adds 60 lines to the plot and makes it
    difficult to read.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data to plot filtered by park set
      parameter.

    Returns
    -------
    None
    '''

    fig, ax = plt.subplots()

    for _, row in df[~df.lat.isnull()].iterrows():
        ax.plot(row[10:-1]/1e6, label=row.park_name)

    ax.set_title('Park Visits by Year')
    ax.set_xticks(ax.get_xticks()[1::5])
    #ax.legend(loc='best')
    plt.xticks(rotation=90)
    plt.ylabel('Millions of Visits')
    plt.show()

def plot_total_park_visits(visits_df, pop_df):
    '''
    This fuction creates two plots. The first plots total park visits
    per year in one subplot, and U.S. population for the same years in
    a second subplot. The second plots park visits per capita.

    Parameters
    ----------
    visits_df : Pandas DataFrame
      DataFrame of park visit data to plot filtered by park set
      parameter.

    pop_df : Pandas DataFrame
      DataFrame of U.S. population by year.

    Returns
    -------
    None
    '''

    visit_totals = pd.DataFrame(visits_df.sum().loc['1979':'2017'],
                                  columns=['visitors'])
    visit_totals.index = range(1979,2018)
    visit_totals['visits_div_pop'] = (visit_totals['visitors'] /
                                      pop_df['population'].loc[1979:2018])

    fig, ax = plt.subplots(2, sharex=True)
    ax[0].plot(visit_totals.index, visit_totals.visitors/1e6)
    ax[0].set_title('Total park visits')
    ax[0].set_ylabel('Millions of people')
    ax[1].plot(visit_totals.index, pop_df['population'].loc[1979:2018])
    ax[1].set_title('U.S. population')
    ax[1].set_ylabel('Millions of people')
    plt.show()
    fig.savefig('_output/total_park_visits.png')

    fig, ax = plt.subplots()
    ax.plot(visit_totals.index, visit_totals.visits_div_pop)
    ax.set_title('Park visits per capita')
    plt.show()
    fig.savefig('_output/park_visits_per_capita.png')

def output_visits_data_to_tables(df):
    '''
    This function outputs the park visit data as a table to both an
    Excel spreadsheet and an html file. The data is sorted by number of
    visits, largest first.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visitation data to export.

    Returns
    -------
    None
    '''

    df_export = (df[['park_name', '2018']]
                 .sort_values(by=['2018'], ascending=False)
                 .reset_index(drop=True))
    df_export.index += 1
    export_cols = {'park_name': 'Park Name',
                   '2018': 'Visits in 2018'}
    df_export = df_export.rename(columns=export_cols)
    df_export.to_excel('_output/nps_parks_sorted_by_visits.xlsx',
                       index=True)
    df_export.to_html('_output/nps_parks_sorted_by_visits.html',
                      justify='left',
                      classes='table-park-list',
                      float_format=lambda x: '{:,.2f}'.format(x))

def main():
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    parser = argparse.ArgumentParser()

    # The user can specify the set of parks to map and plot, using the
    # command line parameter, 'parkset'. If no parameter specified, all
    # park sites are added to the map.
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
        print("Creating park visitation map and plots for the park set, '"
              + args.parkset + "'.")
    else:
        map_df = df
        print("Creating park visitation map and plots for all NPS sites.")

    park_map = create_map()
    park_map = add_park_visits_circles_to_map(park_map, map_df)
    park_map.save('_output/nps_parks_map_visits.html')

    pop_df = read_census_data()

    #plot_visits_by_park(map_df)
    #plot_total_park_visits(map_df, pop_df)

    # Plot for specific parks.
    #park_map_df = map_df[map_df['park_code'] == 'grca']
    #print(park_map_df)
    plot_visits_by_park(map_df[map_df['park_code'] == 'gaar'])

    output_visits_data_to_tables(map_df)

if __name__ == '__main__':
    main()
