'''Read visitor data from 1979 to the present (2018).

This script reads two excel files of NPS visitor data and creates a
dataframe of recreational visits for each National Park site for the
past 40 years, 1979 through 2018. Data prior to 1979 is not available
on the NPS website. The dataframe is output to an Excel file for use
by the nps_create_master_df.py script.

The script creates an Excel file as output named
"annual_visitors_by_park_1979_2018.xlsx" with column headers.
Columns include: 'Park Name', and 1979 through 2018.

Dependencies:

    * Download the most recent visitation reports from the nps webiste
      at: https://irma.nps.gov/Stats/Reports/National. Choose the
      'Annual Visitation By Park (1979 - Last Calendar Year)'. The
      report must be run twice because only 20 years can be reported
      at a time:
      1) Use 'Report Year' = 2018, 'Num Years' = 20, 'Select Field
         Name(s)' = 'Recreation Visits'. Save the report as
         'annual_visitors_by_park_1999_2018.xlsx'.
      2) Use 'Report Year' = 1998, 'Num Years' = 20, 'Select Field
         Name(s)' = 'Recreation Visits'. Save the report as
         'annual_visitors_by_park_1979_1998.xlsx'.
      Both files should be put in the '_visitor_data' directory
      of this project.
'''

import pandas as pd

def main():
    df1 = pd.read_excel(
          '_visitor_data/annual_visitors_by_park_1979_1998.xlsx',
          header=8, index=False, usecols = 'C:L,O:Y')
    df2 = pd.read_excel(
          '_visitor_data/annual_visitors_by_park_1999_2018.xlsx',
          header=8, index=False, usecols='C:L,O:Y')
    df = (df1.merge(df2, how='outer', on='Park Name')
             .sort_values(by=['Park Name']))
    df.fillna(value=0.0, inplace=True)
    df.to_excel('_visitor_data/annual_visitors_by_park_1979_2018.xlsx', index=False)

if __name__ == '__main__':
    main()
