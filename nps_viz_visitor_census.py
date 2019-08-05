'''
This script creates a set of visualizations using the NPS visitation
data availalable from the NPS website and census data avialable from
census.gov.

The following visualizations are created:
1) Plots including:
   Plot #1 - Park visits and U.S. population vs. year
   Plot #2 - Total park visits per capita
   Plot #3 - Park visits per capita (top 10)
   Plot #4 - Total sites in the NPS system per year.
   Plot #5 - Total sites per person per year.

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
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression
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
    fig.savefig(set_filename('census_park_visits_vs_us_pop', designation, 'png'))

def total_park_visits_per_cap_vs_year(df_tot, df_pop, designation, title=""):
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

    # # Fit a linear regression model and estimate visits
    # regressor = LinearRegression()
    # X = pd.Series(df_dec.index.values).to_frame()
    # y = pd.Series(df_dec.visits_div_pop.values)
    # regressor.fit(X, y)
    #
    # Add a text box to the plot.
    text_string = ("Mean per capita visits since {} = "
                   "{:.4f}\nRegression line slope = {:.4f}".format(first_dec_yr, per_capita_mean, stats.slope))
    props = dict(facecolor='white', alpha=0.5)

    # Use parameter title if specified, otherwise standard title.
    if len(title) == 0:
        title = set_title("Park visits per capita vs. year", designation)

    # Plot park visits per capita by year with regression line.
    fig, ax = plt.subplots()
    #ax.plot(X, regressor.predict(X), ':', color='gray')
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
    fig.savefig(set_filename('census_park_visits_per_capita', designation, 'png'))

def park_visits_per_cap_vs_change_rate(df_park, df_pop, designation):
    # For each park in df, fit a regression line to data since 1967, find slope of line, plot average visits per capita vs. change rate (slope)

    df = pd.DataFrame(columns=['park_name', 'per_capita_mean', 'change_rate'])

    for _, row in df_park.iterrows():
        df_row = row.to_frame().T
        df_tot = get_visit_df(df_row)
        df_tot['visits_div_pop'] = df_tot.total_visits / df_pop.population

        first_dec_yr = 1967
        df_dec = df_tot.loc[first_dec_yr:]

        # Calculate average per capita visits from first decrease year to 2018.
        per_capita_mean = df_dec.mean().visits_div_pop
        regress_x = df_dec.index
        regress_y = df_dec.visits_div_pop
        stats = linregress(regress_x, regress_y)
        m = stats.slope

        print(df_row.park_name, per_capita_mean, m)

        df = df.append({'park_name' : df_row.park_name,
                        'per_capita_mean' : per_capita_mean,
                        'change_rate' : m}, ignore_index=True)

        #print('{}: mean={}, slope={}'.format(row.park_name, per_capita_mean, m))
        #ax.plot(per_capita_mean, m, 'bo')

    print(df)

    mean_per_capita_mean = df.per_capita_mean.mean()

    fig, ax = plt.subplots(figsize=(9,5))
    ax.scatter(df.per_capita_mean, df.change_rate, s=10)
    ax.set_ylim(-0.00020, 0.00020)
    plt.axhline(y=0.0, linewidth=1.0, alpha=0.3, color='red')
    plt.axvline(x=mean_per_capita_mean, linewidth=1.0, alpha=0.3, color='red')
    plt.xlabel('Mean visits per capita since 1967')
    plt.ylabel('Visits per capita change rate')
    plt.title
    plt.show()

# def plot_park_visits_per_capita_vs_year(df_park, df_pop, designation,
#                                         title=None):
#
#     start_col = df_park.columns.tolist().index(1904)
#
#     fig, ax = plt.subplots(figsize=(8,5))
#
#     for _, row in df_park.iterrows():
#         plot_row = row.iloc[start_col:].to_frame()
#         plot_row.columns = ['total_visits']
#         plot_row['visits_div_pop'] = plot_row.total_visits / df_pop.population
#         ax.plot(plot_row.visits_div_pop, label=row.park_name_abbrev)
#
#     # Use parameter title if specified, otherwise standard title.
#     if len(title) == 0:
#         title = set_title("Park visits per capita vs. year", designation)
#
#     # Shrink the plot by 30% and put the legend to the right of the
#     # current axis.
#     box = ax.get_position()
#     ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
#     ax.legend(bbox_to_anchor=(1, 0.5), loc='center left',
#               fancybox=True, borderaxespad=2, fontsize=9)
#
#     plt.title(title)
#
#     # X-axis ticks are every 10th year, displayed vertically.
#     ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
#     plt.xticks(rotation=90)
#     plt.ylabel('Park visits per capita')
#     plt.show()
#
#     # Save plot to file.
#     fig.savefig(set_filename('census_' + title, designation, 'png'))

def parks_in_system_vs_year(df, df_pop, designation):
    '''
    This function ...

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park visit data.

    df_pop : Pandas DataFrame
      DataFrame of U.S. population by year.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    # Extract year for each park from entry_date
    print (df.entry_date)
    df['entry_year'] = pd.DatetimeIndex(df.entry_date).year
    print (df.entry_year)
    # start_col = df.columns.tolist().index(1904)
    # df_park_years = df.iloc[:, start_col:]
    # df_park_years.fillna(value=0)
    # df_tot_parks = df_park_years.gt(0).sum()
    #
    # # Plot number of parks in NPS system vs. year.
    # fig, ax = plt.subplots()
    # ax.plot(df_tot_parks.index, df_tot_parks.values)
    # plt.title(set_title("Total NPS sites per year", designation))
    # plt.show()

    # # Save plot to file.
    # fig.savefig(set_filename('census_total_nps_sites_per_year', designation, 'png'))

