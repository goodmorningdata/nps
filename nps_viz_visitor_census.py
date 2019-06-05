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

def plot_park_visits_vs_us_pop(df_visits, df_pop, park_set):
    '''
    This fuction creates two plots. The first plots total park visits
    per year in one subplot, and U.S. population for the same years in
    a second subplot. The second plots park visits per capita. Both
    plot images are saved to .png files.

    Parameters
    ----------
    df_visits : Pandas DataFrame
      DataFrame of park visit data to plot filtered by park set
      parameter.

    df_pop : Pandas DataFrame
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
    visit_totals = pd.DataFrame(df_visits.sum().loc['1904':'2018'],
                                columns=['visitors'])
    visit_totals.index = range(1904,2019)
    visit_totals['visits_div_pop'] = (visit_totals['visitors'] /
                                      df_pop['population'].loc[1904:2018])

    # Plot total park visits and U.S. population by year.
    fig, ax = plt.subplots(2, sharex=True)
    ax[0].plot(visit_totals.index, visit_totals.visitors/1e6)
    ax[0].set_title("Total park visits ({})".format(park_set))
    ax[0].set_ylabel("Millions of visits")
    ax[1].plot(visit_totals.index, df_pop['population'].loc[1904:2018]/1e6)
    ax[1].set_title("U.S. population")
    ax[1].set_ylabel("Millions of people")
    plt.show()

    # Save plot to file.
    fig.savefig('_output/park_visits_vs_us_pop.png')

    # Plot park visits per capita by year.
    fig, ax = plt.subplots()
    ax.plot(visit_totals.index, visit_totals.visits_div_pop)
    ax.set_title("Park visits per capita ({})".format(park_set))
    plt.show()

    # Save plot to file.
    fig.savefig('_output/park_visits_per_capita.png')


        # Plot park visits in relation to the U.S. population.
        #df_pop = read_census_data()
        #plot_park_visits_vs_us_pop(df_park, df_pop, park_set)
