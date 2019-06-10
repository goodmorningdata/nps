'''
This script reads an Excel formatted report of NPS visitor data
downloaded from nps.gov into a dataframe, reformats it so that the
years appear as columns of visits for each park, and saves it to an
Excel file named "annual_visitors_by_park_1904_2018.xlsx".
Columns include: 'Park Name', and 1979 through 2018.

Required Libraries
------------------
pandas

Dependencies
------------
1) Download the most recent version of the "Annual Summary Report
   (1904 - Last Calendar Year)" report from the nps webiste
   at: https://irma.nps.gov/Stats/Reports/National.
   - Select all years, all field names, and all parks. Choose "False"
     for "Summary Only?" Run and download.
   - Move the file to the '_reference_data' directory of this project.
   - Open the file in Excel and save as a .xlsx file with name,
     "Annual_Summary_Report_1904_Last_Calendar_Year.xlsx"
'''

import pandas as pd

def main():
    infile = '_reference_data/Annual_Summary_Report_1904_Last_Calendar_Year.xlsx'
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

    df.to_excel('_reference_data/annual_visitors_by_park_1904_2018.xlsx')

if __name__ == '__main__':
    main()
