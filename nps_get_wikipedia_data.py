''' Scrape Wikipedia page for National Park establishment dates.

This script scrapes the Wikipedia page, "List of national parks of the
United States", for the establishment date of each National Park. The
Python library, BeatutifulSoup, is used to pull the data out of the
html file. The dataframe is saved as an Excel file,
"wikipedia_date_established.xlsx".

Required libraries: BeautifulSoup, pandas, datetime.

Dependencies:
    * Save the webpage:
      https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States
      as "wikipedia_national_parks.html" in the "_reference_data"
      folder of the project.
'''

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def main():
    filename = '_reference_data/wikipedia_national_parks.html'
    soup = BeautifulSoup(open(filename), 'html.parser')

    df = pd.DataFrame(columns=['park_name', 'date_established'])

    # Find the table of National Parks.
    table_rows = soup.find_all('table')[1].find_all('tr')

    # For each row in the table, extract the name of the park, and
    # the date established and add to the dataframe.
    for row in table_rows[1:]:
        name = str(row.a.string)
        date = str(row.findAll("span", {"data-sort-value" : True})[0].string)
        date = datetime.strptime(date, '%B %d, %Y')
        df = df.append({'park_name': name, 'date_established': date},
                       ignore_index=True)

    df.to_excel('_reference_data/wikipedia_date_established.xlsx',
                index=False)

if __name__ == '__main__':
    main()
