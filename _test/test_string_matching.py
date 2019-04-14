from Levenshtein import distance
from difflib import SequenceMatcher
import pandas as pd

def process_match(s):
    s = (s.replace('National Historical Park and Ecological Preserve','')
          .replace('National Park & Preserve','').replace('National Historic','')
          .replace('National Memorial','').replace('National Heritage','')
          .replace('National Monument','').replace('National Heritage Corridor','')
          .replace('National Historical','').replace('National Parks','')
          .replace('National Park','')
          .replace('National Battlefield','').replace('National Recreation Area','')
          .replace('National Preserve','').replace('National Military Park','')
          .replace('National Seashore','').replace('National Lakeshore','')
          .replace('National Scenic Riverway','')
          .replace('National Scenic River','')
          .replace('National and State Parks','')
          .replace('National Wild and Scenic River','')
          .replace('Scenic & Recreational River','')
          .replace('National River and Recreation Area','')
          .replace('Ecological & Historic Preserve','')
          .replace('Recreation Area','')
          .replace('National Scenic','')
          .replace('Site','').replace('Park','').replace('Area',''))
    return s

def process_to_match(s):
    to_match_stripped = s
    # to_match_stripped = (s.replace('NBP','').replace('NHP','').replace('NHS','')
    #                       .replace('NMEM','').replace('NMP','').replace('NRA','')
    #                       .replace('NSR','').replace('NST','').replace('NB','')
    #                       .replace('NL','').replace('NM','').replace('NP','')
    #                       .replace('NS','').replace('NB','').replace('N PRESERVE','')
    #                       .replace('NMP','').replace('NATIONAL PRESERVE','')
    #                       .replace('N. SCENIC RIVER','')
    #                       .replace('NATIONAL MEMORIAL','')
    #                       .replace('FDR','Franklin Delano Roosevelt')
    #                       .replace('T ROOSEVELT','Theodore Roosevelt')
    #                       .replace('FRED-SPOTS','FREDERICKSBURG-SPOTSYLVANIA')
    #                       .replace('WWII','World War II')
    #                       .replace('DELAWARE NSR','LOWER DELAWARE')
    #                       .replace('KINGS CANYON','SEQUOIA & KINGS CANYON'))
    return to_match_stripped

def find_match(s):
    to_match_stripped = process_to_match(s)
    type = 'D'
    if type=='L':
        df['name_match'] = df['park_name_stripped'].apply(lambda x: distance(x.lower(), to_match_stripped.lower()))
    else:
        df['name_match'] = df['park_name_stripped'].apply(
                           lambda x: SequenceMatcher(None, x.lower(),
                           to_match_stripped.lower()).ratio())

    print('Matching: ',s)
    print('Matching (stripped): ', to_match_stripped)
    print(df.loc[df['name_match'].idxmax()].park_code)
    print(df.loc[df['name_match'].idxmax()].park_name)

def test_match(s, correct, incorrect):
    to_match = process_to_match(s)
    print('To match stripped: ',to_match)
    correct_match = process_match(correct)
    print('Correct match stripped: ',correct_match)
    incorrect_match = process_match(incorrect)
    print('Incorrect match stripped', incorrect_match)
    correct_match = SequenceMatcher(None, correct_match.lower(), to_match.lower()).ratio()
    incorrect_match = SequenceMatcher(None, incorrect_match.lower(), to_match.lower()).ratio()

    print('** To Match: ', s)
    print('** Correct Match: ', correct, ' Correct Match Score: ', correct_match)
    print('** Incorrect Match: ', incorrect, ' Incorrect Match Score: ', incorrect_match)

df_parks = pd.read_excel('park_lookup.xlsx', header=0)
df = df_parks[['park_name', 'park_code']]
df['park_name_stripped'] = df['park_name'].apply(lambda x: process_match(x))

to_match = 'White House'
correct_match = "President's Park (White House)"
incorrect_match = 'White Sands National Monument'
find_match(to_match)
test_match(to_match, correct_match, incorrect_match)
