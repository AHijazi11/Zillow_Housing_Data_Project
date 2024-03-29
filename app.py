import streamlit as st
import pandas as pd
import datetime as dt
import calendar
from plotly import express as px
import pydeck as pdk
import json
from zipfile import ZipFile
import numpy as np
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(layout="wide")

@st.cache_resource
def load_data():
    # loading the temp.zip and creating a zip object
    with ZipFile('./City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.zip', 'r') as zObject:
        # Extracting all the members of the zip
        # into a specific location.
        zObject.extractall(path='./')

    df_zillow = pd.read_csv('./City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')

    # change home values from float to int & fill NA with 0
    df_zillow.iloc[:, 8:] = df_zillow.iloc[:, 8:].fillna(0).astype(int)

    # drop excess columns:
    df_zillow.drop(['RegionID', 'StateName', 'RegionType',
                'Metro', 'CountyName'], axis=1, inplace=True)

    # rename RegionName to City
    df_zillow.rename(columns={'RegionName': 'City'}, inplace=True)

    # create new df for the top 100 largest cities
    df_largerst_100_cities = df_zillow.iloc[:100, :]

    return df_zillow, df_largerst_100_cities

df_zillow, df_largerst_100_cities = load_data()

st.header('USA Monthly Housing Data from 2000 to 2023')

# slider to select date ranges of data to be displayed
selected_date_range = st.slider(
    "Date Range: From M/YYYY to M/YYYY",
    value=[dt.date(2000, 1, 31), dt.date(2023, 1, 31)],
    format="M/YYYY")

def get_last_day_in_month(any_date):
    # use calendar module to get last day of month of any_date
    last_day = calendar.monthrange(any_date.year, any_date.month)[1]
    # use datetime.date() to get date as a string of
    last_day_date = dt.date(
        any_date.year, any_date.month, last_day).strftime("%Y-%m-%d")
    return last_day_date

columns_to_show = list(df_zillow.loc[:, ['City', 'State']])

date_range_columns = list(df_zillow.loc[:, get_last_day_in_month(selected_date_range[0]):get_last_day_in_month(
    selected_date_range[1])])

columns_to_show.extend(date_range_columns)

hide_selected_dataframe = st.checkbox(
    'Hide dataframe')
if not hide_selected_dataframe:
    st.write(df_zillow[columns_to_show])

# ... Continue the rest of your code ...
# slider to select data (M/YYYY)
selected_date = st.slider(
    "Date: M/YYYY",
    min_value=dt.date(2000, 1, 31),
    max_value=dt.date(2023, 1, 31),
    value=dt.date(2020, 3, 1),
    format="M/YYYY")

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

st.subheader('Map of Monthly Median Home Values for 100 Largest Cities in US')

# date slider for pydeck chart
selected_date_pydeck = st.slider(
    "M/YYYY",
    label_visibility='hidden',
    min_value=dt.date(2000, 1, 31),
    max_value=dt.date(2023, 1, 31),
    value=dt.date(2020, 3, 1),
    format="M/YYYY")

# Load the city data
with open('simplified_city_dict.json', 'r') as f:
    city_data = json.load(f)

def set_property_price(row):
    '''
    function to set property price value in ['properties']['price']:
    '''
    city_data['features'][row['SizeRank']
                          ]['properties']['price'] = row[get_last_day_in_month(selected_date_pydeck)]

df_largerst_100_cities.apply(set_property_price, axis=1)

def linear_color_scale(val, min_val, max_val):
    """Create a linear color scale"""
    norm = plt.Normalize(min_val, max_val)
    cmap = plt.get_cmap("YlOrRd")
    rgba_color = cmap(norm(val))
    # Convert the color from range 0-1 to 0-255
    return [int(x*255) for x in rgba_color[:3]]


# Find the min and max price
min_price = min(feature['properties']['price'] for feature in city_data['features'])
max_price = max(feature['properties']['price'] for feature in city_data['features'])

# Add the 'color' property to the city_data
for feature in city_data['features']:
    feature['properties']['color'] = linear_color_scale(feature['properties']['price'], min_price, max_price)

layer = pdk.Layer(
    'ColumnLayer',
    city_data['features'],
    get_position='geometry.coordinates',
    get_elevation='properties.price / 100',
    elevation_scale=50,
    radius=5000,
    get_fill_color='properties.color',
    pickable=True,
    auto_highlight=True,
)

# Set initial view state
initial_view_state = pdk.ViewState(
    latitude=30,
    longitude=-100,
    zoom=4,
    max_zoom=8,
    pitch=55,
    bearing=10
)

chart = pdk.Deck(layers=[layer], initial_view_state=initial_view_state)
st.pydeck_chart(chart)
