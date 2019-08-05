'''
This script creates a set of plots to further examine the dates that
NPS units were established. Each park is assigned an entry date which is
the date that they were established as federal parkland. Some parks
began as national monuments and these parks have a national monument
date. National parks are assigned a date when they were established as a
national park.

The following visualizations are created:
1) Plots including:
   Plot #1 - Number of parks established each decade.
   Plot #2 - Number of parks established each year.
   Plot #3 - Number of parks established by president.

Required Libraries
------------------
pandas, seaborn, matplotlib.

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
'''

from nps_shared import *
import pandas as pd
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

    # Create dataframe of count of parks established per decade.
    df['decade'] = df.entry_date.dt.year//10*10
    decade_count = df.decade.value_counts()

    # Create bar plot of parks established per decade.
    fig, ax = plt.subplots()
    plt.bar(decade_count.index, decade_count.values, alpha=0.8, width=8)
    plt.title(set_title("Number of parks established each decade", designation))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(fontsize=9, rotation=90)
    plt.ylabel('Number of parks established', fontsize=12)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('date_parks_per_decade', 'png', designation))

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

    # Create dataframe of count of parks established per year.
    df['year'] = df.entry_date.dt.year
    parks_per_year = df.year.value_counts().sort_index()
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    year_count = (pd.Series(0, index=range(min_year, max_year))
                  .to_frame()
                  .join(parks_per_year)
                  .fillna(0))

    # Create bar plot of parks established per year.
    fig, ax = plt.subplots()
    plt.bar(year_count.index, year_count.year, alpha=0.8, width=1)
    plt.title(set_title("Number of parks established each year", designation))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.xticks(rotation=90, fontsize=9)
    plt.ylabel('Number of parks', fontsize=12)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('date_parks_per_year', 'png', designation)

def plot_parks_per_president(df, designation):
    '''
    Plot parks established per presdient as a bar plot. Park
    designations that this is possible for are: National Monuments,
    National Parks, and All Parks.

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

        # Create bar plot of parks established per president.
        fig = plt.figure()

        # If designation is National Monument, use president in office
        # when the monument was established.
        if designation == "National Monuments":
            pres_count = (df.groupby(['president_nm', 'president_nm_end_date'])
                          .count().reset_index()
                          .sort_values(by=['president_nm_end_date']))
            plt.barh(pres_count.president_nm, pres_count.park_name)

        # If designation is National Park, use president in office when
        # the national park was established.
        if designation == "National Parks":
            pres_count = (df.groupby(['president_np', 'president_np_end_date'])
                          .count().reset_index()
                          .sort_values(by=['president_np_end_date']))
            plt.barh(pres_count.president_np, pres_count.park_name)

        # Otherwise, use president in office when the park was
        # originally established.
        if designation == "All Parks":
            pres_count = (df.groupby(['president', 'president_end_date'])
                          .count().reset_index()
                          .sort_values(by=['president_end_date']))
            plt.barh(pres_count.president, pres_count.park_name)

        plt.title(set_title("Parks established by president", designation))
        plt.xticks(fontsize=9)
        plt.yticks(fontsize=9)
        plt.tight_layout()
        plt.show()

        # Save plot to file.
        fig.savefig(set_filename('date_parks_per_pres', 'png', designation))

    else:
        print("\n** Warning **")
        print("Parks per president plot only available for National Parks, "
              "National Monuments, and All Parks designations. Plot will "
              "not be created for the {} designation.".format(designation))
        print("****\n")

def plot_parks_per_designation(df, designation):
    '''
    Plot parks per designation as a bar plot. This function does not
    really belong in this script, will move when more appropriate
    visualization script is created.

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

    if designation in ["All Parks"]:

        # Create bar plot of parks per designation.
        des_count = (df.groupby(['designation'])
                       .count().reset_index()
                       .sort_values(by=['designation'], ascending=False))

        des_count.loc[:,'designation'] = (
            des_count.loc[:,'designation'].replace(
            {'National Wild and Scenic Rivers and Riverways':
             'Natl Wild & Scenic Rvrs and Rvrways'}, regex=True))

        fig = plt.figure()
        plt.barh(des_count.designation, des_count.park_name)
        plt.title(set_title("Parks per designation", designation))
        plt.xticks(fontsize=9)
        plt.yticks(fontsize=9)
        plt.tight_layout()
        plt.show()

        # Save plot to file.
        fig.savefig(set_filename('date_parks_per_designation', 'png',
                                 designation))

    else:
        print("\n** Warning **")
        print("Parks per designation plot only available if no designation "
              "command line argument set. Plot will not be created for the {} "
              "designation.".format(designation))
        print("****\n")

def main():
    df_park, designation = get_parks_df()

    # Plot #1 - Number of parks established each decade.
    plot_parks_per_decade(df_park, designation)

    # Plot #2 - Number of parks established each year.
    plot_parks_per_year(df_park, designation)

    # Plot #3 - Number of parks established by president.
    plot_parks_per_president(df_park, designation)

    # Plot #4 - Number of parks per designation.
    plot_parks_per_designation(df_park, designation)
#
if __name__ == "__main__":
    main()
