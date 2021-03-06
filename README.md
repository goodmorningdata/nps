# NPS
NPS is a project built in Python to report on and analyze data concerning the National Park Service and its sites.

## Description
In an attempt to better understand the National Parks System, this project is being developed to find all available NPS data and consolidate it for the creation of useful maps, tables, and plots.

Read more about project progress on the blog, [Good Morning Data](https://goodmorningdata.github.io).

## Usage
### Setup
The only setup necessary is the cloning of this repository to your computer. You can then run the below visualizations. All input data files are included in the repository. If you would like to generate your own input files, please see the instructions under the Data Prep section below.

### Designation command line parameter
All of the visualization scripts take a command line parameter, "designation", which allows the user to specify the park designation to add to the visualizations. Possible designation values are: "National Battlefields", "National Battlefield Parks", "National Battlefield Sites", "National Military Parks", "National Historical Parks", "National Historic Sites", "International Historic Sites", "National Lakeshores", "National Memorials", "National Monuments", "National Parks", "National Parkways", "National Preserves", "National Reserves", "National Recreation Areas", "National Rivers", "National Wild and Scenic Rivers and Riverways", "National Scenic Trails", "National Seashores", "Other Designations".

#### Example usage:
To run the location visualization for just the National Parks:<br/>
&nbsp;&nbsp;$ python3 nps_viz_location.py -d "National Parks"<br/>
To show the command line parameters for a script:<br/>
&nbsp;&nbsp;$ python3 nps_viz_location.py -h

### Park location visualizations
Run the script, **<i>nps_viz_location.py</i>**, to create a map showing the locations of all the parks. The park location markers have a popup that gives a clickable park name, which when clicked, takes the user to the NPS web page for the park. Limit the number of parks using the [designation parameter](#designation-command-line-parameter) described above.
#### Output
* Map file: nps_parks_map_location_<i>designation</i>.html

### Park size visualizations
Run the script, **<i>nps_viz_size.py</i>**, to create a map showing the locations of all the parks, marked with a circle marker with size corresponding to the park's size. The circle markers have a hoverable tooltip telling the park name and size in square miles. Limit the number of parks using the [designation parameter](#designation-command-line-parameter) described above.
#### Output
* Map file: nps_parks_map_size_<i>designation</i>.html
* Table: nps_parks_sorted_by_size_<i>designation</i>.xlsx, nps_parks_sorted_by_size_<i>designation</i>.html

### Park visits visualizations
Run the script, **<i>nps_viz_visitor.py</i>**, to create a map showing the locations of all the parks, marked with a circle marker with size corresponding to the number of visits to the park in the latest year that data is available. The circle markers have a hoverable tooltip telling the park name and number of visits. This script also creates a number of plots to take a closer look at the data. Limit the number of parks using the [designation parameter](#designation-command-line-parameter) described above.
#### Output
* Map file: nps_parks_map_visits_<i>designation</i>.html
* Table: nps_parks_sorted_by_visits_<i>designation</i>.xlsx, nps_parks_sorted_by_visits_<i>designation</i>.html
* Plots: park_visits_by_year_highest_10_<i>designation</i>.png, park_visits_by_year_lowest_10_<i>designation</i>.png, park_visits_histogram_<i>designation</i>.png, total_park_visits_vs_year_<i>designation</i>.png, total_estimated_park_visits_vs_year_<i>designation</i>.png

### Choropleths
Run the script, **<i>nps_viz_choropleth.py</i>**, to create a cholopleth of the United States with state color representing the number of parks in that state. Limit the number of parks using the [designation parameter](#designation-command-line-parameter) described above.
#### Output
* nps_state_count_choropleth_<i>designation</i>.html

## Data Prep - Optional
If you would like to download and process your own input files instead of using the ones included in the project, you can do so. The data comes from a number of sources and the steps to get it ready are found below by source.

### Config File
Create a file, **<i>nps_config.py</i>**, in your home folder. This file will be used to store your personal API keys.

### NPS API
1. Register for a NPS API key [here](https://www.nps.gov/subjects/developer/get-started.htm).
2. Add the following line to your **<i>nps_config.py</i>** file, replacing YOUR KEY HERE with your NPS API key.
```
apikey = 'YOUR KEY HERE'
```
3. Run the script, **<i>nps_get_park_sites_api.py</i>**, to pull data from the NPS API. This creates the file, nps_park_sites_api.xlxs, in the _reference_data folder.

### Official Park Units
1. https://www.nps.gov/aboutus/national-park-system.htm, as 'national_park_system.html' in the '_reference_data' folder.
2. Run the script, **<i>nps_get_park_sites_web.py</i>**, to read the html file and create the file, nps_park_sites_web.xlxs, in the _reference_data folder.

### Presidential terms
1. Save the web page, https://en.wikipedia.org/wiki/List_of_Presidents_of_the_United_States, as 'wikipedia_list_of_presidents.html' in the _reference_data folder.
2. Run the script, **<i>nps_get_wikipedia_presidents.py</i>**, to read the html file and create the file, wikipedia_list_of_presidents.csv, in the _reference_data folder.

### Park size report from the NPS website
1. Download the most recent acreage report from the NPS website at: https://www.nps.gov/subjects/lwcf/acreagereports.htm. Calendar Year Reports, Year = 2018. Place this file, **<i>NPS-Acreage-12-31-2018.xlsx</i>**, in the _reference_data folder.

### Visitation report from the NPS website
1. Download the most recent version of the "Annual Summary Report (1904 - Last Calendar Year)" report from the NPS website at https://irma.nps.gov/Stats/Reports/National. Select all years, all field names, and all parks. Choose "False" for "Summary Only?" Run and download.
2. Open the downloaded file in Excel and save as a .xlsx file with name, Annual_Summary_Report_1904_Last_Calendar_Year.xlsx, in the _reference_data folder.
3. Run the script, **<i>nps_read_visitor_data.py</i>**. This creates the file, annual_visitors_by_park_1904_2018.xlsx in the _reference_data folder.

### U.S. census data from census.gov
Coming soon.

### Create master DataFrame
Run the script, **<i>nps_create_master_df.py</i>** to consolidate all the datafiles into one master dataframe. This script creates the file, nps_parks_master_df.xlsx, which will be used by all the visualization scripts.

## Support
Contact [goodmorningdata@gmail.com](mailto:goodmorningdata@gmail.com)

## Roadmap
Coming soon.
___
_README updated on June 10, 2019_
___
