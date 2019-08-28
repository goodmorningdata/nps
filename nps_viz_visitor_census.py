'''
This script creates a set of visualizations using the NPS visitation
data availalable from the NPS website and census data avialable from
census.gov.

The following visualizations are created:
1) Plots including:
   Plot #1 - Park visits and U.S. population vs. year
   Plot #2 - Total park visits per capita
   Plot #3 - Total park visits per capita - grid of 4 parks
   Plot #4 - Park visits per capita vs. rate of change quadrant
   TODO - Plot #5 - Total sites in the NPS system per year.
   TODO - Plot #6 - Total sites per person per year.

Required Libraries
------------------
nps_shared, pandas, numpy, matplotlib, scipy

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
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.stats import linregress

def read_census_data():
    '''
    Read census population data from the Excel file,
    us_est_1900-2018.xlsx, created by the script,
    nps_read_population_data.py, into a dataframe to be used for
    plotting.

    Parameters
    ----------
    None

    Returns
    -------
    df_pop : Pandas DataFrame
      DataFrame of U.S. population by year and state (when available)
    '''

    df_pop = pd.read_excel(
             '_census_data/us_est_1900-2018.xlsx',
              header=0, index=False)
    df_pop = df_pop.groupby('year').sum()

    return df_pop

def park_visits_and_us_pop_vs_year(df_tot, df_pop, designation):
    '''
    This fuction plots total park visits per year in one subplot, and
    U.S. population for the same years in a second subplot. Data is
    plotted for 1904-2018.

    Parameters
    ----------
    df_tot : Pandas DataFrame
      DataFrame of total park visits per year.

    df_pop : Pandas DataFrame
      DataFrame of U.S. population by year.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    # Plot total park visits and U.S. population by year.
    fig, ax = plt.subplots(2, sharex=True)
    ax[0].plot(df_tot.index, df_tot.values/1e6)
    ax[0].set_title(set_title("Total park visits", designation))
    ax[0].set_ylabel("Millions of visits")
    ax[0].set_ylim(bottom=0, top=350)

    ax[1].plot(df_pop.index, df_pop['population']/1e6)
    ax[1].set_title("U.S. population" )
    ax[1].set_ylabel("Millions of people")
    ax[1].set_ylim(bottom=0, top=350)
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('census_park_visits_vs_us_pop',
                             'png', designation))

def total_park_visits_per_cap_vs_year(df_tot, df_pop, designation, title=""):
    '''
    This function plots park visits per capita for 1904-2018. A linear
    regression line is added for the years 1967-2018. 1967 is the
    first year that a dip in per capita visits for all parks is seen
    since the end of World War II. Growth since 1967 is assumed to
    indicate current park visit growth.

    Parameters
    ----------
    df_tot : Pandas DataFrame
      DataFrame of total park visits per year.

    df_pop : Pandas DataFrame
      DataFrame of U.S. population by year.

    designation : str
      Designation of parks in the dataframe.

    title : str (optional)
      Plot title to use instead of default.

    Returns
    -------
    None
    '''

    # Calculate park visits per capita
    df_tot['visits_div_pop'] = df_tot.total_visits / df_pop.population
    df_tot['diff_visits_div_pop'] = df_tot.visits_div_pop.diff()
    df_tot.replace(0.0, np.nan, inplace=True)

    # ** Uncomment following code to find the first decrease in per
    # capita visits since 1965 **
    # df_1965 = df_tot.loc[1965:]
    # first_dec_yr = df_1965.index[df_1965.diff_visits_div_pop < 0].tolist()[0]
    # print("First visits per capita decrease year since 1965 is "
    #       "{}".format(first_dec_yr))

    first_dec_yr = 1967
    first_positive_yr = 1904
    df_tot_zero = df_tot[df_tot.visits_div_pop == 0.0]
    if len(df_tot_zero) > 0:
        first_positive_yr = df_tot_zero.index[-1]
    start_year = max(first_dec_yr, first_positive_yr)

    df_dec = df_tot.loc[start_year:]

    # Calculate average per capita visits from first decrease year to 2018.
    per_capita_mean = df_dec.mean().visits_div_pop

    regress_x = df_dec.index
    regress_y = df_dec.visits_div_pop
    stats = linregress(regress_x, regress_y)
    m = stats.slope
    b = stats.intercept

    # Add a text box to the plot with plot stats.
    text_string = ("Mean per capita visits since {} = "
                   "{:.4f}\nRegression line slope = {:.4f}".format(first_dec_yr, per_capita_mean, stats.slope))
    props = dict(facecolor='white', alpha=0.5)

    # Use parameter title if specified, otherwise standard title.
    if len(title) == 0:
        title = set_title("Park visits per capita vs. year", designation)

    # Plot park visits per capita vs. year.
    fig, ax1 = plt.subplots()
    ax1.text(0.05, 0.95, text_string,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment='top', horizontalalignment='left',
            bbox=props)
    ax1.plot(df_tot.index, df_tot.visits_div_pop, label='Visits per capita')
    ax1.set_ylabel("Visits per capita")

    # Plot regression line.
    ax1.plot(regress_x, m*regress_x + b, '--', alpha=0.5)

    # Plot park visits vs. year.
    ax2 = ax1.twinx()
    ax2.plot(df_tot.index, df_tot.total_visits/1e6, color='blue', alpha=0.1, label='Total visits')
    ax2.set_ylabel("Total visits (millions of visits)")

    # Add legend.
    fig.legend(loc="lower right",
               bbox_to_anchor=(1, 0),
               bbox_transform=ax1.transAxes)

    plt.title(title)
    fig.tight_layout()
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('census_' + title, 'png'))

