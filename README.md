# Zillow Home Values in US Cities Project
This project is to analyze Zillow home values in US cities from Jan 2000 to Jan 2023

To run the project locally, start with git clone https://github.com/AHijazi11/Zillow_Housing_Data_Project

Open terminal and run streamlit run app.py

Copy the local URL provided by streamlit in terminal and paste into a browser to display project

URL: http://localhost:10000/

My render URL: https://zillow-home-values.onrender.com

Note: city_geo_data_from_api.py is a script for obtaining city map polygon coordinates from "https://nominatim.openstreetmap.org" and outputs the results as a JSON. This was used to get the geo data for top 100 largest cities in the US, results of which are in city_dict.json.