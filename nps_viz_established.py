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
import seaborn as sns
import matplotlib.pyplot as plt

def plot_num_parks_per_decade(df):
    df['decade'] = df.date_established.dt.year//10*10
    decade_count = df.decade.value_counts()
    fig, ax = plt.subplots()
    sns.barplot(decade_count.index, decade_count.values, alpha=0.8)
    plt.title('Number of National Parks established each decade')
    plt.ylabel('Number of parks established', fontsize=12)
    plt.show()

    #years = [str(i) for i in range(1904, 2019)]
    #Want count of parks founded in each year (bar) and total number of parks in the system in each year (line)
    #for year in years:
    #     print ('****', year)
         #print(df[df[year] > 0 & pd.notnull(df[year])])
    #     print(df[df[year] > 0 & pd.notnull(df[year])].count())
    #nps_parks_num_parks_per_year.html

def main():
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)
    park_df = df.loc[df.designation == "National Parks"].copy()

    # Use Seaborn formatting for plots and set color palette.
    sns.set()
    sns.set_palette('Dark2')

    # Plot #1 - Number of National Parks established each year.
    plot_num_parks_per_decade(park_df)

    # Plot the total number of parks per year and number
    # established that year.
    #plot_num_parks_num_established(map_df)

if __name__ == "__main__":
    main()
