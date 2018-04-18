outfile = 'upload/support_scores.csv'

print("Loading ABS Data files. May take a few minutes")

import pandas as pd
pd.options.mode.chained_assignment = None
sa1filename = 'data/2011Census_B19_AUST_SA1_short.csv'
sa2filename = 'data/2011Census_B19_AUST_SA2_short.csv'
postcoderfilename = 'data/'
import scipy.stats as stats
from gender_detector.gender_detector import GenderDetector
gender =  GenderDetector('uk')
from geopy import geocoders
g = geocoders.Bing('AkDshUctFFg0jtgXvUYsHanWN3b6qedpS0Ax2oLG-e_yC0Q8AHAai-b9kg1sqX50')
postcodefile = 'data/2011PostcodetoSA2.csv'
postcodes = pd.DataFrame.from_csv(postcodefile, parse_dates=False, infer_datetime_format=False)
import datetime
from dateutil import parser as dateparser
now = datetime.datetime.today()

try:
    df = pd.DataFrame.from_csv(sa1filename, parse_dates=False, infer_datetime_format=False)
    df = df.append(pd.DataFrame.from_csv(sa2filename, parse_dates=False, infer_datetime_format=False))
    df['P_Tot_Volunteer_percent'] = df['P_Tot_Volunteer'] / df['P_Tot_Tot']
    #df.apply(lambda row: row['P_Tot_Volunteer'] / float(row['P_Tot_Tot']),axis=1)
    df.P_Tot_Volunteer_percent[df.P_Tot_Volunteer_percent >0.95] = None
except Exception as e:
    print(("Couldn't find " +str(sa1filename) +" in this folder, or the file was corrupt"))
    print (e)


print("Done loading ABS Data files.")


def postcode_to_sa2(postcode):
    bestcode = postcodes[postcodes['POSTCODE'] == postcode]['RATIO'].idxmax()
    return postcodes.iloc[bestcode]['SA2_MAINCODE_2011']

def getgender(firstname):
    guess = gender.guess(firstname)
    if guess == 'female':
        return 'F'
    elif guess == 'male':
        return 'M'
    else:
        return 'P'

def getvolunteerscore(supporter):
    '''Given an age, gender and SA1, return a volunteer score, based on the ABS census data
    TODO one day
    Weight based on the fact that not all SA1s are the same size and thus have different confidence intervals. '''
    if  pd.isnull(supporter['sex']):
        try:
            supporter['sex'] = getgender(supporter['first_name'])
        except:
            supporter['sex'] = 'P'

    if not pd.isnull(supporter['born_at']):
        supporter['Age'] = now.year - dateparser.parse(supporter['born_at']).year
        if supporter['Age'] < 15:
            agerange='15_19_yr'
        if 15 <= supporter['Age'] <= 19:
            agerange='15_19_yr'
        if 20 <= supporter['Age'] <= 24:
            agerange='20_24_yr'
        if 25 <= supporter['Age'] <= 34:
            agerange='25_34_yr'
        if 35 <= supporter['Age'] <= 44:
            agerange='35_44_yr'
        if 45 <= supporter['Age'] <= 54:
            agerange='45_54_yr'
        if 55 <= supporter['Age'] <= 64:
            agerange='55_64_yr'
        if 65 <= supporter['Age'] <= 74:
            agerange='65_74_yr'
        if 75 <= supporter['Age'] <= 84:
            agerange='75_84_yr'
        if supporter['Age'] > 84:
            agerange='85ov'
        if not agerange:
            agerange='Tot'
        supporter['agerange'] = agerange
    else:
        supporter['agerange'] = 'Tot'
    volunteerbucket = "{sex}_{agerange}".format(**supporter)
    isvol = volunteerbucket +"_Volunteer"
    notvol = volunteerbucket +"_N_a_volunteer"
    allinbucket = volunteerbucket +"_Tot"
    try:
        volunteerscore = float(df.loc[int(supporter['region'])][isvol]) / float(df.loc[int(supporter['region'])][allinbucket])
        supportlevel = int(stats.percentileofscore(df['P_Tot_Volunteer_percent'],volunteerscore,kind='weak') / 100 * 5) + 1
    except Exception as e:
        print (e)
        return 0
    return supportlevel

def makescores(inputfilename):
    supporters = pd.DataFrame.from_csv(inputfilename, parse_dates=False, infer_datetime_format=False)
    allsupporters = supporters.iterrows()
    scores = list()
    for index,supporter in allsupporters:
        data = dict()
        if not pd.isnull(supporter['primary_address1']):
            try:
                address = "{primary_address2} {primary_address1} {primary_city} {primary_state} Australia".format(**supporter)
                result = g.geocode(address)
                if result:
                    supporter['lat'] = result[1][0]
                    supporter['lon'] = result[1][1]
                    from coord_to_census import coord_to_census
                    location = coord_to_census(supporter['lat'],supporter['lon'])
                    supporter['sa1'] = int(location[1])
            except:
                print("Problem geocoding this address")
                supporter['sa2'] = postcode_to_sa2(supporter['primary_zip'])
        else:
            if not pd.isnull(supporter['primary_zip']):
                supporter['sa2'] = postcode_to_sa2(supporter['primary_zip'])
        if 'sa1' in supporter:
            supporter['region'] = supporter['sa1']
            data['sa1'] = supporter['sa1']
        else:
            if 'sa2' in supporter:
                supporter['region'] = supporter['sa2']
                data['sa2'] = supporter['sa2']
            else:
                supporter['region'] = None
        data['inferred_support_level'] = getvolunteerscore(supporter)
        data['nationbuilder_id'] = index
        data['sex'] = supporter['sex']
        scores.append(data)
    return scores

def makecsv(scores):
    from random import randrange
    export = pd.DataFrame.from_records(scores)
    filename = randrange(1000000,9000000)
    shortname ="{filename}.csv".format(**locals())
    outfile = "upload/{filename}.csv".format(**locals())
    result = export.to_csv(outfile,columns=["nationbuilder_id", "inferred_support_level", "sa1","sa2","sex"],index=False)
    return shortname

#print("Processing Nationbuilder Export")
#scores = makescores('upload/nb_export.csv')
#csvname = makecsv(scores)
#print("All done. " + str(csvname) + " created.")
