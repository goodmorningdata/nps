# NPS

NPS is a project built in Python to report on and analyze data concerning the National Park Service and its sites.

## Description

In an attempt to better understand the National Parks System, this project is being developed to find all available NPS data and consolidate it for the creation of useful maps, tables, and plots.

Read more about project progress on the blog, [Good Morning Data](goodmorningdata.com).

## Usage
### Setup
See below.

### Maps
The script, nps_create_maps.py, will generate location or size maps for all park sites or for a subset depending on the command line parameters.
* Running the script with no command line parameters will generate a location map for all park sites.
* Use 'nps_create_maps.py -h' to see all the possible values for command line parameters.
* Use the --parkset (-p) command line parameter to create a map for a specific park set. Ex. -p 'National Parks' will generate a map for National Park sites only.
* Use the --maptype (-m) command line parameter to generate either a location map, area map, or visitation map. Ex. -m 'area' will genearate an area map.


## Data Prep - Optional
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
2. Run the script, **_read_wikipedia_data.py_**. This creates the file, **_wikipedia_date_established.xlsx_** in the _reference_data folder.

### Park size report from the NPS website
1. Download the most recent acreage report from the NPS website at: https://www.nps.gov/subjects/lwcf/acreagereports.htm. Calendar Year Reports, Year = 2018. Place this file, named **_NPS-Acreage-12-31-2018.xlsx_** in the _acreage_data directory of this project.

### Visitation report from the NPS website
1. Download the most recent version of the "Annual Summary Report (1904 - Last Calendar Year)" report from the NPS website at https://irma.nps.gov/Stats/Reports/National. Select all years, all field names, and all parks. Choose "False" for "Summary Only?" Run and download.
2. Open the downloaded file in Excel and save as a .xlsx file with name **_Annual_Summary_Report_1904_Last_Calendar_Year.xlsx_** in the _visitor_data directory of this project.
3. Run the script, **_nps_read_visitor_data.py_**. This creates the file,
**_annual_visitors_by_park_1904_2018.xlsx_** in the _visitor_data directory.

### Create master DataFrame
Run the script, **_nps_create_master_df.py_** to consolidate all the datafiles into one master dataframe. This script creates the file, **_nps_parks_master_df.xlsx_** which will be used by all the visualization scripts.


## Support
Contact [goodmorningdata@gmail.com](mailto:goodmorningdata@gmail.com)


## Roadmap
* Automate the download of the visitation data and acreage data and remove all hardcoded file references.
* Add logic to scrape founding date from Wikipedia.
* Create a bubble map to show park acreage.
* Create a bubble map to show park visitation.
