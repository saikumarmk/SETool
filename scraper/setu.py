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


def gen_database(filename, save_filename, sem):
    '''
    Generates a CSV of SETU data from raw HTML data.    


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
            base.find("tr", attrs={'class': 'CondensedTabularOddRows'}).find('td').text)
        responded = int(
            base.find("tr", attrs={'class': 'CondensedTabularEvenRows'}).find('td').text)

        if responded <= 1:
            continue

        entry = {}
        entry["Responses"] = responded
        entry["Invited"] = invited
        entry["Semester"] = sem

        # Full code
        code = article.find("table").find_all("tr")[3].text

        # Temporary for now, can be added back in with demand
        if "MALAYSIA" in code or "ALFRED" in code or "SAFRICA" in code:
            continue

        unit_code = code.split("_")[0]
        entry["code"] = code
        entry["unit_code"] = unit_code
        try:
            entry["Level"] = int(entry["unit_code"][4])
        except ValueError: # Strange honors project exception
            entry["Level"] = 0
        scores = []
        # Response categories
        for divs in article.find_all("div", attrs={"class": "FrequencyBlock_HalfMain"}):

            tables = divs.find_all("table")
            score = tables[1].tbody.find_all("tr")[1].find("td").text
            try:
                score = float(score)
                scores.append(score)
            except Exception:
                print("score could not be converted: {}, {}".format(code, score))

        entry["scores"] = np.array(scores)
        database[code] = entry
        # Serialize
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


def to_dataframe(db):
    '''
    Converts the input dict to a dataframe. 

    '''
    db = deepcopy(db)
    for key in db:
        for j in range(8):
            db[key]["I" + str(j+1)] = db[key]["scores"][j]
    df = pd.DataFrame(db)
    df = df.T
    df = df.drop(["scores", ], axis=1)
    df["unit_code"] = df["unit_code"].apply(lambda x: x[1:])
    df['mean_score'] = (sum(df['I{}'.format(i)] for i in range(1, 9)))/8
    df["school"] = df["unit_code"].str[0:3]
    df["Response Rate"] = df['Responses']/df['Invited']*100

    df = df.reindex(columns=["code", "unit_code", "school", "Level", "Semester"]+[
                    f'I{i}' for i in range(1, 9)]+["mean_score", "Invited", "Responses", "Response Rate"])
    return df


if __name__ == '__main__':
    '''
    gen_database("2020_S2_SETU.html", "setudb_2020_S2.pkl", "S2")
    print("Done S2 2020")
    gen_database("SETU.html", "setudb_2020_S1.pkl", "S1")
    print("Done S1 2020") #'SETU_2020_S1' 'SETU_2020_S2'
    '''
    setu_s1 = to_dataframe(load_database('setudb_2020_S1.pkl'))
    setu_s2 = to_dataframe(load_database('setudb_2020_S2.pkl'))
    pd.concat([setu_s1, setu_s2]).reset_index(
        drop=True).to_csv("SETU_2020_All.csv")
