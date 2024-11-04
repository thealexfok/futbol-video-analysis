import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_soccer_pitch(figsize=(105, 68),orientation="horizontal",flex=False):
    """
    Plots a soccer pitch of length 105*68 metres which are the recommended dimensions allowed by FIFAs "Stadium Guidelines" 
    https://publications.fifa.com/en/football-stadiums-guidelines/technical-guideline/stadium-guidelines/pitch-dimensions-and-surrounding-areas/
    
    Parameters:
    - figsize: Tuple, optional, default: (105, 68)
        Size of the soccer pitch.
    - orientation: string, optional, default: horizontal
        If horizontal, plot the soccer pitch in a horizontal direction.
        If vertical, plot the soccer pitch in a vertical direction.
    - flex: boolean, optional, default: False
        If True, penalty area and other markings will be resized to be proportional to new size
        If False, penalty area and other markings will be fixed 
    """


    # Standard dimensions
    standard_length = 105
    standard_width = 68
    
    # Scale factor based on figsize and standard dimensions
    scale_length = figsize[0] / standard_length
    scale_width = figsize[1] / standard_width

    # Elements sizes (penalty area, goal area, center circle) with scaling if flex is True
    penalty_area_width = 16.5 * scale_width if flex else 16.5
    #小禁區
    goal_area_width = 5.5 * scale_width if flex else 5.5
    center_circle_radius = 9.15 * (scale_length+scale_width)/2 if flex else 9.15
    # goal龍門
    goal_post_length = 7.32 * scale_width if flex else 7.32
    goal_depth = 1 * scale_length if flex else 1
    #penalty spot
    penalty_spot = 11 * scale_length if flex else 11
    #corner
    corner = 2.5 * (scale_length+scale_width)/2 if flex else 2.5
    if orientation=="vertical":
        figsize= (figsize[1],figsize[0])
        scale_length, scale_width = scale_width, scale_length
    rect = patches.Rectangle((-goal_depth, -goal_depth), figsize[0]+3, figsize[1]+3, linewidth=0.1,
                             edgecolor='r', facecolor='darkgreen', zorder=0)

    fig, ax = plt.subplots(1, figsize=(figsize[0]/10,figsize[1]/10))
    ax.add_patch(rect)
    # Main pitch markings, ie sidelines, penalty area and halfway line
    if orientation=="vertical":
        plt.plot([0, figsize[0],  figsize[0],   0, 0, figsize[0]/2-(penalty_area_width+goal_post_length/2), 
                  figsize[0]/2-(penalty_area_width+goal_post_length/2), figsize[0]/2+(penalty_area_width+goal_post_length/2), 
                  figsize[0]/2+(penalty_area_width+goal_post_length/2), figsize[0]/2+goal_area_width+goal_post_length/2, figsize[0]/2+goal_area_width+goal_post_length/2, 
                  figsize[0]/2-goal_area_width-goal_post_length/2, figsize[0]/2-goal_area_width-goal_post_length/2, figsize[0], figsize[0],  0,   0, 
                  figsize[0]/2-(penalty_area_width+goal_post_length/2), figsize[0]/2-(penalty_area_width+goal_post_length/2), 
                  figsize[0]/2+(penalty_area_width+goal_post_length/2), figsize[0]/2+(penalty_area_width+goal_post_length/2), 
                  figsize[0]/2+goal_area_width+goal_post_length/2, figsize[0]/2+goal_area_width+goal_post_length/2, figsize[0]/2-goal_area_width-goal_post_length/2, 
                figsize[0]/2-goal_area_width-goal_post_length/2],
                [0,  0, figsize[1], figsize[1], 0,     0,  penalty_area_width,  penalty_area_width,     0,     0,   goal_area_width,
                    goal_area_width,  0,  0, figsize[1]/2, figsize[1]/2, figsize[1], figsize[1], figsize[1]-penalty_area_width, 
                    figsize[1]-penalty_area_width, figsize[1], figsize[1], figsize[1]-goal_area_width, figsize[1]-goal_area_width,   
                    figsize[1]], color='white')
         # Secondary pitch markings, ie penalty spots
        # goal
        plt.plot([figsize[0]/2-goal_post_length/2, figsize[0]/2-goal_post_length/2,figsize[0]/2+goal_post_length/2, figsize[0]/2+goal_post_length/2],[0, -1,-1,0], color='white')
        plt.plot([figsize[0]/2-goal_post_length/2, figsize[0]/2-goal_post_length/2,figsize[0]/2+goal_post_length/2, figsize[0]/2+goal_post_length/2],[figsize[1], figsize[1]+1,figsize[1]+1,figsize[1]], color='white')
        #penalty spot
        plt.plot([figsize[0]/2, figsize[0]/2],[penalty_spot, penalty_spot +.25], color='white')
        plt.plot([figsize[0]/2, figsize[0]/2],[figsize[1]-penalty_spot, figsize[1]-penalty_spot-.25], color='white')
        left_arc = patches.Arc([figsize[0]/2,penalty_area_width], 16, 9.5, theta1=360.0, theta2=180.0, color='white')
        ax.add_patch(left_arc)
        right_arc = patches.Arc([figsize[0]/2,figsize[1]-penalty_area_width], 16, 9.5, theta1=180.0, theta2=360.0, color='white')
        ax.add_patch(right_arc)
    else:
        plt.plot([0,  0, figsize[0], figsize[0], 0,     0,  penalty_area_width,  penalty_area_width,     0,     0,   goal_area_width,   goal_area_width, 
                    0,  0, figsize[0]/2, figsize[0]/2, figsize[0], figsize[0], figsize[0]-penalty_area_width, figsize[0]-penalty_area_width, figsize[0], 
                    figsize[0], figsize[0]-goal_area_width, figsize[0]-goal_area_width,   figsize[0]], 
                [0, figsize[1],  figsize[1],   0, 0, figsize[1]/2-(penalty_area_width+goal_post_length/2), figsize[1]/2-(penalty_area_width+goal_post_length/2),
                  figsize[1]/2+(penalty_area_width+goal_post_length/2), figsize[1]/2+(penalty_area_width+goal_post_length/2), figsize[1]/2+goal_area_width+goal_post_length/2, 
                  figsize[1]/2+goal_area_width+goal_post_length/2,figsize[1]/2-goal_area_width-goal_post_length/2, figsize[1]/2-goal_area_width-goal_post_length/2, figsize[1], figsize[1], 
                  0,   0, figsize[1]/2-(penalty_area_width+goal_post_length/2), figsize[1]/2-(penalty_area_width+goal_post_length/2), figsize[1]/2+(penalty_area_width+goal_post_length/2)
                  , figsize[1]/2+(penalty_area_width+goal_post_length/2), figsize[1]/2+goal_area_width+goal_post_length/2, figsize[1]/2+goal_area_width+goal_post_length/2, 
                  figsize[1]/2-goal_area_width-goal_post_length/2, figsize[1]/2-goal_area_width-goal_post_length/2], color='white')
    
        # Secondary pitch markings, ie penalty spots
        # goal龍門
        plt.plot([0, -goal_depth,-goal_depth,0],[figsize[1]/2-goal_post_length/2, figsize[1]/2-goal_post_length/2,figsize[1]/2+goal_post_length/2, figsize[1]/2+goal_post_length/2], color='white')
        plt.plot([figsize[0], figsize[0]+1,figsize[0]+1,figsize[0]],[figsize[1]/2-goal_post_length/2, figsize[1]/2-goal_post_length/2,figsize[1]/2+goal_post_length/2, figsize[1]/2+goal_post_length/2], color='white')
        #penalty spot
        plt.plot([penalty_spot, penalty_spot+.25],[figsize[1]/2, figsize[1]/2], color='white')
        plt.plot([figsize[0]-penalty_spot, figsize[0]-penalty_spot-.25],[figsize[1]/2, figsize[1]/2], color='white')
    
        left_arc = patches.Arc([penalty_area_width, figsize[1]/2], 9.15, 16, theta1=270.0, theta2=90.0, color='white')
        ax.add_patch(left_arc)
        right_arc = patches.Arc([figsize[0]-penalty_area_width, figsize[1]/2], 9.15, 16, theta1=90.0, theta2=270.0, color='white')
        ax.add_patch(right_arc)

    #Unchanged regardless orientation
    centre_circle = patches.Circle([figsize[0]/2, figsize[1]/2], center_circle_radius, edgecolor='white', facecolor='darkgreen')
    ax.add_patch(centre_circle)
    # real recommended dimension was 1m, made 2.5 for better visibility
    bl_corner = patches.Arc([0, 0], corner, corner, theta1=0.0, theta2=90.0, color='white')
    tl_corner = patches.Arc([0, figsize[1]], corner, corner, theta1=270.0, color='white')
    br_corner = patches.Arc([figsize[0], 0], corner, corner, theta1=90.0, theta2=180.0, color='white')
    tr_corner = patches.Arc([figsize[0], figsize[1]], corner, corner, theta1=180.0, theta2=270.0,color='white')
    ax.add_patch(bl_corner)
    ax.add_patch(tl_corner)
    ax.add_patch(br_corner)
    ax.add_patch(tr_corner)
    
    plt.xlim(-1, figsize[0]+1)
    plt.ylim(-1, figsize[1]+1)
    plt.axis('off')    

    return fig, ax

# draw_soccer_pitch(figsize=(105, 68),orientation="vertical",flex=True)
# plt.show()
# plt.savefig("output", dpi='figure', format='png')
