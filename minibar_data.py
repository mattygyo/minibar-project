# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
import pandas as pd 
import numpy as np
import time
from bs4 import BeautifulSoup

def get_token():
    url = 'https://minibardelivery.com'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    bearer_token = soup.findAll(attrs={"name":"access-token"})[0]['content']
    return bearer_token

url = '<minibar XHR url goes here>'
bearer_token = get_token()
header = {'Authorization': 'bearer {}'.format(bearer_token)}
item_count = round(requests.get(url+str(1), headers=header).json()['count']/20)

def alc_pct(x):
    if x is None:
        x = np.nan
    else:
        x = x['value']
    return x

beer_df = pd.DataFrame([])
for x in range(1,item_count+1):   
    time.sleep(3)
    data = requests.get(url+str(x), headers=header).json()
    for i in range(0, len(data['product_groupings'])):
        core_data = {key: data['product_groupings'][i][key] for key in data['product_groupings'][0].keys() & {'name','type','brand'}} 
        core_data['hierarchy_type'] = data['product_groupings'][i]['hierarchy_type']['name']
        core_data['hierarchy_subtype'] = data['product_groupings'][i]['hierarchy_subtype']['name']
        core_data['alcohol_pct'] = alc_pct(next((item for item in data['product_groupings'][i]['properties'] if item["name"] == "Alcohol %"), None))
        variant_df = pd.DataFrame([])
        for v in range(0, len(data['product_groupings'][i]['variants'])):
            variant_data = {key: data['product_groupings'][i]['variants'][v][key] for key in data['product_groupings'][i]['variants'][v].keys() 
                            & {'price','short_pack_size','short_volume','container_type','supplier_id'}}
            core_data.update(variant_data)
            variant_df = variant_df.append(core_data, ignore_index=True)
        beer_df = beer_df.append(variant_df)

beer_df.to_csv('beer_data.csv')



import missingno as msno
msno.matrix(beer_df, figsize=(12, 5))
