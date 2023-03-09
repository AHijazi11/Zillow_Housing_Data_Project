# Zillow_Housing_Data_Project
This project is to analyze Zillow housing value data from 1/31/2000 to 1/31/2023

To run the project locally, start with git clone https://github.com/AHijazi11/Zillow_Housing_Data_Project

Open terminal and run streamlit run app.py

Copy the local URL provided by streamlit in terminal and paste into a browser to display project

URL: http://localhost:10000/

My render URL:

Note: city_geo_data_from_api.py is a script for obtaining city map polygon coordinates from "https://nominatim.openstreetmap.org" and outputs the results as a JSON to be used in pydeck chart. This was used to get the geo data for top 100 largest cities in the US, results of which are in city_dict.json. It's not necessary to run for the streamlit app to function.