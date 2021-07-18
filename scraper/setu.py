from bs4 import BeautifulSoup
import numpy as np
import pickle
import pandas as pd
from copy import deepcopy
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

        # Full unit code
        code = article.find("table").find_all("tr")[3].text

        # Filter out MALAYSIA, COMPOSITE, ALFRED, SAFRICA
        if any(location in code for location in ["MALAYSIA","ALFRED","SAFRICA","FLEXIBLE"]):
            continue

        entry["code"] = code
        entry["unit_code"] = code.split("_")[0]
        # Do not display on datatable, used only for queries
        try:
            entry["Level"] = int(entry["unit_code"][4]) 
        except ValueError: 
            entry["Level"] = 0
        scores = []
        # Response categories, retrieve all tables
        for divs in article.find_all("div", attrs={"class": "FrequencyBlock_HalfMain"}):

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
                scores.append([mean,median])
            except ValueError:
                print(f"score could not be converted: {code}, {mean}, {median}")

        entry["scores"] = np.array(scores)
        database[code] = entry
        # Serialize after each point
        '''
        with open(save_filename, "wb") as f:
            pickle.dump(database, f, pickle.HIGHEST_PROTOCOL)
        '''
    with open(save_filename, "wb") as f:
        pickle.dump(database, f, pickle.HIGHEST_PROTOCOL)        
    return database


def load_database(filename):
    '''
    Deserializes pickled database files into a dict.
    load_database: str -> dict
    '''
    with open(filename, "rb") as f:
        database = pickle.load(f)
    return database


def to_dataframe(db:dict) -> pd.DataFrame:
    '''
    Converts the input dict to a dataframe. 

    :param db: Dictionary of unit statistics.
    :output: Dataframe of all units with their statistics.

    '''
    for unit_name in db:
        for item_index in range(len(db[unit_name]['scores'])):
            db[unit_name][f'I{item_index+1}'] = db[unit_name]["scores"][item_index]
    df = pd.DataFrame(db).T

    df["unit_code"] = df["unit_code"].apply(lambda x: x[1:])
    df['agg_score'] = df['scores'].apply(
        lambda entry: [sum(item[measure] for item in entry)/len(entry) for measure in range(2)]
    ) # Determine mean of all items over mean and median
    df = df.drop(["scores", ], axis=1)
    df["school"] = df["unit_code"].str[0:3]
    df["Response Rate"] = df['Responses']/df['Invited']*100

    df = df.reindex(columns=["code", "unit_code", "school", "Level", "Season"]+[
                    f'I{i}' for i in range(1, 14)]+["agg_score", "Invited", "Responses", "Response Rate"])
    return df


if __name__ == '__main__':
    '''
    gen_database("2020_S2_SETU.html", "setudb_2020_S2.pkl", "S2")
    print("Done S2 2020")
    gen_database("SETU.html", "setudb_2020_S1.pkl", "S1")
    print("Done S1 2020") #'SETU_2020_S1' 'SETU_2020_S2'
    
    setu_s1 = to_dataframe(load_database('setudb_2020_S1.pkl'))
    setu_s2 = to_dataframe(load_database('setudb_2020_S2.pkl'))
    pd.concat([setu_s1, setu_s2]).reset_index(
        drop=True).to_csv("SETU_2020_All.csv")
    '''
    db = gen_database("D://Programming//Python//data_analysis//2021_S1_SETU.htm", "setudb_2021_S1.pkl", "2021_S1")
    df = to_dataframe(db)
    df.to_csv("SETU_2021.csv")