import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

def load_data():
    data = pd.read_csv("data.csv")
    return data


chart_data = load_data()

st.dataframe(chart_data)
st.map(chart_data,
       latitude="lat",
       longitude="lon",
       size="population")

