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
   - Output files = visit_parks_sorted_by_visits_{designation}.xlsx,
                    visit_parks_sorted_by_visits_{designation}.html.

3) A table of park visits per acre in descending order.
   - Output files = visit_park_visits_per_acre_{designation}.xlsx,
                    visit_parks_sorted_by_visits_{designation}.html.

3) Plots including:
   Plot #1 - Total visits for all parks vs. year.
   Plot #2 - Visit change rate, year vs. prior year.
   Plot #3 - Estimated total visits for all parks vs. year.
   Plot #4 - Individual park visits vs. year for a set of parks.
   Plot #5 - Park visit histogram.
   Plot #6 - Park visits per acre histogram.

Required Libraries
------------------
math, pandas, numpy, folium, matplotlib, seaborn, sklearn

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
2) Run the script, nps_read_population_data.py to create the file,
   us_est_1900-2018.xlsx.
'''

from nps_shared import *
import math
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
    map.save(set_filename('visit_map', 'html', designation))

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
    plt.title(set_title("Total park visits, 1904-2018", designation))
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('visit_total_park_visits_vs_year', 'png',
                             designation))

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
    plt.title(set_title("Visit change rate, year to prior year, 1905-2018",
                        designation))
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('visit_change_rate_vs_year', 'png', designation))

    # Plot change rate as a percent of prior year visits vs. year.
    fig, ax = plt.subplots()
    ax.plot(range(1905, 2019), change_pct)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel("Change percent")
    plt.title(set_title("Visit change percent, year to prior year, 1905-2018",
                        designation))
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('visit_change_pct_vs_year', 'png', designation))

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
        title = set_title("+ ~{:02.1f} million visitors per year".format(regressor.coef_[0]/1e6), designation)
        ax.set_title(title, fontsize=10)
        ax.set_xlim(1900, 2040)
        ax.set_ylim(0,500)

    plt.tight_layout()
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('visit_total_estimated_park_visits_vs_year',
                             'png', designation))

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

    start_col = df.columns.tolist().index(1904)

    fig, ax = plt.subplots(figsize=(8,5))

    # Plot years with visits > 0 for each park.
    for _, row in df.iterrows():
        plot_row = row.iloc[start_col:]
        plot_row = plot_row[plot_row > 0]
        ax.plot(plot_row/1e6, label=row.park_name_abbrev)

    # Use parameter title if specified, otherwise standard title.
    if len(title) == 0:
        title = "Park visits vs. year"

    # Shrink the plot by 30% and put the legend to the right of the
    # current axis.
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
    ax.legend(bbox_to_anchor=(1, 0.5), loc='center left',
              fancybox=True, borderaxespad=2, fontsize=9)

    plt.title(set_title(title, designation))

    # X-axis ticks are every 10th year, displayed vertically.
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90)
    plt.ylabel('Millions of visits')
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('visit_' + title, 'png', designation))

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

    # List of park visits in millions of visits.
    x_list = (df[2018].values/1e6)

    # Mean and median text box.
    mean = df[2018].mean()/1e6
    median = np.median(df[2018])/1e6
    text_string = '$\mu=%.2f$\n$\mathrm{median}=%.2f$'%(mean, median)

    # matplotlib.patch.Patch properties.
    props = dict(facecolor='white', alpha=0.5)

    # Create park visit histogram.
    fig, ax = plt.subplots()
    ax.hist(x_list, bins=list(range(math.ceil(max(x_list)) + 1)), alpha=0.8)
    ax.text(0.96, 0.95, text_string,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=props)
    plt.xlabel("Millions of visits")
    plt.ylabel("Number of parks")
    plt.title(set_title("Number of park visits in 2018", designation))
    plt.tight_layout()
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('visit_histogram', 'png', designation))

def plot_park_visits_per_acre_histogram(df, designation):
    '''
    This function creates a histogram of park visits per acre. The
    plot image is saved to a .png file.

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

    # List of park visits in millions of visits.
    df = df[df.park_code != 'jeff'].copy()
    df['visits_per_acre'] = df[2018]/df.gross_area_acres
    x_list = df['visits_per_acre'].values

    # Mean and median text box.
    mean = df.visits_per_acre.mean()
    median = np.median(df.visits_per_acre)
    text_string = '$\mu=%.2f$\n$\mathrm{median}=%.2f$'%(mean, median)

    # matplotlib.patch.Patch properties.
    props = dict(facecolor='white', alpha=0.5)

    # Create park visit histogram.
    fig, ax = plt.subplots()
    ax.hist(x_list, alpha=0.8, bins=np.arange(0, 350, 25))
    ax.text(0.96, 0.95, text_string,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=props)
    plt.xlabel("Vists per acre")
    plt.ylabel("Number of parks")
    # The spaces are hacky, but title and suptitle do not center together.
    plt.suptitle(set_title("      Number of park visits per acre in 2018", designation))
    plt.title("Gateway Arch NP is not included because it is such an extreme outlier.", size=10)
    plt.tight_layout(rect=[0, 0.02, 1, 0.98])
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('visits_per_acre_histogram', 'png', designation))

