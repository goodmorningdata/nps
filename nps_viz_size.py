'''
This script creates a map of the United States with NPS sites marked
with a circle corresponding to the site's size. The command line
argument, "designation", set by the flag, "-d", allows the user to
specify the set of park sites to add to the map. If no parameter is
specified, all NPS site locations are added to the map.

The following visualizations are created:
1) A Folium map with park location mapped as an icon. Each icon has as
   a clickable pop that tells the park name and links to the nps.gov
   page for the park.
   - Output file = nps_parks_map_location_{designation}.html

2) A table of park size in order of size in descending order. first.
   - Output files = nps_parks_sorted_by_visits_{designation}.xlsx,
                    nps_parks_sorted_by_visits_{designation}.html.

3) Plots including:
   Plot #1 - Park size histogram.
   NOT COMPLETE - Plot #2 - Average designation park size bar plot.
   Plot #3 - Total park area per state pie chart.

Required Libraries
------------------
math, pandas, folium, matplotlib

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
'''

from nps_shared import *
import math
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt

def create_size_map(df, designation):
    '''
    This function adds a circle marker for each park in the parameter
    dataframe to the map. The circle size corresponds to the area of
    the park. The radius of the circle was calculated by taking the
    area of the park in square meters, dividing it by pi and then taking
    the square root.

    These markers provide the park name and park size in square miles
    as a tooltip. A tooltip instead of a popup is used for this map
    because the popup was less sensitive for the circle markers.

    Parameters
    ----------
    map : Folium map object
      Folium map to add circle markers to.

    df : Pandas DataFrame
      DataFrame of all park visitors to add to the map.

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

    # Add park size circles to map.
    for _, row in (df[~df.lat.isnull()]
        .sort_values(by='designation', ascending=False).iterrows()):

        # Create tooltip with park size.
        tooltip = (row.park_name.replace("'", r"\'")
                  + ', {:,.0f} acres'.format(row.gross_area_acres)
                  + ' ({:,.0f}'.format(row.gross_area_square_miles)
                  + ' square miles)')

        # Add marker to map.
        folium.Circle(
            radius=math.sqrt(row.gross_area_square_meters/math.pi),
            location=[row.lat, row.long],
            tooltip=tooltip,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(map)

    # Save map to file.
    map.save(set_filename('size_map', 'html', designation))

def plot_park_size_histogram(df, designation):
    '''
    Generate a park size histogram.

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

    # List of park acreage in millions of acrea.
    x_list = (df.gross_area_acres.values)/1e6

    # Mean and median text box.
    mean = df.gross_area_acres.mean()/1e6
    median = np.median(df.gross_area_acres)/1e6
    text_string = '$\mu=%.2f$\n$\mathrm{median}=%.2f$'%(mean, median)

    # matplotlib.patch.Patch properties.
    props = dict(facecolor='white', alpha=0.5)

    # Create park size histogram.
    fig, ax = plt.subplots()
    ax.hist(x_list, bins=list(range(math.ceil(max(x_list)) + 1)), alpha=0.8)
    ax.text(0.96, 0.95, text_string,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=props)
    plt.xlabel("Millions of acres")
    plt.ylabel("Number of parks")
    plt.title(set_title("Park size histogram 2018", designation))
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('size_histogram', 'png', designation))

def plot_avg_size_vs_designation(df, designation):
    '''
    Calculate the average park size within each designation and plot
    as a bar chart.

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

    if designation == "All Parks":
        df = (df[['designation', 'gross_area_acres']]
             .groupby(by='designation').mean())
        df = df.sort_values(by='designation')

        # Create horizontal bar plot of number of parks in each state.
        fig = plt.figure(figsize=(8,6))
        plt.barh(df.index, df.gross_area_acres/1e6, alpha=0.8)
        plt.title(set_title("Average park size by designation",
                            designation))
        plt.xlabel("Millions of acres")
        plt.yticks(fontsize=8)
        plt.tight_layout()
        plt.show()

        # Save plot to file.
        fig.savefig(set_filename('size_avg_size_vs_designation',
                                 'png', designation))

    else:
        print("** Warning ** ")
        print("Average park size vs. designation plot only makes sense for "
              "all parks. You entered designation = {}. If you would like to "
              "see the average park size vs. designation plot, please run the "
              "script again with no designation command line parameter."
              "Ex: 'python3 nps_viz_size.py'".format(designation))
        print("****\n")

def chart_total_park_area_per_state(df, designation):
    '''
    This function plots park area in each state as a percent of total
    U.S. park area as a pie chart. The first 6 states are given their
    own pie wedge and the remaining states grouped as "other" for
    readability.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park size data.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    # Total area of all parks in the dataframe.
    total_area = df.gross_area_acres.sum()

    # Group and sum area by state.
    df_state_areas = (df[['main_state', 'gross_area_acres']]
                      .groupby(['main_state'])
                      .sum()
                      .sort_values('gross_area_acres', ascending=False))

    # Split into top six and "Other".
    df_plot = df_state_areas[:6].copy()
    df_plot.loc['Other'] = [df_state_areas['gross_area_acres'][6:].sum()]

    # Pie chart.
    fig, ax = plt.subplots()
    ax.pie(df_plot.gross_area_acres, labels=df_plot.index,
           startangle=90, autopct='%1.1f%%', shadow=False)
    ax.axis('equal')
    plt.suptitle(set_title("Percent of total U.S. park area by state",
                           designation), size=16)
    plt.title('Total U.S. park area ({}) is {:,.0f} acres'
              .format(designation.lower(), total_area))
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('size_total_park_area_by_state',
                             'png', designation))

