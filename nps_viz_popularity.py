'''
'''

from nps_shared import *
import matplotlib.pyplot as plt

def plot_park_popularity(df, designation):
    increase_years = 5
    df['visitors_per_acre'] = df[2018]/df.gross_area_acres
    df['pct_increase'] = (
        (df[2018] - df[2018-increase_years])/df[2018-increase_years]*100)

    df = df[df.park_name != 'Gateway Arch National Park']

    df['park_name_label'] = df.park_name.replace(
        {'National Park':'NP'}, regex=True)

    print(df[['park_name', 'visitors_per_acre', 'pct_increase']])

    fig, ax = plt.subplots(figsize=(10,7))
    plt.scatter(df.visitors_per_acre, df.pct_increase)
    #plt.xscale('log')
    plt.xlabel("Visitors per acre in 2018")
    plt.ylabel("Visitor % increase, {} to 2018".format(2018-increase_years))
    for i, txt in enumerate(df.park_name_label):
        #print(i, txt)
        #print(type(df.visitors_per_acre))
        #print(df.visitors_per_acre.iloc[i])
        #print(df.pct_increase.iloc[i])
        plt.annotate(txt, (df.visitors_per_acre.iloc[i], df.pct_increase.iloc[i]), fontsize=8)
    plt.show()

# Plot visitors per acre vs. growth rate over past 10 years.
def main():
    df_park, designation = get_parks_df(warning=['visitor', 'size'])

    df_park = (df_park[~df_park[2018].isnull()])
    df_park = (df_park[~df_park.gross_area_acres.isnull()])

    # Plot #1
    plot_park_popularity(df_park, designation)

if __name__ == '__main__':
    main()
