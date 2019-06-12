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
pandas, argparse, seaborn, matplotlib.

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

    # Create dataframe of count of parks established each decade.
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

    fig.savefig('_output/' + filename)

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

        fig.savefig('_output/' + filename)

    else:
        print("\n** Error **")
        print("Parks per president plot only available for National Parks, "
              "National Monuments, and All Parks designations. Plot will "
              "not be created for the {} designation\n".format(designation))

def main():
    df_park, designation = nps.get_parks_df(warning=['location'])

    # Plot #1 - Number of parks established each decade.
    plot_parks_per_decade(df_park, designation)

    # Plot #2 - Number of parks established each year.
    plot_parks_per_year(df_park, designation)

    # Plot #3 - Number of parks established by president.
    plot_parks_per_president(df_park, designation)

if __name__ == "__main__":
    main()
