'''
This script creates a set of visualizations using the NPS visitation
data availalable from the NPS website and census data avialable from
census.gov.

The following visualizations are created:
1) Plots including:
   Plot #1 - Park visits and U.S. population vs. year
   Plot #2 - Total park visits per capita
   Plot #3 - Park visits per capita (top 10)
   TODO - Plot #4 - Total sites in the NPS system per year.
   TODO - Plot #5 - Total sites per person per year.

Required Libraries
------------------
pandas, nps_shared, matplotlib

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
2) Run the script, nps_read_population_data.py to create the file,
   us_est_1900-2018.xlsx.
'''

from nps_shared import *
import pandas as pd
import matplotlib.pyplot as plt
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

    # ** Uncomment following code to find the first decrease in per
    # capita visits since 1965 **
    # df_1965 = df_tot.loc[1965:]
    # first_dec_yr = df_1965.index[df_1965.diff_visits_div_pop < 0].tolist()[0]
    # print("First visits per capita decrease year since 1965 is "
    #       "{}".format(first_dec_yr))

    first_dec_yr = 1967
    df_dec = df_tot.loc[first_dec_yr:]

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

    # Plot park visits per capita by year with regression line.
    fig, ax = plt.subplots()
    ax.text(0.05, 0.95, text_string,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top', horizontalalignment='left',
            bbox=props)
    ax.plot(df_tot.index, df_tot.visits_div_pop)
    ax.plot(regress_x, m*regress_x + b, '--', alpha=0.5)
    plt.title(title)
    plt.show()

    # Save plot to file.
    # fig.savefig(set_filename('census_park_visits_per_capita',
    #                          designation, 'png'))
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
        df_dec = df_tot.loc[first_dec_yr:]

        # Calculate average per capita visits from 1967  to 2018.
        per_capita_mean = df_dec.mean().visits_div_pop

        # Fit a regression line to the per capita visits vs. year and
        # find the slope (change rate in per captia visits over time).
        regress_x = df_dec.index
        regress_y = df_dec.visits_div_pop
        stats = linregress(regress_x, regress_y)
        m = stats.slope

        # Add park row to dataframe.
        df = df.append({'park_name' : df_row.park_name,
                        'park_code' : df_row.park_code,
                        'per_capita_mean' : per_capita_mean,
                        'change_rate' : m}, ignore_index=True)

    # Divide quadrants vertically by average of visits per capita.
    mean_per_capita_mean = df.per_capita_mean.mean()

    # Quadrant labels.
    quad2 = "Q2: Most popular and increasing"
    quad3 = "Q3: Least popular and declining"
    props = dict(facecolor='white', alpha=0.5)

    # Plot park visits per capita vs. change rate.
    fig, ax = plt.subplots(figsize=(9,5))
    ax.scatter(df.per_capita_mean, df.change_rate, s=10)

    # Label each point with the park code.
    for i, txt in enumerate(df.park_code):
        ax.annotate(txt.values[0], (df.per_capita_mean[i], df.change_rate[i]), size=8)

    # Add label for quadrant 2.
    ax.text(0.97, 0.95, quad2,
            transform=ax.transAxes,
            fontsize=8, color='red', alpha=0.7,
            verticalalignment='top', horizontalalignment='right',
            bbox=props)

    # Add label for quadrant 3.
    ax.text(0.02, 0.07, quad3,
            transform=ax.transAxes,
            fontsize=8, color='red', alpha=0.7,
            verticalalignment='top', horizontalalignment='left',
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
    park_code = 'jotr'
    df_one_park = df_park[df_park.park_code == park_code]
    park_name = df_one_park.park_name_abbrev.to_list()[0]
    df_tot = get_visit_df(df_one_park)

    # Plot #2 - Total park visits per capita (for selected park)
    title = "Park visits per capita vs. year ({})".format(park_name)
    total_park_visits_per_cap_vs_year(df_tot, df_pop, designation, title)

    # Plot #3 - Park visits per capita vs. rate of change quadrant
    park_visits_per_cap_vs_change_rate_quad(df_park, df_pop, designation)

    # Plot #4 - Total sites in the NPS system per year.
    # Plot #5 - Total sites per person per year.

if __name__ == '__main__':
    main()
