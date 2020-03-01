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

url = 'https://minibardelivery.com/api/v2/supplier/86,96,170,193,210,229,261,296,327,378,382,386,388,394,410,417,427,435,479,480,481,510,517,536,539,541,562,565,572,653,686,687,698,791,803,809,849/product_groupings?base=hierarchy_category&hierarchy_category=beer&sort=popularity&sort_direction=desc&facet_list[]=selected_supplier&facet_list[]=hierarchy_category&facet_list[]=hierarchy_type&facet_list[]=hierarchy_subtype&facet_list[]=country&facet_list[]=volume&facet_list[]=container_type&facet_list[]=delivery_type&facet_list[]=price&address_id=&coords[latitude]=40.69202170000001&coords[longitude]=-73.9847946&address[address1]=100 Willoughby Street&address[city]=Brooklyn&address[state]=NY&address[zip_code]=11201&per_page=20&shipping_state=NY&page='
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