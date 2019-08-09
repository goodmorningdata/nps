'''
This script creates...

The following visualizations are created:
1)
2) Plots including:
   Plot #1 -

Required Libraries
------------------

Dependencies
------------
1) Run the script, nps_create_master_df.py to create the file,
   nps_parks_master_df.xlsx.
'''

from nps_shared import *
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--parkcode', type=str,
        help = "Four character park code of park for which to display \
                park data. Example values are: 'YELL', 'CUVA', 'SHEN', \
                etc.")
    args = parser.parse_args()

    if not(args.parkcode):
        print("\n** Warning ** ")
        print('Please enter a park code parameter to display park data.\n')
        sys.exit()

    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)
    pd.set_option('display.max_columns', None)

    park = df[df.park_code == args.parkcode.lower()]
    num_stars = len(park.park_name.values[0])
    stars = '*' * (28 + num_stars)
    print('\n' + stars)
    print('Parkcode:                   {}'.format(args.parkcode))
    print('Park Name:                  {}'.format(park.park_name.values[0]))
    print('Designation:                {}'.format(park.designation.values[0]))
    print('States:                     {}'.format(park.states.values[0]))
    print('Entry Date:                 {}'.format(park.entry_date.values[0]))
    print('Size (acres):               {:,.2f}'
          .format(park.gross_area_acres.values[0]))
    print('Size (square miles):        {:.2f}'
          .format(park.gross_area_square_miles.values[0]))
    print('Number of visits in 2018: {}'
          .format(park[2018].values[0]))
    print(stars + '\n')

    # Fix date formatting
    # Add place for size and number of visits

if __name__ == '__main__':
    main()
