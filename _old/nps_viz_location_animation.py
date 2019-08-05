import argparse
import pandas as pd
import folium

def add_park_location_to_map(map, park):
    map_icon = folium.Icon(color="green",
                           prefix="fa",
                           icon="tree")

    popup_string = (park.park_name + ", "
                   + park.date_established.strftime('%B %-d, %Y')
                   ).replace("'", r"\'")
    popup_html = folium.Html(popup_string, script=True)

    folium.Marker(location = [park.lat, park.long],
                  icon = map_icon,
                  popup = folium.Popup(popup_html)
                 ).add_to(map)

    return map

def main():
    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)

    parser = argparse.ArgumentParser()

    # The user can specify the set of parks to map using the command
    # line parameter, 'parkset'. If no parameter specified, all park
    # sites are added to the map.
    parser.add_argument("-p", "--parkset", type=str,
           help = "Set of parks for which to display locations. If not \
                  specified, all park sites will be mapped.\
                  Possible values are: 'National Park', 'National Monument', \
                  'National Preserve or Reserve', 'National Lakeshore or \
                  Seashore', 'National River', 'National Trail', 'National \
                  Historic Site', 'National Memorial', 'National Recreation \
                  Area', 'National Parkway', 'National Heritage Area', \
                  'Affiliated Area', 'Other'")

    args = parser.parse_args()

    if args.parkset:
        df_map = df[df.park_set == args.parkset]
        print("Creating park location map for the park set, '"
              + args.parkset + "'.")
    else:
        df_map = df
        print("Creating park location map for all NPS sites.")

    # Sort by date established.
    df_map = df_map.sort_values(by=["date_established"]).reset_index()

    center_lower_48 = [39.833333, -98.583333]
    map = folium.Map(location = center_lower_48, zoom_start = 3,
                     control_scale = True, tiles = 'Stamen Terrain')

    for index, row in df_map.iterrows():
        map = add_park_location_to_map(map, row)
        map.save('_output/animation/nps_parks_map_animation_' + str(index) + '.html')

if __name__ == "__main__":
    main()
