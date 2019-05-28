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
        df = df.append({'park_name': name,
                        'date_established': date
                       },
                       ignore_index=True)

    return df

def get_list_of_presidents(filename):
    '''
    This function uses the Python library, BeautifulSoup to extract
    each U.S. president name and the start and end dates of presidency
    from a Wikipedia page saved as an html file.

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

    df = pd.DataFrame(columns=['president', 'start_date', 'end_date'])

    # Find the table of National Parks.
    table_rows = soup.find_all('table')[1].find_all('tr')
    for row in table_rows[2:]:
        table_cells = row.find_all('td')
        if len(table_cells) > 3:
            name = table_cells[3].a.text
            dates = table_cells[1].find_all('span')
            if len(dates) > 0:
              start_date = dates[0].text.split('[')[0]
              if len(dates) > 1:
                  end_date = dates[1].text
              else:
                  end_date = datetime.strptime(start_date, '%B %d, %Y')
                  end_date = end_date.replace(year = end_date.year + 4)
            else:
                dates = table_cells[1].text.split('–')
                start_date = dates[0]
                end_date = dates[1].split('(')[0]

            df = df.append({'president': name,
                            'start_date': start_date,
                            'end_date': end_date
                           },
                           ignore_index=True)

    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])

    return df

def main():
    infile = '_reference_data/wikipedia_national_parks.html'
    df = get_established_date_from_page(infile)
    df.to_csv('_reference_data/wikipedia_date_established.csv', index=False)

    infile = '_reference_data/wikipedia_list_of_presidents.html'
    df = get_list_of_presidents(infile)
    df.to_csv('_reference_data/wikipedia_list_of_presidents.csv', index=False)

if __name__ == '__main__':
    main()
