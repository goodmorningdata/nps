'''
This script uses the Python library, BeautifulSoup to scrape data
from the following Wikipedia pages, and to save the resulting
dataframes to csv files.
1) Establishment date of each National Park is retrieved from the
   page, "List of national parks of the United States".
2) President name, and start date and end dates of term, are retrieved
   from the page, "List of Presidents of the United States".

Required Libraries
------------------
BeautifulSoup, pandas, datetime

Dependencies
------------
1) Save the webpage:
   https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States
   as 'wikipedia_national_parks.html' in the '_reference_data' folder
   of the project.
2) Save the webpage:
   https://en.wikipedia.org/wiki/List_of_Presidents_of_the_United_States
   as 'wikipedia_list_of_presidents.html' in the '_reference_data' folder
   of the project.
'''

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_established_date_from_page(filename):
    '''
    This function uses the Python library, BeautifulSoup to extract
    the park name and date established from a Wikipeida page saved as
    an html file.

    Parameters
    ----------
    filename : str
        Name of file containing saved Wikipedia page.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of park name and date established.
    '''

    soup = BeautifulSoup(open(filename), 'html.parser')

    df = pd.DataFrame(columns=['park_name', 'date_established'])

    # Find the table of National Parks.
    table_rows = soup.find_all('table')[1].find_all('tr')

    # For each row in the table, extract the name of the park, and
    # the date established and add to the dataframe.
    for row in table_rows[1:]:
        name = str(row.a.string)
        date = str(row.findAll('span', {'data-sort-value' : True})[0].string)
        date = datetime.strptime(date, '%B %d, %Y')
        df = df.append({'park_name': name, 'date_established': date},
                       ignore_index=True)

    return df

def get_list_of_presidents(filename):
    soup = BeautifulSoup(open(filename), 'html.parser')

    df = pd.DataFrame(columns=['president', 'start_date', 'end_date'])

    # Find the table of National Parks.
    table_rows = soup.find_all('table')[1].find_all('tr')

    print(table_rows)

    return df

def main():
    infile = '_reference_data/wikipedia_national_parks.html'
    #df = get_established_date_from_page(infile)
    df.to_csv('_reference_data/wikipedia_date_established.csv',
                index=False)

    infile = '_reference_data/wikipedia_list_of_presidents.html'
    df  = get_list_of_presidents(infile)
    df.to_csv('_reference_data/wikipedia_list_of_presidents.csv')

if __name__ == '__main__':
    main()
