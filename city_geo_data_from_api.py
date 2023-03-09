import pandas as pd
import requests
import json

city_dict = {"type": "FeatureCollection", "features": []}


def get_city_polygon(row):
    global city_dict
    print(row['RegionName'], row['State'])
    params = {'city': row['RegionName'], 'state': row['State'],
              'format': "geojson", 'polygon_geojson': 1}
    res = requests.get(
        "https://nominatim.openstreetmap.org/search?", params=params)
    dict_1 = res.json()
    try:
        dict_1['features'][0]['properties']['price'] = row['2023-01-31']/10
        return city_dict['features'].append(dict_1['features'][0])
    except:
        print("No data available")


df_zillow = pd.read_csv(
    './cleaned_df_zillow.csv')

df_zillow.iloc[:100, :].apply(get_city_polygon, axis=1)

file_name = 'city_dict_top500_2.json'

with open(file_name, 'w') as f:
    json.dump(city_dict, f)