def get_visit_df(df):
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

    # Parks with visitors recorded in 2018.
    # df_2018 = df_park[~df_park[2018].isnull()]
    # df_2018 = df_2018[df_2018[2018] > 0.0]
    # df_2018 = df_2018.sort_values(by=[2018], ascending=False)

    # Sum park visits for each year over all parks in the dataframe.
    # start_col = df_park.columns.tolist().index(1904)
    # df_tot = df_park.iloc[:, start_col:].sum().to_frame()
    # df_tot.index = df_tot.index.map(int)
    # df_tot.columns = ['total_visits']

    # Sum all parks and format dataframe for plotting.
    df_tot = get_visit_df(df_park)

    # Plot #1 - Park visits and U.S. population vs. year
    park_visits_and_us_pop_vs_year(df_tot, df_pop, designation)

    # Plot #2 - Total park visits per capita
    total_park_visits_per_cap_vs_year(df_tot, df_pop, designation, "")

    # Filter park dataframe by selected park and format for plotting.
    park_code = 'jotr'
    df_one_park = df_park[df_park.park_code == park_code]
    print('** df_one_park **')
    print(type(df_one_park))
    print(df_one_park)
    park_name = df_one_park.park_name_abbrev.to_list()[0]
    df_tot = get_visit_df(df_park[df_park.park_code == park_code])

    # Plot #2 - Total park visits per capita (for selected park)
    title = "Park visits per capita vs. year ({})".format(park_name)
    total_park_visits_per_cap_vs_year(df_tot, df_pop, designation, title)

    # Plot #3 - Park visits per capita vs. rate of change
    park_visits_per_cap_vs_change_rate(df_park, df_pop, designation)

    #df_tot = get_visit_df (df_park[df_park.park_code == park_code])
    # df_one_park = df_park[df_park.park_code == park_code]
    # park_name = df_one_park.park_name_abbrev.to_list()[0]
    # df_tot = df_one_park.iloc[:, start_col:].sum().to_frame()
    # df_tot.index = df_tot.index.map(int)
    # df_tot.columns = ['total_visits']
    # title = "Park visits per capita vs. year ({})".format(park_name)

    # Plot #2 - Total park visits per capita for a specific park
    #total_park_visits_per_cap_vs_year(df_tot, df_pop, designation, title)

    # Plot #3 - Park visits per capita vs. rate of change
    #park_visits_per_cap_vs_change_rate(df_park, df_pop, designation)

    # Plot #3 - Park visits per capita vs. year for a set of parks.
    # plot_park_visits_per_capita_vs_year(df_2018.iloc[0:10,:].copy(), df_pop,
    #     designation,title = "Park visits per capita vs. year, highest 10")
    #
    # plot_park_visits_per_capita_vs_year(df_2018.iloc[-10:,:].copy(), df_pop,
    #     designation,title = "Park visits per capita vs. year, lowest 10")

    # Plot #4 - Total sites in the NPS system per year.
    # Plot #5 - Total sites per person per year.
    # if designation == "All Parks":
    #     plot_parks_in_system_vs_year(df_park, df_pop, designation)
    # else:
    #     print("** Warning **")
    #     print("Parks in system per year plots only generated if designation "
    #           "not specified.\n")

if __name__ == '__main__':
    main()
