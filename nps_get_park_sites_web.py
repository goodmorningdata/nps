'''
'''

from bs4 import BeautifulSoup
import pandas as pd

def get_park_sites_from_page(filename):
    '''
    '''
    soup = BeautifulSoup(open(filename), 'html.parser')

    df = pd.DataFrame(columns=['park_name', 'designation'])

    #prettyHTML = soup.prettify()
    #print(prettyHTML)

    ignore_list = ['Affiliated Areas', 'Authorized Areas',
                   'Commemorative Sites', 'National Heritage Areas',
                   'National Trails System',
                   'National Wild & Scenic Rivers System']

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
