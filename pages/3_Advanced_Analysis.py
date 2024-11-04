import streamlit as st
import base64
import pandas as pd
from io import StringIO
from pathlib import Path
from draw_pitch import draw_soccer_pitch
from streamlit_image_coordinates import streamlit_image_coordinates
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
import sys
sys.path.append('..')
import st_env

# Get an instance of pygwalker's renderer. You should cache this instance to effectively prevent the growth of in-process memory.
@st.cache_resource
def get_pyg_renderer(filename) -> "StreamlitRenderer":
    df = pd.read_csv(filename)
    # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
    return StreamlitRenderer(df, spec="./gw_config.json")


def main():
    st.set_page_config(
    page_title="NARV-Z Analysis",
    page_icon="⚽",
    layout="wide",
    )
    with st.sidebar:
        st_env.getsidebar()
    st.title("Match Statistics")

    filename = st_env.file_selector(st_env.match_folder)
    # Establish communication between pygwalker and streamlit
    init_streamlit_comm()
    
    
    
    renderer = get_pyg_renderer(filename)
    
    # Render your data exploration interface. Developers can use it to build charts by drag and drop.
    renderer.render_explore()

    
if __name__ == "__main__":
    main()