def output_park_visits_per_acre(df, designation):
    '''
    This function outputs the park visits per acre data as a table
    to both an Excel spreadsheet and an html file. The data is sorted
    by number of visits, largest first.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data to export.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    df['visits_per_acre'] = df[2018]/df.gross_area_acres
    df = df.round(0)
    df_export = (df[['park_name', 'gross_area_acres', 'visits_per_acre']]
                .sort_values(by=['visits_per_acre'], ascending=False)
                .reset_index(drop=True))

    df_export.index += 1

    print(df_export)

    df_export['visits_per_acre'].replace(
        to_replace=0, value="<1", regex=True, inplace=True)

    export_cols = {'park_name': 'Park Name', 'gross_area_acres': 'Park size (acres)', 'visits_per_acre': 'Visits per acre in 2018'}
    df_export = df_export.rename(columns=export_cols)

    filename = set_filename('visit_park_visits_per_acre', designation=designation)

    df_export.to_excel(filename + 'xlsx', index=True)
    df_export.to_html(filename + 'html', justify='left',
        classes='table-park-list', float_format=lambda x: '{:,.0f}'.format(x))

def output_visit_data_to_tables(df, designation):
    '''
    This function outputs the park visit data as a table to both an
    Excel spreadsheet and an html file. The data is sorted by number of
    visits, largest first.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data to export.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    # Export all parks in the dataframe.
    df_export = (df[['park_name', 2018]]
                .sort_values(by=[2018], ascending=False)
                .reset_index(drop=True))
    df_export.index += 1
    export_cols = {'park_name': 'Park Name', 2018: 'Visits in 2018'}
    df_export = df_export.rename(columns=export_cols)

    filename = set_filename('visit_parks_sorted_by_visits', designation=designation)

    df_export.to_excel(filename + 'xlsx', index=True)
    df_export.to_html(filename + 'html', justify='left',
        classes='table-park-list', float_format=lambda x: '{:,.0f}'.format(x))

    # Export the top 10 parks in the dataframe.
    df_export_top_10 = df_export.head(10)

    filename = set_filename('visit_parks_sorted_by_visits_top_10', designation=designation)

    df_export_top_10.to_excel(filename + 'xlsx', index=True)
    df_export_top_10.to_html(filename + 'html', justify='left',
        classes='table-park-list', float_format=lambda x: '{:,.0f}'.format(x))

def output_total_visit_data_to_tables(df, designation):
    '''
    This function outputs the total park visit data by year as a
    table to both an Excel spreadsheet and an html file. The data is
    sorted by year.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data to export.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    start_col = df.columns.tolist().index(1904)
    df_export = df.iloc[:, start_col:].sum()
    df_export = df_export.to_frame()
    df_export.columns = ['Total Visits']

    filename = set_filename('visit_total_park_visits_by_year', designation=designation)

    df_export.to_excel(filename + 'xlsx', index=True,
        index_label='Year', float_format='%.2f')
    df_export.to_html(filename + 'html', justify='left', index=True,
        classes='table-park-list', float_format=lambda x: '{:,.0f}'.format(x))

def main():
    df_park, designation = get_parks_df(warning=['location', 'visitor'])

    # Parks with visitors recorded in 2018.
    df_2018 = df_park[~df_park[2018].isnull()]
    df_2018 = df_2018[df_2018[2018] > 0.0]
    df_2018 = df_2018.sort_values(by=[2018], ascending=False)

    # Print statistical info for dataframe.
    print(df_2018[2018].describe(), '\n')

    # Map #1 - Plot park locations as a circle with size corresponding
    # to the number of visits in 2018.
    #create_visitor_map(df_2018, designation)

    # Plot #1 - Total visits for all parks vs. year.
    #plot_total_park_visits_vs_year(df_park, designation)

    # Plot #2 - Visit change rate, year vs. prior year.
    #plot_total_park_visit_change_rate_vs_year(df_park, designation)

    # Plot #3 - Estimated future visits for all parks vs. year.
    #plot_total_estimated_park_visits_vs_year(df_park, designation)

    # Plot #4 - Individual park visits vs. year for a set of parks.
    #plot_park_visits_vs_year(df_2018.iloc[0:10,:].copy(), designation,
    #    title = "Park visits vs. year, highest 10")

    #plot_park_visits_vs_year(df_2018.iloc[-10:,:].copy(), designation,
    #    title = "Park visits vs. year, lowest 10")

    # Plot park visits by year for just one park.
    #plot_park_visits_vs_year(df_park[df_park['park_code'] == 'acad'],
    #                         "Acadia NP")

    # Plot #5 - Histogram - 2018 visits by park
    #plot_park_visits_histogram(df_2018, designation)

    # Plot #6 - Park visits per acre histogram.
    plot_park_visits_per_acre_histogram(df_park, designation)

    # Save park visits per acre table.
    output_park_visits_per_acre(df_park, designation)

    # Save park visit data.
    output_visit_data_to_tables(df_2018, designation)

    # Save total park visit data by year.
    output_total_visit_data_to_tables(df_park, designation)

if __name__ == '__main__':
    main()
