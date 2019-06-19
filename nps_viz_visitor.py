'''
This script creates a set of visualizations using the NPS visitation
data availalable from the NPS website. Visitation data is available
back to 1904.

The following visualizations are created:
1) A Folium map with park location mapped as a circle with size
   dependent on the number of park visits in 2018. Hovering over a
   circle displays a tooltip telling the user the park name and the
   number of visits in 2018.
   - Output file = nps_parks_map_visits_{designation}.html

2) A table of park visits in order of total visits, greatest number of
   visits to smallest.
   - Output files = nps_parks_sorted_by_visits_{designation}.xlsx,
                    nps_parks_sorted_by_visits_{designation}.html.
3) Plots including:
   Plot #1 - Total visits for all parks vs. year.
   Plot #2 - Visit change rate, year vs. prior year.
   Plot #3 - Estimated total visits for all parks vs. year.
   Plot #4 - Individual park visits vs. year for a set of parks.
   Plot #5 - Park visit histogram.

Required Libraries
------------------
pandas, numpy, folium, matplotlib, seaborn, sklearn

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
2) Run the script, nps_read_population_data.py to create the file,
   us_est_1900-2018.xlsx.
'''

from nps_shared import *
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from sklearn.linear_model import LinearRegression

import warnings
warnings.filterwarnings(action="ignore", message="^internal gelsd")

def create_visitor_map(df, designation):
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
    None
    '''

    # Create blank map.
    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48,
                     zoom_start = 3,
                     control_scale = True,
                     tiles = 'Stamen Terrain')

    # Add park visitor circles to map.
    for _, row in (df[~df.lat.isnull()]
        .sort_values(by='designation', ascending=False).iterrows()):

        # Create tooltip with park visits.
        tooltip = (row.park_name.replace("'", r"\'")
                  + ', {:,.0f}'.format(row[2018])
                  + " visits in 2018")

        # Add marker to map.
        folium.Circle(
            radius=row[2018]/100,
            location=[row.lat, row.long],
            tooltip=tooltip,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(map)

    # Save map to file.
    filename = ('_output/nps_parks_map_visits_'
               + designation.lower().replace(' ','_') + '.html')
    map.save(filename)

def plot_total_park_visits_vs_year(df, designation):
    '''
    Sum park visits for each year from 1904-2018 and plot the total vs.
    year. Save the plot image to a .png file.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    # Sum park visits for each year over all parks in the dataframe.
    start_col = df.columns.tolist().index(1904)
    df_tot = df.iloc[:, start_col:].sum()

    # Plot total park visits vs. year as a line plot.
    fig, ax = plt.subplots()
    ax.plot(df_tot.index, df_tot.values/1e6)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel("Millions of visits")
    plt.title("Total park visits, 1904-2018 ({})".format(designation))
    plt.show()

    # Save plot to file.
    filename = ('_output/total_park_visits_vs_year_'
               + designation.lower().replace(' ','_') + '.png')
    fig.savefig(filename)

