'''
This script reads the webpage,
https://www.census.gov/geographies/reference-files/2010/geo/state-area.html,
saved as an html file, and extracts the list of states and their area
in sqaure miles. This list is saved as a csv file,
'census_state_area_measurements.csv'

Required Libraries
------------------
pandas, BeautifulSoup, nps_shared

Dependencies
------------
1) Save the webpage:
   https://www.census.gov/geographies/reference-files/2010/geo/state-area.html,
   as 'census_state_area_measurements.html' in the '_reference_data'
   folder of this project.
'''

import pandas as pd
from bs4 import BeautifulSoup
from nps_shared import *

def get_state_area(filename):
    '''
    This function extracts state name and total area in sqaure miles
    from a census.gov page saved as an html file.

    Data source:
    https://www.census.gov/geographies/reference-files/2010/geo/state-area.html

    Parameters
    ----------
    filename : str
        Name of file containing saved census.gov page.

    Returns
    -------
    df : pandas DataFrame
        Dataframe of state name, state code, and area in square miles.
    '''

    soup = BeautifulSoup(open(filename), 'html.parser')

    df = pd.DataFrame(columns=['state_name', 'state_code', 'area'])

    table_rows = soup.find_all('tbody')[0].find_all('tr')
    for row in table_rows[6:]:
        table_cells = row.find_all('td')
        state_name = table_cells[0].text
        if len(state_name) > 0  and not state_name.startswith("Island Areas"):
            state_name = table_cells[0].text
            area = float(table_cells[1].text.replace(',',''))
            df = df.append({'state_name': state_name,
                            'state_code': state_name,
                            'area': area},
                            ignore_index = True)
    df.state_code = df.state_code.replace(us_state_name_to_code)

    return df

def main():
    infile = '_reference_data/census_state_area_measurements.html'
    df = get_state_area(infile)
    df.to_csv('_reference_data/census_state_area_measurements.csv', index=False)

if __name__ == '__main__':
    main()
