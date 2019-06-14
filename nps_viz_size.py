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
import folium
import matplotlib.pyplot as plt

def create_map():
    '''
    This function creates a Folium map object, centered on the lat/long
    center of the lower 48 states.

    Parameters
    ----------
    None

    Returns
    -------
    map : Folium map object
      Empty Folium map.
    '''

    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48,
                     zoom_start = 3,
                     control_scale = True,
                     tiles = 'Stamen Terrain')

    return map

def add_park_size_circles_to_map(map, df):
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
    map : Folium map object
      Folium map with circle area markers added.
    '''

    for _, row in (df[~df.lat.isnull()]
        .sort_values(by='designation', ascending=False).iterrows()):

        tooltip = (row.park_name.replace("'", r"\'")
                   + ', {:,.0f}'.format(row.gross_area_square_miles)
                   + ' square miles')
        folium.Circle(
            radius=math.sqrt(row.gross_area_square_meters/math.pi),
            location=[row.lat, row.long],
            tooltip=tooltip,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(map)

    return map

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

    x_list = (df.gross_area_acres.values/1e6).tolist()

    title = "Park size in acres in 2018 ({})".format(designation)
    filename = ('park_size_histogram_' + designation.lower()
               .replace(' ','_') + '.png')

    fig, ax = plt.subplots()
    ax = sns.distplot(x_list, kde=False)
    ax.set_xlabel("Millions of acres")
    ax.set_ylabel("Number of parks")
    ax.set_title(title)
    plt.show()

    # Save plot to file.
    fig.savefig('_output/' + filename)

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

        # Horizontal bar plot of number of parks in each state.
        title = "Average park size by designation ({})".format(designation)
        filename = ('avg_size_vs_designation_' + designation.lower()
                   .replace(' ','_') + '.png')

        fig, ax = plt.subplots(figsize=(8,6))
        plt.barh(df.index, df.gross_area_acres/1e6, alpha=0.8)
        ax.set_title(title)
        plt.yticks(fontsize=8)
        plt.xlabel("Millions of acres")
        plt.tight_layout()
        plt.show()

        # Save plot to file.
        fig.savefig('_output/' + filename)

    else:
        print("** Warning ** ")
        print("Average park size vs. designation plot only makes sense for "
              "all parks. You entered designation = {}. If you would like to "
              "see the average park size vs. designation plot, please run the "
              "script again with no designation command line parameter."
              "Ex: 'python3 nps_viz_size.py'".format(designation))
        print("****\n")

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

    df_export = (df[['park_name', 'gross_area_acres',
                     'gross_area_square_miles']]
                 .sort_values(by=['gross_area_acres'], ascending=False)
                 .reset_index(drop=True))
    df_export.index += 1
    export_cols = {'park_name': 'Park Name',
                   'gross_area_acres': 'Size (acres)',
                   'gross_area_square_miles': 'Size (square miles)'}
    df_export = df_export.rename(columns=export_cols)

    filename = ('nps_parks_sorted_by_size_'
                + designation.lower().replace(' ','_'))

    df_export.to_excel('_output/' + filename + '.xlsx', index=False)
    df_export.to_html('_output/' + filename + '.html',
                      justify='left',
                      classes='table-park-list',
                      float_format=lambda x: '{:,.2f}'.format(x))

def main():
    df_park, designation = get_parks_df(warning=['location', 'size'])

    # Remove parks missing size data from the dataframe.
    df_park = df_park[~df_park.gross_area_acres.isnull()]

    # Map #1 - Plot park locations with size circle and save map to html file.
    park_map = create_map()
    park_map = add_park_size_circles_to_map(park_map, df_park)
    filename = ('_output/nps_parks_map_size_'
                + designation.lower().replace(' ','_')
                + '.html')
    park_map.save(filename)

    # Plot #1 - Histogram - park size
    plot_park_size_histogram(df_park, designation)

    # Plot #2 - Average designation park size bar plot.
    plot_avg_size_vs_designation(df_park, designation)

    # Save park size data as an Excel spreadsheet and an html table.
    output_size_data_to_tables(df_park, designation)

if __name__ == '__main__':
    main()
