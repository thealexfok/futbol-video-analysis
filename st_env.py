#video file path 
File = None
File = "streamlit_storage\\"+"0a2d9b_0.mp4"
size = 1920,1080
plot_size=105,68
kp_model_shape = 320,320
colors= {"Home":"#000000","Home_keeper":"#000000","Away":"#000000","Away_keeper":"#000000","Referee":"#000000",}
team_color = "#000000"
team_gk_color = "#000000"
opponent_team_color = "#000000"
opponent_team_gk_color = "#000000"
ref_color = "#000000"
color_range = 70
frame=0



#web
import streamlit as st
import base64
import pandas as pd
from io import StringIO
import os
from pathlib import Path
from datetime import datetime

storage_folder="streamlit_storage"
match_folder="streamlit_storage/matches"
accepted_file_type=["mov", "mp4","mkv","m4v"]


def save_uploadedfile(uploadedfile):
     with open(os.path.join(storage_folder,uploadedfile.name),"wb") as f:
         f.write(uploadedfile.getbuffer())
     return st.success(f"Saved File:{uploadedfile.name} to {storage_folder}")

def file_selector(folder_path='.',msg='Select a file from uploaded storage',selected_filename=None,file_types=[]):
    exclude= []
    filenames = os.listdir(folder_path)
    for i in filenames:
        if exclude !=[]:
            for j in exclude:
                if j in i or "." not in i:
                    filenames.remove(i)
        elif "." not in i:
            filenames.remove(i)
    selected_filename = st.selectbox(msg, filenames)
    if selected_filename is None:
        raise ValueError("There are no saved matches")
    return os.path.join(folder_path, selected_filename)

def fileselection(filepath):
    global File
    File=filepath


def getsidebar():
    logoname="narv-z white.png"
    logo = f"url(data:image/png;base64,{base64.b64encode(Path(logoname).read_bytes()).decode()})"
    st.markdown(
            f"""
            <style>
                [data-testid="stSidebar"] {{
                    background-image: {logo};
                    background-repeat: no-repeat;
                    position: fixed;
                    padding-top: 2rem;
                    background-position: 1rem 1rem;
                    background-size: 12rem, contain;
                }}
                [data-testid="stSidebarNav"]::before {{
                    content: "Soccer Analytics";
                    margin-left: 1rem;
                    font-size: 28px;
                    position: relative;
                    top: 1rem;
                }}
                [data-testid='stSidebarNav'] > ul {{
                    min-height: 60vh;
                }}
            </style>
            """, unsafe_allow_html=True,
        )
    from st_social_media_links import SocialMediaIcons

    social_media_links = [
        "https://www.instagram.com/TheAlexFok",
        "https://www.github.com/thealexfok",
    ]

    colors = ["White", "White"]
    social_media_icons = SocialMediaIcons(social_media_links,colors)

    social_media_icons.render()
    
    year = datetime.now().strftime('%Y')
    st.header("")
    st.write("Designed by Alex Fok", divider="")
    st.write(f":white[© NARV-Z {year}]")