def plot_park_area_pct_of_state(df, designation):
    '''
    This function plots park area percent of total state area for each
    state as a horizontal bar plot. If a state does not have any parks
    in the designation parameter category, it will not be included in
    the plot.

    Parameters
    ----------
    df : Pandas DataFrame
      DataFrame of park size data.

    designation : str
      Designation of parks in the dataframe.

    Returns
    -------
    None
    '''

    # Get state areas from file.
    df_state = pd.read_csv('_reference_data/census_state_area.csv',
                           index_col='state_code')

    # Group and sum area by state.
    df_park_area = (df[['main_state', 'gross_area_acres']]
                    .groupby(['main_state'])
                    .sum()
                    .sort_values('gross_area_acres', ascending=False))

    # Join park area and state area dataframes and calculate percent.
    df_park_area = df_park_area.join(df_state, how='left')
    df_park_area['pct_area'] = (df_park_area.gross_area_acres /
                                df_park_area.area_acres * 100)
    df_park_area.sort_values(by=['pct_area'], ascending=False, inplace=True)

    # Plot park area percent of state area by state.
    fig = plt.figure(figsize=(8,6))
    plt.barh(df_park_area.index, df_park_area.pct_area, alpha=0.8)
    plt.title(set_title("Park area as a percent of total state area",
                        designation), size=16)
    plt.xlabel("Percent of total state area")
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.show()

    # Save plot to file.
    fig.savefig(set_filename('size_park_area_pct_of_state',
                             'png', designation))

def output_size_data_to_tables(df, designation):
    '''
    This function outputs the park size data as a table to both an
    Excel spreadsheet and an html file. The data is sorted by size,
    largest first.

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

    df = df.round(0)
    df_export = (df[['park_name', 'gross_area_acres',
                     'gross_area_square_miles']]
                .sort_values(by=['gross_area_acres'], ascending=False)
                .reset_index(drop=True))
    df_export.index += 1

    df_export['gross_area_square_miles'].replace(
        to_replace=0, value="<1", regex=True, inplace=True)

    export_cols = {'park_name': 'Park Name',
                   'gross_area_acres': 'Size (acres)',
                   'gross_area_square_miles': 'Size (square miles)'}
    df_export = df_export.rename(columns=export_cols)

    filename = set_filename('size_parks_sorted_by_size',
                            designation=designation)

    df_export.to_excel(filename + 'xlsx', index=True)
    df_export.to_html(filename + 'html',
                      justify='left',
                      classes='table-park-list',
                      float_format=lambda x: '{:,.0f}'.format(x))

def main():
    df_park, designation = get_parks_df(warning=['location', 'size'])

    # Remove parks missing size data from the dataframe.
    df_park = df_park[~df_park.gross_area_acres.isnull()]

    # Print statistical info for dataframe.
    print(df_park[['gross_area_acres', 'gross_area_square_miles',
                   'gross_area_square_meters']].describe(), '\n')

    # Map #1 - Plot park locations with size circle and save map to html file.
    create_size_map(df_park, designation)

    # Plot #1 - Histogram - park size
    plot_park_size_histogram(df_park, designation)

    # NOT COMPLETE - Plot #2 - Average designation park size bar plot.
    #plot_avg_size_vs_designation(df_park, designation)

    # Plot #3 - Total park area per state pie chart.
    chart_total_park_area_per_state(df_park, designation)

    # Plot #4 - Park area as a percent of state area.
    plot_park_area_pct_of_state(df_park, designation)

    # Save park size data as an Excel spreadsheet and an html table.
    output_size_data_to_tables(df_park, designation)

if __name__ == '__main__':
    main()