def total_park_visits_per_cap_vs_year_4(df_parks, df_pop):
    '''
    This function plots park visits per capita for 1904-2018 for 4
    parks in subplots. A linear regression line is added for the years
    1967-2018. 1967 is the first year that a dip in per capita visits
    for all parks is seen since the end of World War II. Growth since
    1967 is assumed to indicate current park visit growth.

    Parameters
    ----------
    df_parks : Pandas DataFrame
      DataFrame of 4 parks to plot.

    df_pop : Pandas DataFrame
      DataFrame of U.S. population by year.

    Returns
    -------
    None
    '''

    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True)
    title = 'Park visits per capita vs. year (4 parks)'
    fig.suptitle(title)

    # Park dataframe counter.
    p = 0

    for i in range(0,2):
        for j in range(0,2):
            # Format for plotting and calculate the per capita visits.
            df_tot = get_visit_df(df_parks.iloc[p].to_frame().T)
            df_tot['visits_div_pop'] = df_tot.total_visits / df_pop.population

            # Limit years to those with > 0 visits, 1967 or later.
            first_dec_yr = 1967
            first_positive_yr = 1904
            df_tot_zero = df_tot[df_tot.visits_div_pop == 0.0]
            if len(df_tot_zero) > 0:
                first_positive_yr = df_tot_zero.index[-1]
            start_year = max(first_dec_yr, first_positive_yr)

            df_plot = df_tot.loc[start_year:]
            per_capita_mean = df_plot.mean().visits_div_pop

            # Fit a regression line to the per capita visits
            regress_x = df_plot.index
            regress_y = df_plot.visits_div_pop
            stats = linregress(regress_x, regress_y)
            m = stats.slope
            b = stats.intercept

            # Don't plot years with zero values.
            df_plot.replace(0.0, np.nan, inplace=True)

            # Add subplot title.
            ax_title = df_parks.iloc[p].park_name_abbrev
            props = dict(facecolor='white', alpha=0.5)
            axs[i, j].text(0.05, 0.95, ax_title,
                    transform=axs[i, j].transAxes,
                    fontsize=10,
                    verticalalignment='top', horizontalalignment='left',
                    bbox=props)

            # Plot data and regression line.
            axs[i, j].plot(df_plot.index, df_plot.visits_div_pop)
            axs[i, j].plot(regress_x, m*regress_x + b, '--', alpha=0.5)
            axs[i, j].xaxis.set_major_locator(ticker.MultipleLocator(10))
            (axs[i, j].yaxis
                .set_major_formatter(ticker.FormatStrFormatter('%.3f')))
            axs[i, j].tick_params(axis='both', which='major', labelsize=9)
            p+=1

    # Shared x and y labels.
    fig.text(0.5, 0.04, 'Year', ha='center', va='center')
    fig.text(0.03, 0.5, 'Per capita visits', ha='center', va='center',
             rotation='vertical')

    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('census_' + title, 'png'))

