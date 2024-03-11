import streamlit as st
import pandas as pd

@st.cache_data(ttl=0.01)
def load_data():
    data = pd.read_csv("data.csv")
    inds = data[(data.lon ==0) & (data.lat == 0)].index

    data.drop(index=inds, inplace=True, axis='columns')
    data.reset_index(inplace=True, drop=True)
    data.to_csv("~/projects/fish/data.csv", index=False)
    return data

data_coord = load_data()

if "add_mes" not in st.session_state:
    st.session_state["add_mes"] = True



def on_change_data():
    df = pd.read_csv("~/projects/fish/data.csv")
    edits = st.session_state["df_editor"]["edited_rows"]
    for row_id, change in edits.items():
        if not change:
            break
        row = df.loc[row_id]
        for key, value in change.items():
            row[key] = value
        
        #df.loc[row_id] = change

    df.to_csv("~/projects/fish/data.csv", index=False)

def add_data_row(lat, lon):
    df =pd.read_csv("~/projects/fish/data.csv")
 
    cam_id = df['camera_id'].max() + 1
    change = {"lat":lat,
              "lon":lon,
              "camera_id":cam_id
            }
    df.loc[len(df.index)] = change
    df.to_csv("~/projects/fish/data.csv", index=False)


col1, col2, col3 = st.columns(3)


with col1:
    lat = st.number_input("Введите широту:", 
                          value=0.0,
                          #on_change=set_add
                          )
    
with col2:
    lon = st.number_input("Введите долготу:", 
                          value=0.0,
                          #on_change=set_add
                          )
with col3:
    st.button("Добавить данные",
              disabled = not (lat>0 and lon>0),
              on_click=add_data_row,
              key="add_measure",
              kwargs={"lat":lat, "lon":lon})
                
edited_df = st.data_editor(data_coord, 
                           num_rows="dynamic",
                           key="df_editor",
                           on_change=on_change_data
                            
                           )


