'''Create Folium choropleth maps of National Park Service data.

Description.

Dependencies:

    *

This script contains the following functions:

    *
'''

def create_choropleth_map():
    ''' Create an empty Folium map.

    This function creates a Folium map object, centered on the lat/long
    center of the lower 48 states.

    Parameters
    ----------
    None

    Returns
    -------
    map : Folium map object
      Empty Folium map.
    '''

    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48,
                     zoom_start = 4)

    return map

def add_choropleth_color_to_map(map, df):
    ''' Add cholorpleth color to map based on number of parks per state

    This function...

    Parameters
    ----------
    map : Folium map object
      Folium map to add choropleth color to.

    df : Pandas DataFrame
      DataFrame of all parks to add to the map.

    Returns
    -------
    map : Folium map object
      Folium map with choropleth color added.
    '''

    print (df['states'])
    state_list = df['states'].values
    print(state_list)

    return map

def main():
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    parser = argparse.ArgumentParser()

    # The user can specify the set of parks to map using the command
    # line parameter, 'parkset'. If no parameter specified, all park
    # sites are added to the map.
    parser.add_argument('-p', '--parkset', type=str,
           help = "Set of parks for which to display locations. If not \
                  specified, all park sites will be mapped.\
                  Possible values are: 'National Park', 'National Monument', \
                    'National Preserve or Reserve', 'National Lakeshore or \
                     Seashore', 'National River', 'National Trail', 'National \
                     Historic Site', 'National Memorial', 'National Recreation \
                     Area', 'National Parkway', 'National Heritage Area', \
                    'Affiliated Area', 'Other'")

    if args.parkset:
        map_df = df[df.park_set == args.parkset]
    else: map_df = df

    print("Creating parks per state map for the park set, '"
          + args.parkset + "'.")
    park_map = create_choropleth_map()
    park_map = add_choropleth_color_to_map(park_map, map_df)

if __name__ == '__main__':
    main()
