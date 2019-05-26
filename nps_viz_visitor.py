'''
This script creates a set of visualizations using the NPS visitation
data availalable from the NPS website. Visitation data is available
back to 1904.

The following visualizations are created:
1) A Folium map with park location mapped as a circle with size
   dependent on the number of park visits in 2018. Hovering over a
   circle displays a tooltip telling the user the park name and the
   number of visits in 2018.
   - Output file = nps_parks_map_visits.html
2) A table of park visits in order of total visits, greatest number of
   visits to smallest.
   - Output files = nps_parks_sorted_by_visits.xlsx,
                    nps_parks_sorted_by_visits.html.
3) Plots including:
   Plot #1 - Total visits for all parks vs. year.
   Plot #2 - Estimated total visits for all parks vs. year.
   Plot #3 - Individual park visits vs. year for a set of parks.
   Plot #4 - Park visit histogram.

Required Libraries
------------------
argparse, pandas, numpy, folium, matplotlib, seaborn, sklearn

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
2) Run the script, nps_read_population_data.py to create the file,
   us_est_1900-2018.xlsx.
'''

import argparse
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from sklearn.linear_model import LinearRegression

import warnings
warnings.filterwarnings(action="ignore", message="^internal gelsd")

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

def add_park_visit_circles_to_map(map, df):
    '''
    This function adds a circle marker for each park in the parameter
    dataframe to the map. The circle size corresponds to the number of
    visits to the park in 2018. Hovering over the marker shows a
    tooltip which lists the park name and total visits in 2018.

    Parameters
    ----------
    map : Folium map object
      Folium map to add circle markers to.

    df : Pandas DataFrame
      DataFrame of parks to add to map.

    Returns
    -------
    map : Folium map object
      Folium map with circle visit markers added.
    '''

    for _, row in df[~df.lat.isnull()].iterrows():
        tooltip = (row.park_name.replace("'", r"\'")
                   + ', {:,.0f}'.format(row[2018])
                   + " visits in 2018")
        folium.Circle(
            radius=row[2018]/100,
            location=[row.lat, row.long],
            tooltip=tooltip,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(map)

    return map

def output_visit_data_to_tables(df):
    '''
    This function outputs the park visit data as a table to both an
    Excel spreadsheet and an html file. The data is sorted by number of
    visits, largest first.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data to export.

    Returns
    -------
    None
    '''

    df_export = (df[['park_name', 2018]]
                 .sort_values(by=[2018], ascending=False)
                 .reset_index(drop=True))
    df_export = df_export[~df_export[2018].isnull()]
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

def plot_total_park_visits_vs_year(df, designation):
    '''
    Sum park visits for each year from 1904-2018 and plot the total vs.
    year. Save the plot image to a .png file.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data.

    designation : str
      Designation of parks in the dataframe. The dataframe, df, has
      already been filtered for this park set, but the parameter is
      necessary for the plot title and output filename.

    Returns
    -------
    None
    '''

    # Sum park visits for each year over all parks in the dataframe.
    start_col = df.columns.tolist().index(1904)
    tot_df = df.iloc[:, start_col:].sum()
    fig, ax = plt.subplots()
    ax.plot(tot_df.index, tot_df.values/1e6)

    # X-axis ticks are every 10th year, displayed vertically.
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel("Millions of Visits")
    ax.set_title("Total park visits, 1904-2018 ({})".format(designation))
    plt.show()

    # Save plot to file.
    filename = ('total_park_visits_vs_year_'
                + designation.lower().replace(' ','_')
                + '.png')
    fig.savefig('_output/' + filename)

def plot_total_estimated_park_visits_vs_year(df, designation):
    '''
    Fit a Linear Regression classifier to the park visit data and use
    this classifier to predict park visit totals in the future. Plot
    both the actual visit data and the predicted future visit totals.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data to plot filtered by park set
      parameter.

    designation : str
      Designation of parks in the dataframe. The dataframe, df, has
      already been filtered for this park set, but the parameter is
      necessary for the plot title and output filename.

    Returns
    -------
    None
    '''

    # Subset the dataframe and use only years from "start_year"
    # forward. Sum park visits for each year over all parks in the
    # dataframe.
    start_year = 2010
    start_col = df.columns.tolist().index(start_year)
    tot_df = df.iloc[:, start_col:].sum()

    # Create a linear regression classifier and fit it to the park
    # visit total data back to the value of start_year. Use the
    # classifier to predict future visit totals.
    regressor = LinearRegression()
    X = pd.Series(tot_df.index.values).to_frame()
    y = pd.Series(tot_df.values)
    regressor.fit(X, y)
    X_estimate = pd.Series(range(start_year, 2041)).to_frame()

    # Plot both the actual visit data as a scatter plot and the linear
    # regression line.
    fig, ax = plt.subplots()
    ax.scatter(tot_df.index, tot_df.values/1e6)
    plt.plot(X_estimate, regressor.predict(X_estimate)/1e6, color='k')

    # X-axis ticks are every 5th year, displayed vertically.
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    plt.xticks(rotation=90)
    plt.ylabel("Millions of Visits")
    plt.suptitle("Total park visits, future estimate ({})"
                 .format(designation), fontsize=12)
    plt.title("+ ~{:02.1f} million visitors per year"
              .format(regressor.coef_[0]/1e6), fontsize=10)
    plt.show()

    # Save plot to file.
    filename = ('total_estimated_park_visits_vs_year_'
                + designation.lower().replace(' ','_')
                + '.png')
    fig.savefig('_output/' + filename)

def plot_park_visits_vs_year(df, designation, title=None):
    '''
    Plot park visits from 1904-2018 for each park in the parameter
    dataframe. Save the plot image to a .png file. This plot displays
    optimally for ~10 parks maximum.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data to plot filtered by park set
      parameter.

    designation : str
      Designation of parks in the dataframe. The dataframe, df, has
      already been filtered for this park set, but the parameter is
      necessary for the plot title and output filename.

    title : str (optional)
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

    start_col = df.columns.tolist().index(1904)

    fig = plt.figure(figsize=(8,5))
    ax = plt.subplot(111)
    for _, row in df[~df.lat.isnull()].iterrows():
        # Only plot years in which the number of visits is > 0.
        plot_row = row.iloc[start_col:]
        plot_row = plot_row[plot_row > 0]
        ax.plot(plot_row/1e6, label=row.park_name)

    # If a title was specified in the parameters, use it, otherwise
    # use the standard title with the addition of the designation for
    # clarification. Generate the plot image output file name using the
    # title with spaces replaced by dashses.
    if title:
        ax.set_title(title)
        filename = (title.lower().replace(' ', '_').replace(',', '')
                    .replace('(', '').replace(')', '') + '.png')
    else:
        ax.set_title("Park visits by year ({})".format(designation))
        filename = ('park_visits_vs_year_' + designation.lower()
                    .replace(' ','_') + '.png')

    # Shrink the plot by 30% and put the legend to the right of the
    # current axis.
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
    ax.legend(bbox_to_anchor=(1, 0.5), loc='center left',
              fancybox=True, borderaxespad=2)

    # X-axis ticks are every 10th year, displayed vertically.
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel('Millions of Visits')
    plt.show()

    # Save plot to file.
    fig.savefig('_output/' + filename)

def plot_park_visits_histogram(df, designation):
    '''
    This function creates a histogram of park visits in bins of 1
    million visits. The plot image is saved to a .png file.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visitation data to plot.

    designation : str
      Designation of parks in the dataframe. The dataframe, df, has
      already been filtered for this park set, but the parameter is
      necessary for the plot title and output filename.

    Returns
    -------
    None
    '''

    x_list = (df[2018].values/1e6).tolist()
    fig, ax = plt.subplots()
    ax = sns.distplot(x_list, bins=12, rug=True, kde=False)
    ax.set_xlabel("Millions of visits")
    ax.set_ylabel("Number of parks")
    ax.set_title("Number of park visits in 2018 ({})".format(designation))
    plt.show()

    # Save plot to file.
    filename = ('park_visits_histogram_'
                + designation.lower().replace(' ','_')
                + '.png')
    fig.savefig('_output/' + filename)

def main():
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0, index_col=0)

    # Use Seaborn formatting for plots and set color palette.
    sns.set()
    sns.set_palette('Dark2')

    # The user can specify the set of parks to map and plot, using the
    # command line parameter, 'parkset'. If no parameter specified, all
    # park sites are added to the map.
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--designation', type=str,
           help = "Set of parks for which to display locations. If not \
                  specified, all park sites will be mapped.\
                  Possible values are: 'International Historic Sites',\
                  'National Battlefields', 'National Battlefield Parks',\
                  'National Battlefield Sites', 'National Military Parks',\ 'National Historical Parks', 'National Historic Sites',\
                  'National Lakeshores', 'National Memorials',\
                  'National Monuments', 'National Parks', 'National Parkways',\ 'National Preserves', 'National Reserves',\
                  'National Recreation Areas', 'National Rivers',\
                  'National Wild and Scenic Rivers and Riverways',\
                  'National Scenic Trails', 'National Seashores',\
                  'Other Designations'")
    args = parser.parse_args()

    # Filter the dataframe based on designation and remind user which
    # park designations will be in the visualizations.
    # Filter the dataframe based on designation and remind user which
    # park designations will be in the visualizations.
    if args.designation:
        park_df = df[df.designation == args.designation]
        print("\nCreating park visit map for the park designation, {}."
              .format(args.designation))
        designation = args.designation
    else:
        park_df = df
        print("\nCreating park visit map for all NPS sites.")
        designation = "All Parks"

    # Check for parks missing location.
    missing_loc = park_df[park_df.lat.isnull()].park_name
    if missing_loc.size:
        print("\n** Warning ** ")
        print("Park sites with missing lat/long from API, so no location "
              "available. These park sites will not be added to the map.")
        print(*missing_loc, sep=', ')
        print("Total parks missing location: {}".format(len(missing_loc)))

    # Check for parks missing visitor data and remove from dataframe.
    missing_visit = park_df[park_df[2018].isnull()].park_name
    if missing_visit.size:
        print("\n** Warning **")
        print("Park sites not included in the NPS Visitor Use Statistics "
              "report, so no park visit data available. These park sites will "
              "not be added to the map or plots.")
        print(*missing_visit, sep=', ')
        print("** Total parks missing visit data: {}\n"
              .format(len(missing_visit)))
        park_df = park_df[~park_df[2018].isnull()]

    park_df = park_df.sort_values(by=2018, ascending=False)

    # Map #1 - Plot park locations as a circle with size corresponding
    # to the number of visits in 2018.
    park_map = create_map()
    park_map = add_park_visit_circles_to_map(park_map, park_df)
    park_map.save('_output/nps_parks_map_visits.html')

    # Save park visit data as an Excel spreadsheet and an html table.
    output_visit_data_to_tables(park_df)

    # Plot #1 - Total visits for all parks vs. year.
    plot_total_park_visits_vs_year(park_df, designation)

    # Plot #2 - Estimated future visits for all parks vs. year.
    plot_total_estimated_park_visits_vs_year(park_df, designation)

    # Plot #3 - Individual park visits vs. year for a set of parks.
    plot_title = "Park visits by year, highest 10 ({})".format(designation)
    plot_park_visits_vs_year(park_df.iloc[0:10,:], designation,
                             title = plot_title)
    plot_title = "Park visits by year, lowest 10 ({})".format(designation)
    plot_park_visits_vs_year(park_df.iloc[-10:,:], designation,
                             title = plot_title)
    # Plot park visits by year for just one park.
    #plot_park_visits_vs_year(park_df[park_df['park_code'] == 'acad'],
    #                         "Acadia NP")

    # Plot #4 - Histogram - visits by park in bins of 1 million visits
    plot_park_visits_histogram(park_df, designation)

if __name__ == '__main__':
    main()
