import streamlit as st
import pandas as pd
import datetime as dt
import calendar
from plotly import express as px
import pydeck as pdk
import json
from zipfile import ZipFile

def find_centroid_v4(geometry):
    def find_centroid_single_ring(ring):
        x = [coord[0] for coord in ring]
        y = [coord[1] for coord in ring]
        length = len(ring)
        centroid_x = sum(x) / length
        centroid_y = sum(y) / length
        return [centroid_x, centroid_y]

    if geometry["type"] == "Polygon":
        centroids = [find_centroid_single_ring(ring) for ring in geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        centroids = [find_centroid_single_ring(ring) for polygon in geometry["coordinates"] for ring in polygon]
    elif geometry["type"] == "Point":
        return geometry["coordinates"]
    else:
        raise ValueError(f"Unsupported geometry type: {geometry['type']}")
    
    centroid_x = sum(centroid[0] for centroid in centroids) / len(centroids)
    centroid_y = sum(centroid[1] for centroid in centroids) / len(centroids)
    return [centroid_x, centroid_y]

# define the input file name
file_name = 'city_dict.json'

# read the dictionary from a JSON file
with open(file_name, 'r') as f:
    # Placeholder dict for city geo polygon & price
    city_dict = json.load(f)

simplified_city_dict = {"type": "FeatureCollection", "features": []}

for feature in city_dict["features"]:
    # Create a new feature dictionary
    new_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            # We use the centroid (center point) of the polygon as the point coordinates
            "coordinates": find_centroid_v4(feature["geometry"])
        },
        "properties": {
            "name": feature["properties"]["display_name"]
        }
    }
    # Add this feature to the new city_dict
    simplified_city_dict["features"].append(new_feature)

# Print the first feature to check
simplified_city_dict["features"][0]

file_name = 'simplified_city_dict.json'

with open(file_name, 'w') as f:
    json.dump(simplified_city_dict, f)