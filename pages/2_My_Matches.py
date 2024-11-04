import streamlit as st
import base64
import pandas as pd
import numpy as np
from io import StringIO
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import mpld3
import streamlit.components.v1 as components
from streamlit_image_coordinates import streamlit_image_coordinates
import sys
sys.path.append('..')
import utils
import st_env
from draw_pitch import draw_soccer_pitch

@st.experimental_fragment
def plot_avgpos(newdf,team):
    
    homedf=newdf
    home_data = homedf[(homedf['team'] == f'{team}')|(homedf['team'] == f'{team}_keeper')]
    player_trackid_list = home_data['track_id'].unique().tolist()
    homepopover = st.popover("Filter players")
    homepopover.markdown("Select players")
    home_trackid_dict=dict()
    for id in player_trackid_list:
        home_trackid_dict[id] = homepopover.checkbox(f"{team}:{id}", True,key=f'{team}_avgpos_{id}')
    print(home_trackid_dict)
    filtered_home_data = home_data.loc[home_data['track_id'].map(home_trackid_dict)]
    # Group by track_id and calculate the mean coordinates for each group
    average_positions = filtered_home_data.groupby('track_id')[['coordinates_2d_x', 'coordinates_2d_y']].mean()
    # print(average_positions)
    # Merge the average_positions DataFrame with the original DataFrame on track_id
    avg_df = pd.merge(home_data[['team', 'track_id','color']].drop_duplicates(), average_positions, on='track_id')
    fig, ax = draw_soccer_pitch(st_env.plot_size)
    # fig, ax = plt.subplots(figsize=(72,40.6))
    # sns.heatmap(home_coordinates.set_index('coordinates_2d_x'), annot=True, cmap="YlGnBu", ax=ax)
    from matplotlib.patches import Ellipse
    for id, val in home_trackid_dict.items():
    # x,y= utils.invert_y((x,y),st_env.plot_size)
        if val:
            team = avg_df[avg_df['track_id']== id]['team'].iloc[0]
            color = avg_df[avg_df['track_id']== id]['color'].iloc[0]
            # print(team)
            x,y = int(avg_df[avg_df['track_id']== id]['coordinates_2d_x'].iloc[0]), int(avg_df[avg_df['track_id']== id]['coordinates_2d_y'].iloc[0])
            ax.add_artist(Ellipse(
                            (x,y),
                            2,2,
                            edgecolor="white",
                            linewidth=1,
                            # facecolor=st_env.colors[team],
                            # facecolor=mpl.colors.to_rgba(eval(color)),
                            # facecolor=utils.rgb_to_hex(eval(color)),

                            #input is bgr value
                            facecolor=utils.bgr_to_hex(eval(color)),
                            # alpha=0.8,
                            zorder=20,
                        ))
            plt.text(
                        x,y,
                        id,#playernumber
                        horizontalalignment="center",
                        verticalalignment="center",
                        fontsize=8,
                        color="white",
                        zorder=22,
                        alpha=0.8,
                    )

    ax.set_title(f'Average Player Position for {team} Team')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    st.pyplot(fig)

def main():
    st.set_page_config(
    page_title="NARV-Z Dashboard",
    page_icon="⚽",
    layout="wide",
    )

    st.title("Match Statistics")
    with st.sidebar:
        st_env.getsidebar()

    defaultfile="tracking_data_new.csv"
    filename = st_env.file_selector(st_env.match_folder,selected_filename=defaultfile)
    df = pd.read_csv(filename)

    df = df.interpolate(method='linear')

    newdf = pd.DataFrame(columns=["Frame","track_id","team",'coordinates_2d_x', 'coordinates_2d_y','color'])
    for index, row in df.iterrows():
        x = row['coordinates_2d_x']
        y= row['coordinates_2d_y']
        transformed_points = utils.scale_points((x,y),st_env.kp_model_shape,st_env.plot_size)
        # row['coordinates_2d_x'] = transformed_points[0]
        # row['coordinates_2d_y'] = transformed_points[1]
        newdf= pd.concat([newdf,pd.DataFrame([{"Frame":row['Frame'],"track_id":row['track_id'],'team':row['team'],'coordinates_2d_x':transformed_points[0], 'coordinates_2d_y':transformed_points[1],'color':row['color']}])])

    col1, col2 = st.columns(2)
    with col1:
        st.header("Home Team heatmap")
        @st.experimental_fragment
        def plot_heatmap():
            
            homedf=newdf
            home_data = homedf[homedf['team'] == 'Home']
            player_trackid_list = home_data['track_id'].unique().tolist()
            homepopover = st.popover("Filter players")
            homepopover.markdown("Select players")
            home_trackid_dict=dict()
            for id in player_trackid_list:
                home_trackid_dict[id] = homepopover.checkbox(f"Home:{id}", True)
            # print(home_trackid_dict)
            filtered_home_data = home_data.loc[home_data['track_id'].map(home_trackid_dict)]
            home_coordinates = filtered_home_data[['coordinates_2d_x', 'coordinates_2d_y']]
            fig, ax = draw_soccer_pitch(st_env.plot_size)
            from scipy.stats import gaussian_kde
            xy = np.vstack([home_coordinates['coordinates_2d_x'], home_coordinates['coordinates_2d_y']])
            z = gaussian_kde(xy)(xy)
            plt.scatter(home_coordinates['coordinates_2d_x'], home_coordinates['coordinates_2d_y'],c=z)
            ax.set_title('Heatmap of Average Player Coordinates for Home Team')
            ax.set_xlabel('X Coordinate')
            ax.set_ylabel('Y Coordinate')
            st.pyplot(fig)
        plot_heatmap()
        
            
        plot_avgpos(newdf,team="Home")
    with col2:
        st.header("Away Team heatmap")
        enemydf=newdf
        enemy_data = enemydf[enemydf['team'] == 'Away']
        enemy_player_trackid_list = enemy_data['track_id'].unique().tolist()
        enemypopover = st.popover("Filter players")
        enemypopover.markdown("Select players")
        enemy_trackid_dict=dict()
        for id in enemy_player_trackid_list:
            enemy_trackid_dict[id] = enemypopover.checkbox(f"Away:{id}", True)
        filtered_enemy_data = enemy_data.loc[enemy_data['track_id'].map(enemy_trackid_dict)]
        enemy_coordinates = filtered_enemy_data[['coordinates_2d_x', 'coordinates_2d_y']]
        fig, ax = draw_soccer_pitch(st_env.plot_size)
        from scipy.stats import gaussian_kde
        xy = np.vstack([enemy_coordinates['coordinates_2d_x'], enemy_coordinates['coordinates_2d_y']])
        z = gaussian_kde(xy)(xy)
        plt.scatter(enemy_coordinates['coordinates_2d_x'], enemy_coordinates['coordinates_2d_y'],c=z)
        ax.set_title('Heatmap of Average Player Coordinates for Enemy Team')
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        st.pyplot(fig)
        plot_avgpos(newdf,team="Away")

    
if __name__ == "__main__":
    main()