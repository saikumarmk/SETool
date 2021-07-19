from bs4 import BeautifulSoup
import numpy as np
import pickle
import pandas as pd
import os
'''
This is the file that extracts the statistics from SETU data (not provided). You may run this script by uncommenting the gen_database functions.
The process to extract all SETU information can take a few minutes, so be patient! After this, they are serialized for convenient use later down the line.
Credits to Jake Vandenberg for the original script.
'''


def gen_database(filename: str, save_filename: str, season: str) -> dict:
    ''' 
    Creates a dictionary of units with their statistics.

    :param filename: str filepath to read from.
    :param save_filename: str filepath to write to.
    :param sem: adds the semester and year in which the unit was done. e.g 2020_S1
    :output: dictionary.

    '''
    
    with open(filename, "r") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, "lxml")

    database = {}

    for article in soup.find_all("article"):
        # invited number first
        base = article.find(
            "div", attrs={"class": "CrossCategoryBlockRow TableContainer"}).find("tbody")
        
        invited = int(
            base
            .find("tr", attrs={'class': 'CondensedTabularOddRows'})
            .find('td')
            .text)
        
        responded = int(
            base
            .find("tr", attrs={'class': 'CondensedTabularEvenRows'})
            .find('td')
            .text)

        if responded <= 1: continue

        entry = {}
        entry["Responses"] = responded
        entry["Invited"] = invited
        entry["Season"] = season
        entry['Response Rate'] = responded/invited*100

        # Full unit code
        code = article.find("table").find_all("tr")[3].text

        # Filter out MALAYSIA, COMPOSITE, ALFRED, SAFRICA
        if any(location in code for location in ["MALAYSIA","ALFRED","SAFRICA","FLEXIBLE"]):
            continue

        entry["code"] = code
        entry["unit_code"] = code.split("_")[0][1:]
        # Do not display on datatable, used only for queries
        try:
            entry["Level"] = int(entry["unit_code"][3]) 
        except ValueError: 
            entry["Level"] = 0
        scores = []
        # Response categories, retrieve all tables
        for item_num,divs in enumerate(
            article.find_all("div", attrs={"class": "FrequencyBlock_HalfMain"})):

            score_table = divs.find_all("table")[1].tbody.find_all("tr") # Split by stats and chart

            # Extract the means and medians from their td element
            mean, median = list(
                map(lambda x: x.find("td").text,
                    score_table
                )
            )[1:3]

            # Attempt conversion, not sure if this activates...?
            try:
                mean, median = float(mean), float(median)
                entry[f'I{item_num+1}'] = [mean,median]
                scores.append([mean,median])
            except ValueError:
                print(f"score could not be converted: {code}, {mean}, {median}")

        entry['agg_score'] = [sum(map(
            lambda item:item[measure],scores))/len(scores)
            for measure in range(2)
            ]

        database[code] = entry
        # Serialize after each point
        '''
        with open(save_filename, "wb") as f:
            pickle.dump(database, f, pickle.HIGHEST_PROTOCOL)
        '''

    df = pd.DataFrame(database).T.fillna(0)
    with open(save_filename, "wb") as f:
        pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)        
    return df



if __name__ == '__main__':
    # Open script from base directory
    base = 'conversion'
    reports = ['2019_S2','2020_S1','2020_S2','2021_S1']
    db = pd.concat([gen_database(f'{base}//{report}_SETU.html', f"setudb_{report}.pkl", report) for report in reports]).reset_index(drop=True)

    with open('setudb_total.pkl','wb') as file:
        pickle.dump(db, file, pickle.HIGHEST_PROTOCOL)
    print(db)