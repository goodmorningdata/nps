'''
This script uses the Python library, BeautifulSoup to scrape data
from the following Wikipedia pages, and to save the resulting
data to a csv file.
- "List of national lakeshores and seashores of the United States"
- "List of national memorials of the United States"
- ""
- ""
- ""

Required Libraries
------------------
BeautifulSoup, pandas, datetime

Dependencies
------------
1) Save the webpage:
   https://en.wikipedia.org/wiki/List_of_national_lakeshores_and_seashores_of_the_United_States
   as 'wikipedia_national_lakeshores_and_seashores.html' in the
   '_reference_data' folder of the project.
2) Save the webpage:
   https://en.wikipedia.org/wiki/List_of_national_memorials_of_the_United_States
   as 'wikipedia_national_memorials.html' in the '_reference_data'
   folder of the project.
3) Save the webpage:
   XXX
   as 'wikipedia_national_monuments.html' in the '_reference_data'
   folder of the project.
4) Save the webpage:
   XXX
   as 'wikipedia_national_parks.html' in the '_reference_data' folder
   of the project.
5) Save the webpage:
   XXX
   as 'wikipedia_national_parkways.html' in the '_reference_data' folder
   of the project.
'''

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

'''
The following functions use the Python library, BeautifulSoup, to
extract the park name and date established from a Wikipeida page saved
as an html file. The extracted items are added to a dataframe which is
returned to the calling fuction.

Parameters
----------
filename : str
    Name of file containing saved Wikipedia page.

Returns
-------
df : pandas DataFrame
    Dataframe of park name and date established.
'''

def get_nlns_established_date(filename):
    soup = BeautifulSoup(open(filename), 'html.parser')
    df = pd.DataFrame(columns=['park_name', 'date_established'])

    table_rows = (soup.find_all('table')[1].find_all('tr')[1:] +
                  soup.find_all('table')[2].find_all('tr')[1:])
    for row in table_rows:
        name = row.find_all('th')[0].text.rstrip()
        date = pd.to_datetime(row.find_all('td')[2].text)
        df = df.append({'park_name': name,
                        'date_established': date
                       },
                       ignore_index=True)

    return df

def get_nmem_established_date(filename):
    soup = BeautifulSoup(open(filename), 'html.parser')
    df = pd.DataFrame(columns=['park_name', 'date_established'])

    table_rows = soup.find_all('table')[1].find_all('tr')[1:]
    for row in table_rows:
        name = row.find_all('th')[0].text.rstrip()
        date = pd.to_datetime(row.find_all('td')[2].text)
        df = df.append({'park_name': name,
                        'date_established': date
                       },
                       ignore_index=True)

    return df

def get_nm_established_date(filename):
    ''' There are two sites on this list that are not on the
    official NPS unit list from nps.gov. They are: Medgar and Myrlie
    Evers Home, and Mill Springs Battlefield. They are recent sites with
    status - "Pending acquisition of property".'''

    soup = BeautifulSoup(open(filename), 'html.parser')
    df = pd.DataFrame(columns=['park_name', 'date_established'])

    table_rows = soup.find_all('table')[2].find_all('tr')[1:]
    for row in table_rows:
        row_cells = row.find_all('td')
        name = row_cells[0].text.rstrip()
        agency = row_cells[2].text.rstrip()
        date = pd.to_datetime(row_cells[4].span.text)
        # Only add site to df if agency is the NPS.
        if agency.find('NPS') == 0:
            df = df.append({'park_name': name,
                            'date_established': date
                           },
                           ignore_index=True)

    return df

def get_np_established_date(filename):
    soup = BeautifulSoup(open(filename), 'html.parser')
    df = pd.DataFrame(columns=['park_name', 'date_established'])

    table_rows = soup.find_all('table')[1].find_all('tr')[1:]

    # For each row in the table, extract the name of the park, and
    # the date established and add to the dataframe.
    for row in table_rows:
        name = row.find_all(['th','td'])[0].text.replace('*','').rstrip()
        date = pd.to_datetime(
                   row.find_all(['th', 'td'])[3].text.rstrip().split('[')[0])
        df = df.append({'park_name': name,
                        'date_established': date
                       },
                       ignore_index=True)

    return df

def get_npkwy_established_date(filename):
    soup = BeautifulSoup(open(filename), 'html.parser')
    df = pd.DataFrame(columns=['park_name', 'date_established'])

    table_rows = soup.find_all('table')[1].find_all('tr')[1:]
    for row in table_rows:
        name = row.find_all('th')[0].text.rstrip()
        date = pd.to_datetime(row.find_all('td')[4].text)
        df = df.append({'park_name': name,
                        'date_established': date
                       },
                       ignore_index=True)

    return df

def main():
    df = pd.DataFrame(columns=['park_name', 'date_established'])

    # National Battlefields
    # National Battlefield Parks
    # National Battlefield Sites
    # National Military Parks
    # National Historical Parks
    # National Historic Sites
    # International Historic Sites

    # National Lakeshores and Seashores
    infile = '_reference_data/wikipedia_national_lakeshores_and_seashores.html'
    df = df.append(get_nlns_established_date(infile), ignore_index=True)

    # National Memorials
    infile = '_reference_data/wikipedia_national_memorials.html'
    df = df.append(get_nmem_established_date(infile), ignore_index=True)

    # National Monuments
    infile = '_reference_data/wikipedia_national_monuments.html'
    df = df.append(get_nm_established_date(infile), ignore_index=True)

    # National Parks
    infile = '_reference_data/wikipedia_national_parks.html'
    df = df.append(get_np_established_date(infile), ignore_index=True)

    # National Parkways
    infile = '_reference_data/wikipedia_national_parkways.html'
    df = df.append(get_npkwy_established_date(infile), ignore_index=True)

    # National Preserves
    # National Reserves
    # National Recreation Areas
    # National Rivers
    # National Wild and Scenic Rivers and Riverways
    # National Scenic Trails
    # Other Designations

    print(df)

    df.to_csv('_reference_data/wikipedia_date_established.csv', index=False)

if __name__ == '__main__':
    main()
