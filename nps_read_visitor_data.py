'''Read visitor data from 1904 to the present (2018).

This script reads an excel file of NPS visitor data into a dataframe,
reformats it so that the years appear as columns of recreation visits
for each park, and saves it to an Excel file named
"annual_visitors_by_park_1904_2018.xlsx" with column headers.
Columns include: 'Park Name', and 1979 through 2018.

Dependencies:

    * Download the most recent version of the "Annual Summary Report
      (1904 - Last Calendar Year)" report from the nps webiste
      at: https://irma.nps.gov/Stats/Reports/National.
      1) Select all years, all field names, and all parks. Choose
         "False" for "Summary Only?" Run and download.
      2) Move the file to the '_visitor_data' directory of this project.
      3) Open the file in Excel and save as a .xlsx file with name,
         "Annual_Summary_Report_1904_Last_Calendar_Year.xlsx"
'''

import pandas as pd

def main():
    infile = '_visitor_data/Annual_Summary_Report_1904_Last_Calendar_Year.xlsx'
    df = pd.read_excel(infile, header=3, index=False, usecols='A:C')

    # Eliminate the summary rows found at the bottom of the file after
    # the annual park totals.
    first_blank_row = df[pd.isnull(df.ParkName)].index.values[0]
    df = df[:first_blank_row]

    # Pivot dataframe so that the years become columns.
    df.RecreationVisitors = df.RecreationVisitors.apply(int)
    df = df.pivot_table('RecreationVisitors', ['ParkName'], 'Year' )
    df.index.rename('park_name', inplace=True)

    # Replace NaN with 0.0.
    df.fillna(value=0.0, inplace=True)

    df.to_excel('_visitor_data/annual_visitors_by_park_1904_2018.xlsx')

if __name__ == '__main__':
    main()
