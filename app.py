import streamlit as st
import pandas as pd
import datetime as dt
import calendar
from plotly import express as px
import pydeck as pdk
import json

df_zillow = pd.read_csv(
    './City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')

# change home values from float to int & fill NA with 0
df_zillow.iloc[:, 8:] = df_zillow.iloc[:, 8:].fillna(0).astype(int)

# drop excess columns:
df_zillow.drop(['RegionID', 'StateName', 'RegionType',
               'Metro', 'CountyName'], axis=1, inplace=True)

# rename RegionName to City
df_zillow.rename(columns={'RegionName': 'City'}, inplace=True)

st.header('USA Housing Data from 2000 to 2023')

# slider to select data (M/YYYY)
selected_date = st.slider(
    "Date: M/YYYY",
    min_value=dt.date(2000, 1, 31),
    max_value=dt.date(2023, 1, 31),
    value=dt.date(2020, 3, 1),
    format="M/YYYY")


def get_last_day_in_month(any_date):
    # use calendar module to get last day of month of any_date
    last_day = calendar.monthrange(any_date.year, any_date.month)[1]
    # use datetime.date() to get date as a string of
    last_day_date = dt.date(
        any_date.year, any_date.month, last_day).strftime("%Y-%m-%d")
    return last_day_date


hide_selected_dataframe = st.checkbox(
    'Hide dataframe')
if not hide_selected_dataframe:
    st.write(df_zillow[['SizeRank', 'City', 'State',
             get_last_day_in_month(selected_date)]])

# variable df based on selected date to be used in scatter plot
df_state_last_day_date = df_zillow.groupby('State').agg(
    {get_last_day_in_month(selected_date): 'median'}).reset_index()

# scatter plot
st.write(px.scatter(df_state_last_day_date, y=get_last_day_in_month(selected_date), x='State',
                    title=f"Median Home Value by State for {get_last_day_in_month(selected_date)}", labels={get_last_day_in_month(selected_date): 'Home Value in $'}))

# create new df for the top 100 largest cities
df_largerst_100_cities = df_zillow.iloc[:100, :]

color_toggle = st.checkbox('Color bars by state')
if color_toggle:
    # histogram colored by state
    fig = px.histogram(df_largerst_100_cities, x='City', y=get_last_day_in_month(
        selected_date), color='State', title=f"Median Home Value: 100 Largest US Cities for {get_last_day_in_month(selected_date)}", labels={get_last_day_in_month(selected_date): 'Home Value in $'})
    fig.for_each_trace(lambda t: t.update(
        hovertemplate=t.hovertemplate.replace("sum of", "")))
    fig.for_each_yaxis(lambda a: a.update(
        title_text=a.title.text.replace("sum of", "")))
    st.write(fig)
else:
    # histogram without coloring bars by state
    fig = px.histogram(df_largerst_100_cities, x='City', y=get_last_day_in_month(
        selected_date), title=f"Median Home Value: 100 Largest US Cities for {get_last_day_in_month(selected_date)}", labels={get_last_day_in_month(
            selected_date): 'Home Value in $'})
    fig.for_each_trace(lambda t: t.update(
        hovertemplate=t.hovertemplate.replace("sum of", "")))
    fig.for_each_yaxis(lambda a: a.update(
        title_text=a.title.text.replace("sum of", "")))
    st.write(fig)

st.subheader('Map of Median Home Values for 100 Largest Cities in US')

# date slider for pydeck chart
selected_date_pydeck = st.slider(
    "M/YYYY",
    label_visibility='hidden',
    min_value=dt.date(2000, 1, 31),
    max_value=dt.date(2023, 1, 31),
    value=dt.date(2020, 3, 1),
    format="M/YYYY")

# define the input file name
file_name = 'city_dict.json'

# read the dictionary from a JSON file
with open(file_name, 'r') as f:
    # Placeholder dict for city geo polygon & price
    city_dict = json.load(f)


def set_property_price(row):
    '''
    function to set property price value in ['properties']['price']:
    '''
    city_dict['features'][row['SizeRank']
                          ]['properties']['price'] = row[get_last_day_in_month(selected_date_pydeck)]


df_largerst_100_cities.apply(set_property_price, axis=1)

INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=38.252740,
    longitude=-100.473460,
    zoom=3.25,
    max_zoom=8,
    pitch=80,
    bearing=10
)

geojson = pdk.Layer(
    'GeoJsonLayer',
    city_dict,
    opacity=0.1,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=False,
    get_elevation='properties.price',
    get_fill_color='[255, 0, 255]',
    get_line_color=[255, 255, 255],
    pickable=True
)

st.pydeck_chart(pdk.Deck(
    layers=[geojson],
    initial_view_state=INITIAL_VIEW_STATE)
)
