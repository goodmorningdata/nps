'''
This script

The following visualizations are created:
1)

Required Libraries
------------------

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
'''

def plot_num_parks_per_year(df):
    years = [str(i) for i in range(1904, 2019)]
    #Want count of parks founded in each year (bar) and total number of parks in the system in each year (line)
    for year in years:
         print ('****', year)
         #print(df[df[year] > 0 & pd.notnull(df[year])])
         print(df[df[year] > 0 & pd.notnull(df[year])].count())
    #nps_parks_num_parks_per_year.html

def main():
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    # Plot #1 - Number of National Parks established each year.
    #plot_num_parks_per_year(map_df)

    # Plot the total number of parks per year and number
    # established that year.
    #plot_num_parks_num_established(map_df)

if __name__ == "__main__":
    main()
