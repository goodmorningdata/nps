'''
This script creates a set of visualizations using the NPS visitation
data availalable from the NPS website and census data avialable from
census.gov.

The following visualizations are created:
1) Plots including:
   Plot #1 - Park visits and U.S. population vs. year
   Plot #2 - Park visits per capita

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

def plot_park_visits_and_us_pop_vs_year(df_tot, df_pop, designation):
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
    fig.savefig(set_filename('census_park_visits_vs_us_pop', designation, 'png'))

def plot_park_visits_per_capita_vs_year(df_tot, df_pop, designation):
    '''
    This function plots park visits per capita for 1904-2018.

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

    # Calculate park visits per capita
    visits_div_pop = df_tot.values / df_pop['population']

    # Plot park visits per capita by year.
    fig, ax = plt.subplots()
    ax.plot(df_tot.index, visits_div_pop)
    plt.title(set_title("Park visits per capita", designation))
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('census_park_visits_per_capita', designation, 'png'))

def main():
    df_park, designation = get_parks_df()

    # Get population data and limit population data to 1904-2018
    df_pop = read_census_data()
    df_pop = df_pop.loc[1904:2018]

    # Sum park visits for each year over all parks in the dataframe.
    start_col = df_park.columns.tolist().index(1904)
    df_tot = df_park.iloc[:, start_col:].sum()

    # Plot #1 - Park visits and U.S. population vs. year
    plot_park_visits_and_us_pop_vs_year(df_tot, df_pop, designation)

    # Plot #2 - Park visits per capita
    plot_park_visits_per_capita_vs_year(df_tot, df_pop, designation)

if __name__ == '__main__':
    main()