def park_visits_per_cap_vs_change_rate_quad(df_park, df_pop, designation):
    '''
    This function plots the mean per capita visits over 1967 - 2018
    vs. the change rate in per capita visits from 1967 to 2018 and
    adds quadrant dividing lines.

    Parameters
    ----------
    df_park : Pandas DataFrame
      DataFrame of park data.

    df_pop : Pandas DataFrame
      DataFrame of U.S. population by year.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    df = pd.DataFrame(columns=['park_name', 'per_capita_mean', 'change_rate'])

    # Create a dataframe with row for each park with mean per capita
    # visits since 1967 and change rate in per capita visits since 1967.
    for _, row in df_park.iterrows():
        # Format dataframe and caluculate per capita visits per year.
        df_row = row.to_frame().T
        df_tot = get_visit_df(df_row)
        df_tot['visits_div_pop'] = df_tot.total_visits / df_pop.population

        first_dec_yr = 1967
        first_positive_yr = 1904
        df_tot_zero = df_tot[df_tot.visits_div_pop == 0.0]
        if len(df_tot_zero) > 0:
            first_positive_yr = df_tot_zero.index[-1] + 1
        start_year = max(first_dec_yr, first_positive_yr)
        df_dec = df_tot.loc[start_year:]

        # Calculate average per capita visits from 1967  to 2018.
        per_capita_mean = df_dec.mean().visits_div_pop

        # Fit a regression line to the per capita visits vs. year and
        # find the slope (change rate in per captia visits over time).
        regress_x = df_dec.index
        regress_y = df_dec.visits_div_pop
        stats = linregress(regress_x, regress_y)
        m = stats.slope

        # Add park row to dataframe.
        df = df.append({'park_name' : row.park_name,
                        'park_code' : row.park_code,
                        'per_capita_mean' : per_capita_mean,
                        'change_rate' : m}, ignore_index=True)

    # Divide quadrants vertically by average of visits per capita.
    mean_per_capita_mean = df.per_capita_mean.mean()

    print('\n** Park with Maximum change rate:')
    print(df.loc[df.change_rate.idxmax()])
    print('\n** Park with Minimum change rate:')
    print(df.loc[df.change_rate.idxmin()])

    # Quadrant labels.
    quad1 = "QI: Most popular and increasing"
    quad2 = "QII: Least popular and increasing"
    quad3 = "QIII: Least popular and declining"
    quad4 = "QIV: Most popular and declining"
    quads = [quad1, quad2, quad3, quad4]
    props = dict(facecolor='white', alpha=0.5)

    # Print park contents of each quadrant.
    print ('\n** Quad I **')
    Q1 = df[(df.per_capita_mean >= mean_per_capita_mean)
            & (df.change_rate >= 0.0)]
    print(', '.join(Q1.park_name.values))
    print('Total Q I: {}'.format(len(Q1.index)))

    print('\n** Quad II **')
    Q2 = df[(df.per_capita_mean < mean_per_capita_mean)
            & (df.change_rate >= 0.0)]
    print(', '.join(Q2.park_name.values))
    print('Total Q II: {}'.format(len(Q2.index)))

    print('\n** Quad III **')
    Q3 = df[(df.per_capita_mean < mean_per_capita_mean)
            & (df.change_rate < 0.0)]
    print(', '.join(Q3.park_name.values))
    print('Total Q III: {}'.format(len(Q3.index)))

    print('\n** Quad IV **')
    Q4 = df[(df.per_capita_mean >= mean_per_capita_mean)
            & (df.change_rate < 0.0)]
    print(', '.join(Q4.park_name.values))
    print('Total Q IV: {}'.format(len(Q4.index)))
    print('\n')

    # Plot park visits per capita vs. change rate.
    fig, ax = plt.subplots(figsize=(9,5))
    ax.scatter(df.per_capita_mean, df.change_rate, s=10)

    # Label each point with the park code.
    for i, txt in enumerate(df.park_code):
        ax.annotate(txt, (df.per_capita_mean[i], df.change_rate[i]), size=8)

    # Add label for quadrant I.
    ax.text(0.97, 0.95, quad1,
            transform=ax.transAxes,
            fontsize=8, color='red', alpha=0.7,
            verticalalignment='top', horizontalalignment='right',
            bbox=props)

    # Add label for quadrant II.
    ax.text(0.03, 0.95, quad2,
            transform=ax.transAxes,
            fontsize=8, color='red', alpha=0.7,
            verticalalignment='top', horizontalalignment='left',
            bbox=props)

    # Add label for quadrant III.
    ax.text(0.03, 0.05, quad3,
            transform=ax.transAxes,
            fontsize=8, color='red', alpha=0.7,
            verticalalignment='bottom', horizontalalignment='left',
            bbox=props)

    # Add label for quadrant IV.
    ax.text(0.97, 0.05, quad4,
            transform=ax.transAxes,
            fontsize=8, color='red', alpha=0.7,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=props)

    # Add lines to divide plot into quadrants.
    plt.axhline(y=0.0, linewidth=1.0, alpha=0.3, color='red')
    plt.axvline(x=mean_per_capita_mean, linewidth=1.0, alpha=0.3, color='red')

    # Format axis labels and ticks.
    ax.set_ylim(-0.00020, 0.00020)
    plt.xlabel('Mean visits per capita since 1967', size=10)
    plt.ylabel('Visits per capita change rate', size=10)
    ax.tick_params(labelsize=8)
    plt.title(set_title("Park popularity quadrant", designation))
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('census_park_popularity_quadrant',
                             'png', designation))

def get_visit_df(df):
    '''
    This function sums and formats the park visits data in the
    parameter dataframe for plotting functions in this script.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park data.

    Returns
    -------
    df_tot : Pandas DataFrame
      DataFrame ready for plot functions.
    '''

    start_col = df.columns.tolist().index(1904)
    df_tot = df.iloc[:, start_col:].sum().to_frame()
    df_tot.index = df_tot.index.map(int)
    df_tot.columns = ['total_visits']

    return df_tot

def main():
    df_park, designation = get_parks_df()

    # Get population data and limit population data to 1904-2018
    df_pop = read_census_data()
    df_pop = df_pop.loc[1904:2018]

    # Sum all parks and format dataframe for plotting.
    df_tot = get_visit_df(df_park)

    # Plot #1 - Park visits and U.S. population vs. year
    park_visits_and_us_pop_vs_year(df_tot, df_pop, designation)

    # Plot #2 - Total park visits per capita
    total_park_visits_per_cap_vs_year(df_tot, df_pop, designation, "")

    # Filter park dataframe by selected park and format for plotting.
    park_codes = ['shen']
    df_parks = df_park[df_park.park_code.isin(park_codes)]
    park_name = df_parks.park_name_abbrev.to_list()[0]
    df_tot = get_visit_df(df_parks)

    # Plot #2 - Total park visits per capita (for selected park)
    title = "Park visits per capita vs. year ({})".format(park_name)
    total_park_visits_per_cap_vs_year(df_tot, df_pop, designation, title)

    # Plot #3 - Total park visits per capita - 4 park grid
    # QI examples: park_codes = ['cuva', 'glac', 'yell', 'zion']
    # Q2 examples: park_codes = ['arch', 'care', 'viis', 'jotr']
    # Q3 examples: park_codes = ['cave', 'ever', 'pinn', 'redw']
    park_codes = ['acad', 'grte', 'maca', 'shen']
    df_parks = (
        df_park[df_park.park_code.isin(park_codes)]
        .reset_index(drop=True).copy())
    total_park_visits_per_cap_vs_year_4(df_parks, df_pop)

    # Plot #4 - Park visits per capita vs. rate of change quadrant
    #park_visits_per_cap_vs_change_rate_quad(df_park, df_pop, designation)

    # Plot #5 - Total sites in the NPS system per year.
    # Plot #6 - Total sites per person per year.

if __name__ == '__main__':
    main()
