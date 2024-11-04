import streamlit as st
import base64
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from streamlit_image_coordinates import streamlit_image_coordinates
import matplotlib.colors
import matplotlib as mpl
import matplotlib.patches as patches
from svgpathtools import svg2paths
from svgpath2mpl import parse_path
import cv2
from PIL import Image
import time
import random
import sys
sys.path.append('..')
import st_env
import utils

from track_player import trackplayer


formations = {
    "4-3-3 DM": ["GK", "LB", "LCB", "RCB", "RB", "DM", "LCM", "RCM", "LW", "ST", "RW"],
    "4-4-2": ["GK", "LB", "LCB", "RCB", "RB", "LM", "LCM", "RCM", "RM", "LF", "RF"],
    "4-2-3-1": ["GK", "LB", "LCB", "RCB", "RB", "LCM", "RCM", "LM", "RM", "CAM", "ST"],
    "3-5-2": ["GK", "LCB", "CB", "RCB", "LM", "LCM", "CDM", "RCM", "RM", "LF", "RF"],
    "5-3-2": ["GK", "LB", "LCB", "CB", "RCB", "RB", "CDM", "LCM", "RCM", "LF", "RF"],
    "3-4-3 vertical": ["GK", "LCB", "CB", "RCB", "LM", "RM",  "CDM", "CAM", "RW", "LW", "ST"],
    "3-4-3": ["GK", "LCB", "CB", "RCB", "LM", "RM",  "LCM", "RCM", "RW", "LW", "ST"],
    "4-1-4-1": ["GK", "LB", "LCB", "RCB", "RB", "CDM", "LM", "RM", "LW", "RW", "ST"],
    "4-2-4": ["GK", "LB", "LCB", "RCB", "RB", "LCM", "CDM", "RCM", "LW", "ST", "RW"],
    "4-3-1-2": ["GK", "LB", "LCB", "RCB", "RB", "CDM", "LCM", "RCM", "CAM", "LF", "RF"],
    "4-5-1": ["GK", "LB", "LWB", "LCB", "RCB", "RWB", "RB", "LM", "CM", "RM", "ST"],
    # Add more formations as needed
}
def map_player_positions(formation, pitch_width, pitch_height):
    """
    Maps player positions to coordinates based on the given formation.

    Args:
        formation (str): The selected formation (e.g., "4-3-3").
        pitch_width (float): The width of the pitch.
        pitch_height (float): The height of the pitch.

    Returns:
        dict: A dictionary mapping player positions to coordinates.
    """

    player_coords = {}
    positions = formations[formation]

    # Define position-specific coordinates relative to pitch dimensions
    position_ratios = {
        "GK": (0.5, 0.15),
        "LB": (0.2, 0.3),
        "LCB": (0.35, 0.25),
        "RCB": (0.65, 0.25),
        "CB": (0.5, 0.25),
        "RB": (0.8, 0.3),
        "CDM": (0.5, 0.45),
        "DM": (0.5, 0.45),
        "LCM": (0.33, 0.55),
        "CM": (0.5, 0.55),
        "RCM": (0.66, 0.55),
        "LW": (0.2, 0.9),
        "CF": (0.5, 0.9),
        "RW": (0.8, 0.9),
        "CAM": (0.5, 0.8),
        "ST": (0.5, 0.95),
        "LWB": (0.08, 0.6),
        "RWB": (0.92, 0.6),
        "LM": (0.2, 0.6),
        "RM": (0.8, 0.6),
        "LF": (0.4, 0.95),
        "RF": (0.6, 0.95),
    }

    # Calculate coordinates for each player based on their position and pitch dimensions
    for i, position in enumerate(positions):
        x_ratio, y_ratio = position_ratios[position]
        x = x_ratio * pitch_width
        y = y_ratio * pitch_height
        player_coords[position] = (x, y)

    return player_coords


