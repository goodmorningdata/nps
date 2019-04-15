# NPS

NPS is a project built in Python to report on and analyze data concerning the National Park Service and its sites.

## Description

In an attempt to better understand the National Parks System, this project is being developed to find all available NPS data and consolidate it for the creation of useful maps, tables, and plots.

Read more about project progress on the blog, [Good Morning Data](goodmorningdata.com).

##

## Data Prep
If you would like to download and process your own input files instead of using the ones included in the project, you can do so. The data comes from a number of sources and the steps to get it ready are found below by source.
### Config File
Create a file, **_nps_config.py_**, in your home folder. This file will be used to store your personal API keys.
### NPS API
1. Register for a NPS API key [here](https://www.nps.gov/subjects/developer/get-started.htm).
2. Add the following line to your **_nps_config.py_** file, replacing YOUR KEY HERE with your NPS API key.
```
apikey = 'YOUR KEY HERE'
```
3. Run the script, **_nps_create_park_lookup.py_** to pull data from the NPS API and create the park lookup dataframe. This creates the file **_nps_park_lookup.xlxs_** in your NPS project folder.
### Established date from Wikipedia
1. Save the web page, https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States, as an html file named, **_wikipedia_national_parks.html_** in the _reference_data folder of the project.
2. Run the script, **_read_wikipedia_data.py_**. The creates the file, 
###


3. Run the script, nps_create_master_df.py to create the master parks dataframe which also includes visitation data and acreage data.

## Usage

### Setup
1. Register for a NPS API key [here](https://www.nps.gov/subjects/developer/get-started.htm).
2. Run the script, nps_create_park_lookup.py to pull data from the NPS API and create the park lookup dataframe.
3. Run the script, nps_create_master_df.py to create the master parks dataframe which also includes visitation data and acreage data.

### Maps
The script, nps_create_maps.py, will generate location or size maps for all park sites or for a subset depending on the command line parameters.
* Running the script with no command line parameters will generate a location map for all park sites.
* Use 'nps_create_maps.py -h' to see all the possible values for command line parameters.
* Use the --parkset (-p) command line parameter to create a map for a specific park set. Ex. -p 'National Parks' will generate a map for National Park sites only.
* Use the --maptype (-m) command line parameter to generate either a location map, area map, or visitation map. Ex. -m 'area' will genearate an area map.

## Support
Contact [goodmorningdata@gmail.com](mailto:goodmorningdata@gmail.com)

## Roadmap
* Automate the download of the visitation data and acreage data and remove all hardcoded file references.
* Add logic to scrape founding date from Wikipedia.
* Create a bubble map to show park acreage.
* Create a bubble map to show park visitation.
