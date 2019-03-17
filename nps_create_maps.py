import pandas as pd
import folium

def add_locations(map, df, park_set):

    if park_set == 'national parks':
        df = df[df.designation.isin(national_parks)]

    # Plot each park site on the map
    for _, row in df.iterrows():
        marker = folium.Marker(location=[row.lat, row.long],
                               icon=folium.Icon(color=row.color,
                                                prefix='fa',
                                                icon=row.icon),
                               popup = folium.Popup(row.park_name,
                                                    parse_html=True))

        marker.add_to(park_map)

    # Print the mapped park List
    print(df[['park_code', 'park_name', 'designation', 'states']])
    print('Count: ', df.shape[0])

    return map

# ** Main program block **

# Read in the park data
df = pd.read_excel('df_master.xlsx', header=0)
#df[['color', 'icon']] = [['black', 'question']]
df['color'], df['icon'] = 'black', 'question'
#df['icon'] = 'question'

# NPS designations found here: https://www.nps.gov/articles/nps-designations.htm
# National parks
national_parks = ['National Park', 'National Park & Preserve',
                  'National and State Parks']
df.loc[df.designation.isin(national_parks), ['color', 'icon']] = 'darkgreen', 'tree'

# National monuments
monuments = ['National Monument', 'National Monument & Preserve',
             'Part of Statue of Liberty National Monument',
             'National Monument and Historic Shrine',
             'National Monument of America']
df.loc[df.designation.isin(monuments), ['color', 'icon']] = 'darkblue', 'monument'

# National preserves and reserves
preserves_reserves = ['National Preserve', 'National Reserve']
df.loc[df.designation.isin(preserves_reserves), ['color', 'icon']] = 'beige', 'pagelines'

# National lakeshores and seashores
lakeshores_seashores = ['National Lakeshore', 'National Seashore']
df.loc[df.designation.isin(lakeshores_seashores), ['color', 'icon']] = 'lightblue', 'water'

# National rivers and wild and scenic riverways
rivers = ['National River & Recreation Area', 'National Scenic River',
          'National River', 'Scenic & Recreational River', 'Wild River',
          'National River and Recreation Area', 'National Recreational River',
          'National Scenic Riverway', 'Wild & Scenic River',
          'National Scenic Riverways', 'National Wild and Scenic River']
df.loc[df.designation.isin(rivers), ['color', 'icon']] = 'lightblue', 'water'

# National scenic trails and National historic trails
trails = ['National Scenic Trail', 'National Geologic Trail',
          'National Historic Trail']
df.loc[df.designation.isin(trails), ['color', 'icon']] = 'beige', 'sign'

# National historic sites, national military parks, national battlefield parks,
# national battlefield site, national battlefields, national historical parks,
# national historical parks, international historic site
historic_sites = ['National Historical Park', 'National Historic Site',
                  'National Historic Area', 'National Historical Reserve',
                  'Part of Colonial National Historical Park',
                  'National Historical Park and Preserve',
                  'National Historical Park and Ecological Preserve'
                  'National Historic District' 'Ecological & Historic Preserve',
                  'International Historic Site', 'National Heritage Area',
                  'International Park', 'National Battlefield',
                  'National Battlefield Site', 'National Military Park',
                  'National Battlefield Park', 'National Historic Landmark District']
df.loc[df.designation.isin(historic_sites), ['color', 'icon']] = 'red', 'university'

# National memorials
memorials = ['National Memorial', 'Memorial']
df.loc[df.designation.isin(memorials), ['color', 'icon']] = 'blue', 'monument'

# National recreation areas
recreation_areas = ['National Recreation Area']
df.loc[df.designation.isin(recreation_areas), ['color', 'icon']] = 'beige', 'pagelines'

# National parkways
parkways = ['Parkway', 'Memorial Parkway']
df.loc[df.designation.isin(parkways), ['color', 'icon']] = 'beige', 'road'

# National heritage areas
heritage_areas = ['National Heritage Partnership',  'Heritage Area',
                 'National Heritage Corridor', 'Cultural Heritage Corridor',
                 'Heritage Center']
df.loc[df.designation.isin(heritage_areas), ['color', 'icon']] = 'red', 'univeristy'

# Other affiliated sites
affiliated_areas = ['Affiliated Area']
df.loc[df.designation.isin(affiliated_areas), ['color', 'icon']] = 'orange', 'map-marker-alt'

# Others
others = ['Park', 'Other']
df.loc[df.designation.isin(others), ['color', 'icon']] = 'orange', 'map-marker-alt'



# Some global constants
center_lower_48 = [39.833333, -98.583333]

# Set up folium map
park_map = folium.Map(location = center_lower_48,
                      zoom_start = 4,
                      control_scale = True,
                      #tiles = 'Stamen Toner')
                      tiles = 'Stamen Terrain')

# ???????? What to do about parks with no lat/longs???????

# Add National Parks to the map
#add_locations(park_map,
#              df[df.designation.isin(national_parks) & ~df.lat.isnull()])

# Add National Monuments to the map
#add_locations(park_map,
#              df[df.designation.isin(monuments) & ~df.lat.isnull()])

# Add Historic Sites to the map
#add_locations(park_map,
#              df[df.designation.isin(historic_sites) & ~df.lat.isnull()])

add_locations(park_map,
              df[~df.lat.isnull()],
              'national parks')

# Folium legend code from:
# https://medium.com/@bobhaffner/creating-a-legend-for-a-folium-map-c1e0ffc34373
legend_html = '''
    <div style="position:fixed;
    bottom: 50px; left: 50px; width: 200px; height: 90px;
    border:2px solid grey; z-index:9999; font-size:14px;
    background-color: white;
    ">&nbsp; Cool Legend <br>
    &nbsp; National Parks &nbsp; <i class="fa fa-tree fa-2x"
    #             style="color:darkgreen"></i><br>
    </div>
    '''

    #&nbsp; East &nbsp; <i class="fa fa-map-marker fa-2x"
    #             style="color:green"></i><br>
    #&nbsp; West &nbsp; <i class="fa fa-map-marker fz-2x"
    #             style="color:red"></i>


# Add legend to the map
#park_map.get_root().html.add_child(folium.Element(legend_html))

# Save map to .html
park_map.save('nps_parks_map.html')
