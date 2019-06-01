'''
This script uses the Python library, BeautifulSoup to scrape data
from the Wikipedia page, "List of Presidents of the United States", and
to save the resulting dataframe to a csv files.

Required Libraries
------------------
BeautifulSoup, pandas, datetime

Dependencies
------------
1) Save the webpage:
   https://en.wikipedia.org/wiki/List_of_Presidents_of_the_United_States
   as 'wikipedia_list_of_presidents.html' in the '_reference_data' folder
   of the project.
'''

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_list_of_presidents(filename):
    '''
    This function extracts each U.S. president name and the start and
    end dates of presidency from a Wikipedia page saved as an html file.

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
    infile = '_reference_data/wikipedia_list_of_presidents.html'
    df = get_list_of_presidents(infile)
    df.to_csv('_reference_data/wikipedia_list_of_presidents.csv', index=False)

if __name__ == '__main__':
    main()