def plot_total_park_visit_change_rate_vs_year(df, designation):
    '''
    Sum park visits for each year from 1904-2018 and calculate the
    change rate of each year to the prior year as a difference in total
    visits and as a percent. Plot each change rate vs. year. Save the
    plot image to a .png file.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    # Sum park visits for each year over all parks in the dataframe.
    start_col = df.columns.tolist().index(1904)
    df_tot = df.iloc[:, start_col:].sum().to_list()
    change_rate, change_pct = [], []

    # Calculate change rate for each year compared to the prior year
    # as a difference in total visists and as a percent.
    for i, tot in enumerate(df_tot):
        if i > 0:
            change_rate.append((df_tot[i] - df_tot[i-1])/1e6)
            change_pct.append((df_tot[i] - df_tot[i-1])/df_tot[i-1])

    # Plot change rate as number of visits vs. year.
    fig, ax = plt.subplots()
    ax.plot(range(1905, 2019), change_rate)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel("Change rate (millions of visits)")
    plt.title("Visit change rate, year to prior year, 1905-2018 ({})"
             .format(designation))
    plt.show()

    # Save plot to file.
    filename = ('_output/visit_change_rate_vs_year_'
               + designation.lower().replace(' ','_') + '.png')
    fig.savefig(filename)

    # Plot change rate as a percent of prior year visits vs. year.
    fig, ax = plt.subplots()
    ax.plot(range(1905, 2019), change_pct)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel("Change rate percent")
    plt.title("Visit change rate percent, year to prior year, 1905-2018 ({})"
             .format(designation))
    plt.show()

    # Save plot to file.
    filename = ('_output/visit_change_rate_pct_vs_year_'
               + designation.lower().replace(' ','_') + '.png')
    fig.savefig(filename)

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
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    # Subset the dataframe and use only years from "start_year"
    # forward. Sum park visits for each year over all parks in the
    # dataframe.
    start_years = [1904, 1950, 1980, 2010]
    end_year = 2040

    # Predict total visits from each start year through 2040 and plot.
    fig = plt.figure()
    for i, year in enumerate(start_years):
        # Subset dataframe - vists from start year to end year.
        start_col = df.columns.tolist().index(year)
        df_tot = df.iloc[:, start_col:].sum()

        # Fit a linear regression model and estimate visits
        regressor = LinearRegression()
        X = pd.Series(df_tot.index.values).to_frame()
        y = pd.Series(df_tot.values)
        regressor.fit(X, y)
        X_estimate = pd.Series(range(year, end_year)).to_frame()

        # Plot actual visit data and linear regression line.
        ax = fig.add_subplot(2,2,i+1)
        ax.scatter(df_tot.index, df_tot.values/1e6, s=8)
        ax.plot(X_estimate, regressor.predict(X_estimate)/1e6, color='k')
        ax.set_title("+ ~{:02.1f} million visitors per year ({})"
            .format(regressor.coef_[0]/1e6, year), fontsize=10)
        ax.set_xlim(1900, 2040)
        ax.set_ylim(0,500)

    plt.tight_layout()
    plt.show()

    # Save plot to file.
    filename = ('total_estimated_park_visits_vs_year_'
               + designation.lower().replace(' ','_') + '.png')
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
      Designation of parks in the dataframe.

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
         '& Preserve':'',
         'National Historic Site':'NHS',
         'National Memorial':'NMem',
         'National Battlefield Site':'NBS'}, regex=True)

    start_col = df.columns.tolist().index(1904)

    fig, ax = plt.subplots(figsize=(8,5))

    # Plot years with visits > 0 for each park.
    for _, row in df.iterrows():
        plot_row = row.iloc[start_col:]
        plot_row = plot_row[plot_row > 0]
        ax.plot(plot_row/1e6, label=row.park_name)

    # Use parameter title if specified, otherwise standard title.
    if title:
        plt.title(title)
        filename = (title.lower().replace(' ', '_').replace(',', '')
                    .replace('(', '').replace(')', '') + '.png')
    else:
        plt.title("Park visits by year ({})".format(designation))
        filename = ('park_visits_vs_year_' + designation.lower()
                    .replace(' ','_') + '.png')

    # Shrink the plot by 30% and put the legend to the right of the
    # current axis.
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
    ax.legend(bbox_to_anchor=(1, 0.5), loc='center left',
              fancybox=True, borderaxespad=2, fontsize=9)

    # X-axis ticks are every 10th year, displayed vertically.
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel('Millions of visits')
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
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    x_list = (df[2018].values/1e6).tolist()

    fig, ax = plt.subplots()
    ax = plt.hist(x_list, bins=12)
    plt.xlabel("Millions of visits")
    plt.ylabel("Number of parks")
    plt.title("Number of park visits in 2018 ({})".format(designation))
    plt.tight_layout()
    plt.show()

    # Save plot to file.
    filename = ('park_visits_histogram_' + designation.lower().replace(' ','_')
               + '.png')
    fig.savefig('_output/' + filename)

def output_visit_data_to_tables(df, designation):
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
    df_export.index += 1
    export_cols = {'park_name': 'Park Name', '2018': 'Visits in 2018'}
    df_export = df_export.rename(columns=export_cols)

    filename = ('_output/nps_parks_sorted_by_visits_'
               + designation.lower().replace(' ','_'))
    df_export.to_excel(filename + '.xlsx', index=True)
    df_export.to_html(filename + '.html', justify='left',
        classes='table-park-list', float_format=lambda x: '{:,.2f}'.format(x))

def main():
    df_park, designation = get_parks_df(warning=['location', 'visitor'])

    # Parks with visitors recorded in 2018.
    df_2018 = df_park[~df_park[2018].isnull()]
    df_2018 = df_2018[df_2018[2018] > 0.0]
    df_2018 = df_2018.sort_values(by=[2018], ascending=False)

    # Map #1 - Plot park locations as a circle with size corresponding
    # to the number of visits in 2018.
    create_visitor_map(df_2018, designation)

    # Plot #1 - Total visits for all parks vs. year.
    plot_total_park_visits_vs_year(df_park, designation)

    # Plot #2 - Visit change rate, year vs. prior year.
    plot_total_park_visit_change_rate_vs_year(df_park, designation)

    # Plot #3 - Estimated future visits for all parks vs. year.
    plot_total_estimated_park_visits_vs_year(df_park, designation)

    # Plot #4 - Individual park visits vs. year for a set of parks.
    plot_title = "Park visits by year, highest 10 ({})".format(designation)
    plot_park_visits_vs_year(df_2018.iloc[0:10,:].copy(), designation,
        title = plot_title)

    plot_title = "Park visits by year, lowest 10 ({})".format(designation)
    plot_park_visits_vs_year(df_2018.iloc[-10:,:].copy(), designation,
        title = plot_title)

    # Plot park visits by year for just one park.
    #plot_park_visits_vs_year(df_park[df_park['park_code'] == 'acad'],
    #                         "Acadia NP")

    # Plot #5 - Histogram - 2018 visits by park
    plot_park_visits_histogram(df_2018, designation)

    # Save park visit data as an Excel spreadsheet and an html table.
    output_visit_data_to_tables(df_2018, designation)

if __name__ == '__main__':
    main()
