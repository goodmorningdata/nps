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
3) Plots including: visits per park per year, total park visits by year
   with U.S. population by year, and park visits per capita.

This script requires the following libraries: argparse, pandas,
    folium, matplotlib.

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
    * plot_park_visits_vs_us_pop : Creates plot of total visits by year
      compared to the U.S. population.
    * output_visits_data_to_tables : Output park visitation data to an
      Excel spreadshhet and an html table.
'''

import argparse
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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

def plot_visits_by_park(df, park_set, title=None):
    '''
    Plot park visits from 1904-2017 for each park in the parameter
    dataframe. Save the plot image to a .png file. This plot displays
    optimally for ~10 parks maximum.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data to plot filtered by park set
      parameter.

    park_set : str
      Set of parks in the dataframe. The dataframe, df, has already
      been filtered for this park set, but the parameter is necessary
      to be used in the plot title and output filename.

    title : Str (optional)
      Override plot title. If not sent, standard title is used.

    Returns
    -------
    None
    '''

    # Shorten the park name so that the legend will fit.
    df.loc[:,'park_name'] = df.loc[:,'park_name'].replace(
                            {'National Park':'NP', 'Mountain':'Mtn',
                             'National Recreation Area':'NRA',
                             'Memorial Parkway':'Mem Pkwy',
                             '& Preserve':''}, regex=True)
                             
    fig = plt.figure(figsize=(8,5))
    ax = plt.subplot(111)
    for _, row in df[~df.lat.isnull()].iterrows():
        # Only plot years in which the number of visits is > 0.
        plot_row = row.loc['1904':'2018']
        plot_row = plot_row[plot_row > 0]
        # Change year to int type for plotting.
        plot_row.index = plot_row.index.map(int)
        ax.plot(plot_row/1e6, label=row.park_name)

    # If a title was specified in the parameters, use it, otherwise
    # use the standard title with the addition of the park set for
    # clarification. Generate the plot image output file name using the
    # title with spaces replaced by dashses.
    if title:
        ax.set_title(title)
        filename = (title.lower().replace(' ', '_')
                    .replace(',', '')
                    .replace('(', '')
                    .replace(')', '')
                    + '.png')
    else:
        ax.set_title('Visits by year (' + park_set + ')')
        filename = ('park_visits_by_year_'
                    + park_set.lower().replace(' ','_')
                    + '.png')

    # Shrink the plot by 30% and put the legend to the right of the
    # current axis.
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
    ax.legend(bbox_to_anchor=(1, 0.5), loc='center left',
              fancybox=True, borderaxespad=2)

    # X-axis ticks are every 5th year, displayed vertically.
    #ax.set_xticks(ax.get_xticks()[1::5])
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel('Millions of Visits')
    plt.show()

    fig.savefig('_output/' + filename)

def plot_park_visits_vs_us_pop(visits_df, pop_df, park_set):
    '''
    This fuction creates two plots. The first plots total park visits
    per year in one subplot, and U.S. population for the same years in
    a second subplot. The second plots park visits per capita. Both
    plot images are saved to .png files.

    Parameters
    ----------
    visits_df : Pandas DataFrame
      DataFrame of park visit data to plot filtered by park set
      parameter.

    pop_df : Pandas DataFrame
      DataFrame of U.S. population by year.

    park_set : str
      Set of parks in the dataframe. The dataframe, df, has already
      been filtered for this park set, but the parameter is necessary
      for use in the plot title and output filename.

    Returns
    -------
    None
    '''

    # Sum visits for each year over all parks in the dataframe, re-index
    # visits dataframe with numeric years, and calculate the visits
    # per capita.
    visit_totals = pd.DataFrame(visits_df.sum().loc['1979':'2017'],
                                columns=['visitors'])
    visit_totals.index = range(1979,2018)
    visit_totals['visits_div_pop'] = (visit_totals['visitors'] /
                                      pop_df['population'].loc[1979:2018])

    # Plot total park visits and U.S. population by year.
    fig, ax = plt.subplots(2, sharex=True)
    ax[0].plot(visit_totals.index, visit_totals.visitors/1e6)
    ax[0].set_title('Total park visits (' + park_set + ')')
    ax[0].set_ylabel('Millions of visits')
    ax[1].plot(visit_totals.index, pop_df['population'].loc[1979:2018]/1e6)
    ax[1].set_title('U.S. population')
    ax[1].set_ylabel('Millions of people')
    plt.show()
    fig.savefig('_output/plot_park_visits_vs_us_pop.png')

    # Plot park visits per capita by year.
    fig, ax = plt.subplots()
    ax.plot(visit_totals.index, visit_totals.visits_div_pop)
    ax.set_title('Park visits per capita (' + park_set + ')')
    plt.show()
    fig.savefig('_output/park_visits_per_capita.png')

def plot_park_visits_hist(df, park_set):
    '''
    This function creates a histogram of park visits in bins of 1
    million visits. The plot image is saved to a .png file.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visitation data to plot.

    park_set : str
      Set of parks in the dataframe. The dataframe, df, has already
      been filtered for this park set, but the parameter is necessary
      for use in the plot title and output filename.

    Returns
    -------
    None
    '''

    fig, ax = plt.subplots()
    ax.hist(df['2018']/1e6, bins=np.arange(0,13), alpha=0.5)
    ax.set_xlabel('Millions of visits')
    ax.set_ylabel('Number of parks in millions of visits group')
    ax.set_xticks(np.arange(0,13))
    ax.set_title('Number of park visits in 2018 (' + park_set + ')')
    plt.show()

    fig.savefig('_output/park_visits_histogram.png')

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
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0, index_col=0)

    # The user can specify the set of parks to map and plot, using the
    # command line parameter, 'parkset'. If no parameter specified, all
    # park sites are added to the map.
    parser = argparse.ArgumentParser()
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

    # Filter the dataframe based on park set and print a message to
    # remind the user what set they are reporting on.
    if args.parkset:
        park_df = df[df.park_set == args.parkset]
        park_set = args.parkset + 's'
        print("Creating park visitation map and plots for the park set, '"
              + args.parkset + "'.")
    else:
        park_df = df
        park_set = 'All Parks'
        print("Creating park visitation map and plots for all NPS sites.")

    park_df = park_df.sort_values('2018', ascending=False)

    # Create the folium circle marker map.
    park_map = create_map()
    park_map = add_park_visits_circles_to_map(park_map, park_df)
    park_map.save('_output/nps_parks_map_visits.html')

    # Plot park visits by year for the top 10 and bottom 10.
    plot_visits_by_park(park_df.iloc[0:10,:], park_set,
        title = 'Park visits by year, highest 10 (' + park_set + ')')
    plot_visits_by_park(park_df[pd.notnull(park_df['2018']) & park_df['2018'] > 0].iloc[-10:,:],
        park_set, title = 'Park visits by year, lowest 10 (' + park_set + ')')

    # Plot park visits in relation to the U.S. population.
    pop_df = read_census_data()
    plot_park_visits_vs_us_pop(park_df, pop_df, park_set)

    # Run visits plot for a specific park using park code.
    plot_visits_by_park(park_df[park_df['park_code'] == 'acad'], park_set)

    # Plot histogram of park visits.
    plot_park_visits_hist(park_df, park_set)

    output_visits_data_to_tables(park_df)

if __name__ == '__main__':
    main()