def main():
    st.set_page_config(
    page_title="NARV-Z Team Setup",
    page_icon="⚽",
    layout="wide",
    )
    with st.sidebar:
        st_env.getsidebar()
        
    if st_env.File is not None:
        # st.write(f":red[Target Video file:] _:blue[{st_env.File}]_")
        filename = st_env.File.split("\\")[1]
        st.write(f":red[Target Video file:] _:blue[{filename}]_")

        col1,col2 = st.columns(2)
        
        with col1:
            image = utils.getFrame(st_env.File,frame=st_env.frame)
            # st.image(image)
            # image =Image.open("test.jpg")
            # pic=image.load()
            image= Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            # display image size
            image.thumbnail((720,480), Image.Resampling.LANCZOS)
            imgcor=streamlit_image_coordinates(source=image,key="pil",)
            opponent_color_from_img=utils.hex_to_rgb(st_env.colors["Away"])
            color_from_img=utils.hex_to_rgb(st_env.colors["Home"])
            ref_color_from_img=utils.hex_to_rgb(st_env.colors["Referee"])
            color_gk_from_img=utils.hex_to_rgb(st_env.colors["Home_keeper"])
            opponent_gk_color_from_img=utils.hex_to_rgb(st_env.colors["Away_keeper"])

            if st.button("Use another frame"):
                st_env.frame= random.randint(0,utils.getNumberofFrames(st_env.File))
        with col2:
            if imgcor is not None:
                img_x,img_y = imgcor.values()
                # print(img_x,img_y)
                
                pic=image.load()
                # team = st.radio("Choose Team",["Your Team","Your Team GK","opponent Team","opponent Team GK","Ref"])
                team = st.selectbox("Choose Team",["Your Team","Your Team GK","Opponent Team","Opponent Team GK","Referee"])
                if team =="Opponent Team":
                    opponent_color_from_img=pic[img_x,img_y]
                elif team =="Opponent Team GK":
                    opponent_gk_color_from_img=pic[img_x,img_y]
                elif team =="Your Team":
                    color_from_img=pic[img_x,img_y]
                elif team =="Your Team GK":
                    color_gk_from_img=pic[img_x,img_y]
                elif team == "Referee":
                    ref_color_from_img=pic[img_x,img_y]
                # print(color_from_img)
                subcol1,subcol2 = st.columns(2)
                with subcol1:
                    # print(color_from_img)
                    st_env.colors["Home"] = st.color_picker('Pick your team color', utils.rgb_to_hex(color_from_img))
                    st.write('Your team color is', utils.hex_to_rgb(st_env.colors["Home"]))
                    st_env.colors["Home_keeper"] = st.color_picker('Pick your team GK color', utils.rgb_to_hex(color_gk_from_img))
                    st.write('Your team GK color is', utils.hex_to_rgb(st_env.colors["Home_keeper"]))
                # st.write('Your current team color is', matplotlib.colors.to_rgb(color))
                with subcol2:
                    st_env.colors["Away"] = st.color_picker('Pick your opponent team color', utils.rgb_to_hex(opponent_color_from_img))
                    st.write('Your opponent team color is', utils.hex_to_rgb(st_env.colors["Away"]))
                    st_env.colors["Away_keeper"] = st.color_picker('Pick your opponent team GK color', utils.rgb_to_hex(opponent_gk_color_from_img))
                    st.write('Your opponent team  GK color is', utils.hex_to_rgb(st_env.colors["Away_keeper"]))
                st_env.colors["Referee"] = st.color_picker('Pick referee color', utils.rgb_to_hex(ref_color_from_img))
                st.write('Referee color is', utils.hex_to_rgb(st_env.colors["Referee"]))
            else:
                st.warning("Select team color.",icon="⚠️")
            marker_path, attributes = svg2paths('jersey icon.svg')
            marker = parse_path(attributes[0]['d'])
            marker.vertices -= marker.vertices.mean(axis=0)
            marker = marker.transformed(mpl.transforms.Affine2D().rotate_deg(180))
            marker = marker.transformed(mpl.transforms.Affine2D().scale(-1,1))

            # st.button("Submit & Run", on_click= utils.progressbar(trackplayer(st_env.File),"Now running model on selected file..."))
            if st.button("Submit & Run"):
                trackplayer(st_env.File)

    else:
        st.warning("You have not selecting a video file, redirecting to Home.",icon="⚠️")
        time.sleep(2)
        st.switch_page("Home.py")

    
if __name__ == "__main__":
    main()