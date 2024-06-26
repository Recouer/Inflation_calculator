import numpy as np
import pandas as pd
import re

items_number = 13

def get_inflation(table, start_time, end_time):
    inflation = 1.0
    for i in range(start_time+1, end_time):
        for j in range(4, 30):
            if table["Année"][j] == i:
                inflation *= 1 + table["Taux"][j] * 0.01
                continue
    return inflation

class DataHolder():
    def __init__(self) -> None:
        price_index = pd.read_excel("famille_IPC-2015_25062024.xlsx")
        consumption_type_2017 = pd.read_excel("TF106.xlsx")
        val = consumption_type_2017["TF106 : Dépenses annuelles moyennes par ménage en France selon le niveau de vie"]
        price_inflation = price_index["Libellé"]

        corr = {}
        price_dict = {}                             # consomation type | year
        consumption_dict: dict[str, dict] = {}      # consomation type | tencile 

        for i in range(len(price_inflation)):
            for j in range(1, items_number):
                stringy = "Indice des prix à la consommation - Base 2015 - Ensemble des ménages - France métropolitaine - Nomenclature Coicop " + (f": 0{j} -" if j<10 else f": {j} -")
                if isinstance(price_inflation[i], str):
                    if stringy in price_inflation[i]:
                        price_dict[j] = {}
                        for k in price_index.keys()[4:]:
                            price_dict[j][k] = price_index[k][i]

        for i in range(len(val)):
            for j in range(1, items_number):
                stringy = f"0{j} -" if j<10 else f"{j} -"
                if isinstance(val[i], str):
                    if re.match(stringy, val[i]) is not None:
                        corr[j] = val[i]
                        consumption_dict[j] = {}
                        for k in consumption_type_2017.keys()[2:]:
                            consumption_dict[j][k] = consumption_type_2017[k][i]
        self.corr = corr
        self.price_dict = price_dict
        self.consumption_dict = consumption_dict
        self.life_level_file = pd.read_excel("reve-niv-vie-decile.xlsx")
        self.inflation_rate = pd.read_excel("econ-gen-taux-inflation.xlsx")

    def get_data(self):
        start = 2001
        end = 2017
        
        for i in range(3, 14):
            old = self.life_level_file[start][i]
            new = self.life_level_file[end][i]
            print(new / old * (1 / get_inflation(self.inflation_rate, start, end)))
            print(get_inflation(self.inflation_rate, start, end))
        

    def inflation_by_tencile(self, tencile, old, new):
        sum = 0
        for _type in self.consumption_dict.items():
            sum += _type[1][f"Décile {tencile}"]
        
        inflation = 0
        for (_type, prices) in self.price_dict.items():
            old_price = prices[f"{old}-01"]
            new_price = prices[f"{new}-01"]
            
            inflation += (self.consumption_dict[_type][f"Décile {tencile}"] / sum) * (new_price / old_price)
        print(tencile, inflation)


if __name__ == "__main__":
    dh = DataHolder()
    dh.get_data()
    for i in range(1, 11):
        dh.inflation_by_tencile(i, 2001, 2021)