# NPS

NPS is a project built in Python to report on and analyze data concerning the National Park Service and its sites.

## Description

In an attempt to better understand the National Park System, this project is being developed to find all available NPS data and consolidate it for the creation of useful maps and tables.

Read more about project progress on the blog, [Good Morning Data](goodmorningdata.com).

## Usage

### Setup
1. Register for a NPS API key [here](https://www.nps.gov/subjects/developer/get-started.htm).
2. Run the script, nps_create_park_lookup.py to pull data from the NPS API and create the park lookup dataframe.
3. Run the script, nps_create_master_df.py to create the master parks dataframe which also includes visitation data and acreage data.

### Maps
1. Run the script, nps_create_maps.py to generate a clickable map of all sites in the National Parks system.
2. That previous map is a bit ugly with all those location markers, so specify the set of park sites you would like to see by running the script with the --parkset (-p) option: nps_create_maps.py -p 'National Park'. Use the -h command line argument to see all available park sets.

## Support
Contact [goodmorningdata@gmail.com](mailto:goodmorningdata@gmail.com)

## Roadmap
* Automate the download of the visitation data and acreage data and remove all hardcoded file references.
* Add logic to scrape founding date from Wikipedia.
* Create a bubble map to show park acreage.
* Create a bubble map to show park visitation.
