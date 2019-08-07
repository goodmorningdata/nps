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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--parkcode', type=str,
        help = "Four character park code of park for which to display \
                park data. Example values are: 'YELL', 'CUVA', 'SHEN', \
                etc.")
    args = parser.parse_args()

    if args.parkcode:
        print('** Parkcode: {}'.format(args.parkcode))
    else:
        print("\n** Warning ** ")
        print('Please enter a park code parameter to display park data.\n')

if __name__ == '__main__':
    main()
