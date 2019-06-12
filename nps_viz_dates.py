'''
This script creates a set of plots to further examine the established
date of national park units. Currently, established date is only
available for park units with the designation, "National Park".

The following visualizations are created:
1)

Required Libraries
------------------

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
'''
import pandas as pd
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def plot_parks_per_decade(df, designation):
    '''
    Plot parks established per decade as a bar chart.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park data.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    df['decade'] = df.entry_date.dt.year//10*10
    decade_count = df.decade.value_counts()

    title = "Number of parks established each decade ({})".format(designation)
    filename = ('parks_per_decade_' + designation.lower()
                .replace(' ','_') + '.png')

    fig, ax = plt.subplots()
    sns.barplot(decade_count.index, decade_count.values, alpha=0.8, ax=ax)
    ax.set_title(title)
    plt.ylabel('Number of parks established', fontsize=12)
    plt.xticks(fontsize=9, rotation=90)
    plt.tight_layout()
    plt.show()

    # Save plot to file.
    fig.savefig('_output/' + filename)

def plot_parks_per_year(df, designation):
    '''
    Plot parks established per year as a bar plot.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park data.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    df['year'] = df.entry_date.dt.year
    parks_per_year = df.year.value_counts().sort_index()
    year_count = (pd.Series(0, index=range(1870, 2019))
                  .to_frame()
                  .join(parks_per_year)
                  .fillna(0))

    title = "Number of Parks established each year ({})".format(designation)
    filename = ('park_per_year_' + designation.lower()
                .replace(' ','_') + '.png')

    fig, ax = plt.subplots()
    sns.barplot(year_count.index, year_count.year, alpha=0.8, ax=ax)
    plt.title(title)
    plt.ylabel('Number of parks', fontsize=12)
    # X-axis ticks are every 10th year, displayed vertically.
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useOffset=-1870))
    plt.xticks(rotation=90)
    plt.show()

    # Save plot to file.
    fig.savefig('_output/' + filename)

def plot_parks_per_president(df, designation):
    '''
    Plot parks established per presdient as a bar plot.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park data.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    if designation in ["National Monuments", "National Parks", "All Parks"]:

        fig, ax = plt.subplots()

        if designation == "National Monuments":
            print("National Monuments per president")
            pres_count = (df.groupby(['president_nm', 'president_nm_end_date'])
                          .count().reset_index()
                          .sort_values(by=['president_nm_end_date']))
            plt.barh(pres_count.president_nm, pres_count.park_name)
        if designation == "National Parks":
            print("National Parks per president")
            pres_count = (df.groupby(['president_np', 'president_np_end_date'])
                          .count().reset_index()
                          .sort_values(by=['president_np_end_date']))
            plt.barh(pres_count.president_np, pres_count.park_name)
        if designation == "All Parks":
            print("All Parks per president")
            pres_count = (df.groupby(['president', 'president_end_date'])
                          .count().reset_index()
                          .sort_values(by=['president_end_date']))
            plt.barh(pres_count.president, pres_count.park_name)

        title = "Parks established by president ({})".format(designation)
        filename = ('parks_per_president_' + designation.lower()
                    .replace(' ','_') + '.png')

        plt.title(title)
        plt.xticks(fontsize=9)
        plt.tight_layout()
        plt.show()

        # Save plot to file.
        fig.savefig('_output/' + filename)

    else:
        print("\n** Error **")
        print("Parks per president plot only available for National Parks, "
              "National Monuments, and All Parks designations. Plot will "
              "not be created for the {} designation\n".format(designation))

def main():
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    # Use Seaborn formatting for plots and set color palette.
    sns.set()
    sns.set_palette('Paired')

    # The user can specify the set of parks to map using the command
    # line parameter, 'designation'. If no parameter specified, all
    # park sites are added to the map.
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--designation', type=str,
           help = "Set of parks for which to display locations. If not \
                  specified, all park sites will be mapped.\
                  Possible values are: 'International Historic Sites',\
                  'National Battlefields', 'National Battlefield Parks',\
                  'National Battlefield Sites', 'National Military Parks',\
                  'National Historical Parks', 'National Historic Sites',\
                  'National Lakeshores', 'National Memorials',\
                  'National Monuments', 'National Parks', 'National Parkways',\
                  'National Preserves', 'National Reserves',\
                  'National Recreation Areas', 'National Rivers',\
                  'National Wild and Scenic Rivers and Riverways',\
                  'National Scenic Trails', 'National Seashores',\
                  'Other Designations'")
    args = parser.parse_args()

    # Filter the dataframe based on designation and remind user which
    # park designations will be in the visualizations.
    if args.designation:
        df_park = df[df.designation == args.designation].copy()
        print("\nCreating park dates plots for the park designation, {}."
              .format(args.designation))
        designation = args.designation
    else:
        df_park = df.copy()
        print("\nCreating park date plots for all NPS sites.")
        designation = "All Parks"
    print("")

    #df_park = df.loc[df.designation == "National Parks"].copy()

    # Plot #1 - Number of parks established each decade.
    plot_parks_per_decade(df_park, designation)

    # Plot #2 - Cummulative park total vs. year.
    plot_parks_per_year(df_park, designation)

    # Plot #3 - Number of parks established by president.
#    plot_parks_per_president(df_park[['park_name','president', 'president_end_date']], designation)
    plot_parks_per_president(df_park, designation)

if __name__ == "__main__":
    main()
