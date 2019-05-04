'''
Read list of NPS sites from nps.gov.

This script reads the webpage,
https://www.nps.gov/aboutus/national-park-system.htm, saved as an html
file, and extracts the list of official park units and their
designations. There are 419 units as of May 1, 2019. This list is saved
as an Excel file, 'nps_park_sites_web.xlsx'.

Required libraries: pandas, BeautifulSoup.

Dependencies:
    * Save the webpage:
      https://www.nps.gov/aboutus/national-park-system.htm, as
      'national_park_system.html' in the _reference_data folder of this
      project.
'''

from bs4 import BeautifulSoup
import pandas as pd

def get_park_sites_from_page(filename):
    '''Extract park names and designations from page.

    This function uses the BeautifulSoup library to extract each park
    name and its designation from the list of official units in the
    web page.

    Parameters
    ----------
    filename : str : Name of html file to read.

    Returns
    -------
    df : pandas DataFrame : Dataframe of park names and designations.
    '''
    soup = BeautifulSoup(open(filename), 'html.parser')

    df = pd.DataFrame(columns=['park_name', 'designation'])

    # Pretty print html.
    #prettyHTML = soup.prettify()
    #print(prettyHTML)

    # "Related Areas" are also listed on this web page. Ignore these.
    ignore_list = ["Affiliated Areas", "Authorized Areas",
                   "Commemorative Sites", "National Heritage Areas",
                   "National Trails System",
                   "National Wild & Scenic Rivers System"]

    # Use BeautifulSoup to parse the html tree and extract the park
    # names and designations.
    for link in soup.select('.collapsible-item-title-link'):
        designation = link.text.split('(')[0].strip()
        if designation not in ignore_list:
            parks = (link.parent.parent.next_sibling.next_sibling.text
                     .split('\n'))
            for park in parks:
                if park:
                    df = df.append({'park_name': park.split(',')[0].strip(),
                                    'designation': designation},
                                    ignore_index=True)

    return df

def main():
    filename = '_reference_data/national_park_system.html'
    df = get_park_sites_from_page(filename)
    df.to_excel('nps_park_sites_web.xlsx', index=False)

if __name__ == '__main__':
    main()
