---
layout: post
title: What is the National Park Service?
date: 08-05-2019
tags: national-park-service
---

The National Park Service, a new bureau of the Department of the Interior, was created on August 25, 1916, by the "Organic Act", signed into law by President Woodrow Wilson. At that time, there were 35 national parks and monuments managed by the Department of the Interior. Other parks existed at the time, managed by the War Department (now the Deparment of Defense), the Department of Agriculture, and the Forest Service. All these parks were brought under the auspices of the National Park Service by executive order in 1933, signed by XXX?

The National Park Sevice manages 419 official units as of today. The units are categorized into different designations depending on their natural and historical resources. Aside from the national parks introduced in the last post, designations include:
>National battlefields and national battlefield parks, national military parks, national historical parks, national historic sites, national lakeshores, national memorials, national monuments, national parks, national parkways, national preserves and reserves, national recration areas, national rivers and national wild and scenic rivers and riverways, national scenic trails, national seashores, and one international historic site.

New units are added every year by acts of Congress. The exception to this is national mouments. Teddy Roosevelt (my favorite president, go Teddy!) oversaw the establishment the Antiquities Act of 1906 which allows the sitting president to create national monuments by execute order. Seeing the destruction and looting of important geologic and historic areas of the American West, Roosevelt used the Antiquties Act to protect first, XXX, and then such sites as Mesa Verde, and Grand Canyon.

Map of NPS Sites
State distribution of NPS Sites
Designation counts

The map below, shows the locations of all 61 national parks. The map was created using park location data pulled from the NPS API and using the Python library, [Folium](https://python-visualization.github.io/folium/){:target="_blank"}, which uses the Leaflet.js library for map visualizations. A clickable version of the map that gives you the park name and a link to its website is found [here](https://goodmorningdata.github.io/assets/20190501_nps_parks_map_location_national_parks.html){:target="_blank"}.

![Map image]({{ site.baseurl }}/assets/20190501_nps_parks_map_location_national_parks.png){:target="_blank"}

National parks are found in 27 of the lower 48 states, in Alaska and Hawaii, and in the U.S. territories of American Samoa, and the U.S. Virgin Islands. California is the winner with 9 national parks and Alaska in a close second with 8.

![Bar chart image]({{ site.baseurl }}/assets/20190501_parks_per_state_national_parks.png){:target="_blank"}

Another way to look at national parks per state is a choropleth map. The winners are in blue.

![Choropleth map]({{ site.baseurl }}/assets/20190501_nps_state_count_choropleth_national_parks.png){:target="_blank"}

### Data Sources
The list of 419 official park units (as of 5/1/2019) broken out by designation comes from the [National Park System](https://www.nps.gov/aboutus/national-park-system.htm){:target="_blank"} page at nps.gov. Park location data, including latitude, longitude, and state(s) are from the National Park Service [API](https://www.nps.gov/subjects/digital/nps-data-api.htm){:target="_blank"}.

### Creating the Map
The clickable map was created using Folium.

```python

```

### Using the Scripts
Instructions to run the scripts are found in the readme in the GitHub repository found [here](https://github.com/goodmorningdata/nps){:target="_blank"}.

---
