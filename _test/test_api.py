"""
To Do:
  - List of parks with addresses and satellite locations
  - List of parks and other NPS sites
  - Create a map of these locations
  - Find weather data for each location
"""

import urllib.request, urllib.parse, urllib.error
import json
import pandas as pd
import gmplot
import folium
import sys, getopt
import argparse

apikey = 'itjuKSNUeQFjDlscdfr6H5es8FFlnVqQahBHaMSU'

def retrieve_data(url):
    print('')
    print('Retrieving', url)
    connection = urllib.request.urlopen(url)
    data = connection.read().decode()
    headers = dict(connection.getheaders())
    print('Limit', headers['X-RateLimit-Limit'])
    print('Remaining', headers['X-RateLimit-Remaining'])

    try:
        js = json.loads(data)
    except:
        js = None
    if not js:
        print('==== Failure to Retrieve ====')
    #js = json.loads(data)

    # Option to print the json.
    #print(json.dumps(js, indent=4))
    return js

# Visitor data pulled from - https://irma.nps.gov/Stats/SSRSReports/National%20
# Reports/Annual%20Visitation%20By%20Park%20(1979%20-%20Last%20Calendar%20Year)
def read_visitor_data():
    #df = pd.read_csv('annual_visitation_by_park_2008_2017.csv', header=4)
    df = pd.read_excel('annual_visitation_by_park_2008_2017.xlsx', header=8)
    df = df[['Park Name', 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]]
    # TO-DO: Strip out the park designation and make a new column.
    #print(df)

def get_nps_code(park_name):
    list = park_name.split(' ')
    if len(list) == 1:
        return list[0][:4].lower()
    else:
        return list[0][:2].lower() + list[1][:2].lower()


def read_wikipedia_data():
    df = pd.read_excel('20181225_wikipedia_list_of_national_parks.xlsx',
                       header=0,
                       names=['Name', 'Location', 'State', 'Date Established',
                              'Area (2017)', 'Visitors (2017)', 'Description'])
    df['nps_code'] = df.Name.apply(lambda x: get_nps_code(x))

def get_api_data():
    domain = 'https://developer.nps.gov/api/v1'
    path = '/parks?'
    domain_path = domain + path

    # Retrieve the total number of park sites.
    url = domain_path + urllib.parse.urlencode({'limit': 1, 'api_key': apikey})
    js = retrieve_data(url)
    total_sites = js['total']
    print('Total number of park sites: ', js['total'])

    # Retrieve all park sites using the total number as the limit.
    url = domain_path + urllib.parse.urlencode({'limit': total_sites, 'api_key': apikey})
    js = retrieve_data(url)

    # Create parks dataframe.
    park_list = []
    for i, item in enumerate(js['data']):
        park_list.append(item)
        parks_df = pd.DataFrame(park_list)

        # Data Cleanup - Assign the correct designation to National Park of American
        # Samoa. Designation is blank via api.
        parks_df.at[parks_df[parks_df.fullName == 'National Park of American Samoa'].index.item(), 'designation'] = 'National Park'

        # Split latLong column into two columns.
        parks_df['lat'] = pd.to_numeric(parks_df['latLong'].str.split(',').str.get(0).str[4:])
        parks_df['long'] = pd.to_numeric(parks_df['latLong'].str.split(',').str.get(1).str[6:])

        # Create a dataframe of just the National Parks.
        national_parks_df = parks_df[parks_df.designation.isin(['National Park',
        'National Parks', 'National Park & Preserve', 'National and State Parks'])]

        center = national_parks_df.lat.mean(), national_parks_df.long.mean()
        folium_map = folium.Map(location=center,
                                zoom_start = 4,
                                tiles = 'Stamen Terrain')
        for index, row in national_parks_df.iterrows():
            label = row.fullName.split('National Park')[0].strip()
            if not(label):
                label = "American Samoa"
                popup = folium.Popup(label, parse_html=True)
                marker = folium.Marker(location=[row.lat, row.long], popup=popup)
                marker.add_to(folium_map)

        folium_map.save("nps_parks_map.html")

# An attempt to use
def main(argv):
    park_code = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o", ["park_code="])
    except getopt.GetoptError:
        print ('api_test.py -p <park code>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-p':
            park_code = arg
            #print 'api_test.py -p <park code>'
    print ('Park code is: ', park_code)

    #get_api_data()
    read_visitor_data()
    read_wikipedia_data()

if __name__ == "__main__":
    main(sys.argv[1:])

#path = '/alerts?'
#path = '/articles?'
#path = '/campgrounds?'
#path = '/events?'
#path = '/lessonplans?'
#path = '/newsreleases?'
#path = '/people?'
#path = '/places?'
#path = '/visitorcenters?'
