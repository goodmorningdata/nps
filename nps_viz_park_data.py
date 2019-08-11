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

def to_ord(i):
    i = str(i)
    if i[len(i) - 1] == '1':
        return i + 'st'
    elif i[len(i) - 1] == '2':
        return i + 'nd'
    elif i[len(i) - 1] == '3':
        return i + 'rd'
    else:
        return i + 'th'

def get_park_place(parkcode, designation, df, place_type):
    if place_type == 'size':
        sort_column = 'gross_area_acres'
    else:
        sort_column = 2018
    df = df.sort_values(by=sort_column, ascending=False).reset_index(drop=True)
    df_d = df[df.designation == designation].sort_values(by=sort_column, ascending=False).reset_index(drop=True)

    overall_place = to_ord(df.loc[df.park_code == parkcode].index.values[0])
    desig_place = to_ord(df_d.loc[df_d.park_code == parkcode].index.values[0])

    return overall_place, desig_place

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

    parkcode = args.parkcode

    df = pd.read_excel('nps_parks_master_df.xlsx', header=0)
    park = ((df.loc[df.park_code == parkcode.lower()]
           .reset_index(drop=True))
           .loc[0])

    overall_size_place, designation_size_place = (
        get_park_place(parkcode.lower(), park.designation, df, 'size'))

    overall_visit_place, designation_visit_place = (
        get_park_place(parkcode.lower(), park.designation, df, 'visit'))

    num_stars = len(park.park_name)
    stars = '*' * (78 + num_stars)
    print('\n' + stars)
    print('Parkcode:                   {}'.format(parkcode))
    print('Park Name:                  {}'.format(park.park_name))
    print('Designation:                {}'.format(park.designation))
    print('States:                     {}'.format(park.states))
    print('Entry Date:                 {}'.format(park.entry_date))
    print('Size (acres):               {:,.2f} -- {} place overall, {} place '
      'within {}.'.format(park.gross_area_acres, overall_size_place,
      designation_size_place, park.designation))
    print('Size (square miles):        {:.2f}'
          .format(park.gross_area_square_miles))
    print('Number of visits in 2018:   {:,.0f} -- {} place overall, {} place '
      'within {}.'.format(park[2018], overall_visit_place,
      designation_visit_place, park.designation))
    print(stars + '\n')

    # Fix date formatting

if __name__ == '__main__':
    main()
