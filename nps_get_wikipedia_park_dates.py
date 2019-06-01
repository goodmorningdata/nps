'''
This script uses the Python library, BeautifulSoup to scrape data
from the following Wikipedia pages, and to save the resulting
data to a csv file.
- "List of national lakeshores and seashores of the United States"
- ""
- ""
- ""
- ""

Required Libraries
------------------
BeautifulSoup, pandas, datetime

Dependencies
------------
1) Save the webpage:
   XXX
   as 'wikipedia_national_lakeshores_and_seashores.html' in the
   '_reference_data' folder of the project.
2) Save the webpage:
   XXX
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
    return df

def get_nmem_established_date(filename):
    ''' There are two sites on this list that are not on the
    official NPS unit list from nps.gov. They are: Medgar and Myrlie
    Evers Home, and Mill Springs Battlefield. They are recent sites with
    status - "Pending acquisition of property".'''

    soup = BeautifulSoup(open(filename), 'html.parser')
    df = pd.DataFrame(columns=['park_name', 'date_established'])
    return df

def get_nm_established_date(filename):
    soup = BeautifulSoup(open(filename), 'html.parser')
    df = pd.DataFrame(columns=['park_name', 'date_established'])

    # Find the table of National Monuments.
    table_rows = soup.find_all('table')[2].find_all('tr')

    # For each row in the table, get the park name and date established.
    # Check if the agency is the NPS. If it is, add the National
    # Monument to the dataframe.
    for row in table_rows[1:]:
        row_cells = row.find_all('td')
        name = row_cells[0].text.rstrip()
        agency = row_cells[2].text.rstrip()
        date = pd.to_datetime(row_cells[4].span.text)
        if agency.find('NPS') == 0:
            df = df.append({'park_name': name,
                            'date_established': date
                           },
                           ignore_index=True)

    return df

def get_np_established_date(filename):
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

def get_npkwy_established_date(filename):
    soup = BeautifulSoup(open(filename), 'html.parser')
    df = pd.DataFrame(columns=['park_name', 'date_established'])
    return df

def main():
    # National Battlefields
    # National Battlefield Parks
    # National Battlefield Sites
    # National Military Parks
    # National Historical Parks
    # National Historic Sites
    # International Historic Sites

    # National Lakeshores and Seashores
    infile = '_reference_data/wikipedia_national_lakeshores_and_seashores.html'
    df.append(get_nlns_established_date(infile), ignore_index=True)

    # National Memorials
    infile = '_reference_data/wikipedia_national_memorials.html'
    #df.append(get_nmem_established_date(infile), ignore_index=True)

    # National Monuments
    infile = '_reference_data/wikipedia_national_monuments.html'
    df.append(get_nm_established_date(infile), ignore_index=True)

    # National Parks
    infile = '_reference_data/wikipedia_national_parks.html'
    df = get_np_established_date(infile)

    # National Parkways
    infile = '_reference_data/wikipedia_national_parkways.html'
    #df.append(get_npkwy_established_date(infile), ignore_index=True)

    # National Preserves
    # National Reserves
    # National Recreation Areas
    # National Rivers
    # National Wild and Scenic Rivers and Riverways
    # National Scenic Trails
    # Other Designations

    df.to_csv('_reference_data/wikipedia_date_established.csv', index=False)

if __name__ == '__main__':
    main()
