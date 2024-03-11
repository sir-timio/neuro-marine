import streamlit as st
import cv2
from model import Processor
import json
import os
from pathlib import Path
import logging
import pandas as pd
from fpdf import FPDF
import base64
from sklearn.preprocessing import MinMaxScaler

scaler_min = MinMaxScaler(feature_range=(27.32, 36.23))
scaler_mean = MinMaxScaler(feature_range=(58.21, 82.35))
scaler_max = MinMaxScaler(feature_range=(87.12, 93.52))

logging.basicConfig(filename="stream.log", encoding='utf-8')

if "data_download" not in st.session_state:
    st.session_state["data_download"] = True

if "data_process" not in st.session_state:
    st.session_state["data_process"] = True

if "report" not in st.session_state:
    st.session_state["report"] = True

@st.cache_resource
def load_processor():
    processor = Processor()
    return processor

def process_flag():     
    st.session_state['data_process'] = False

processor = load_processor()
time_plot = processor.time_plot
size_plot = processor.size_plot
red_plot = processor.red_plot

uploaded_video = st.file_uploader("Choose video", 
                                  type=["mp4", "webm", "mov", "png", "jpg", "jpeg"],
                                   on_change=process_flag,
)


frame_skip = 1# display every 300 frames

def process_data():
    global processor
    file_name = st.session_state['vid'] 

    with st.spinner('Обрабатываем данные... :clock1:'):
        out = processor.process(file_name)
        time_plot = processor.time_plot
        logging.warn(out)
    try:
        os.remove("../output.json")
    except  FileNotFoundError:
        pass

    with open("../output.json", "x") as file:
        json.dump(out, file)

    st.session_state['data_download'] = False

col1, col2 = st.columns(2)
with col1:
    process_button = st.button("Обработать данные", 
                               key="process_button",
                               on_click = process_data,
                               disabled=st.session_state['data_process']

                               )






if uploaded_video is not None: # run only when user uploads video
    vid = uploaded_video.name
    st.session_state['vid'] = vid

    with open(vid, mode='wb') as f:
        f.write(uploaded_video.read()) # save video to disk

    st.markdown(f"""
    ### Files
    - {vid}
    """,
    unsafe_allow_html=True) # display file name
with col2:
    st.download_button(
        "Скачать json",
        data=Path("../output.json").read_text(),
        file_name="output.json",
        mime="application/json",
        disabled = st.session_state['data_download'],
    )


def load_data():
    data = pd.read_csv("data.csv")
    return data

data_ = load_data()

st.dataframe(data_)


chart_data = pd.DataFrame(time_plot, columns=["рыбовые"])
st.area_chart(chart_data,
              y = "рыбовые",
              color = ["#cc6666"])

size_data = pd.DataFrame.from_dict(size_plot)

size_data['min'] = scaler_min.fit_transform(size_data[['mean']])
size_data['mean'] = scaler_mean.fit_transform(size_data[['mean']])
size_data['max'] = scaler_max.fit_transform(size_data[['mean']])
print(size_plot[:20])
st.area_chart(size_data,
              y=["min", "max", "mean"],
              color = ["#88b5d3", "#4a8cb9", "#516372"]
              )


red_data = pd.DataFrame.from_dict(red_plot)

st.area_chart(red_data,
              y=["red", "silver"],
              color = ["#cc0033", "#92a0a3" ]
              )

