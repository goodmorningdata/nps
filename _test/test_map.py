import pandas as pd
import folium

center_lower_48 = [39.833333,-98.583333]

folium_map = folium.Map(location=center_lower_48,
#location=[40.738, -73.98],
                        zoom_start = 5,
                        tiles = 'Stamen Terrain')
popup_text = popup_text = """{}<br>
                             Park Info: {}"""
popup_text = popup_text.format("Acadia", "Info")
marker = folium.Marker(location=[40.738, -73.98], popup="Park Name")
marker.add_to(folium_map)
folium_map.save("my_map.html")
