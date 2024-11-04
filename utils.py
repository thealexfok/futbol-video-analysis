import cv2
import numpy as np
import random
import time
import streamlit as st

def progressbar(function, progress_text):
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    yield function()
    time.sleep(1)
    my_bar.empty()

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def bgr_to_hex(bgr_tuple):
    # Extract BGR components
    blue, green, red = bgr_tuple
    
    # Convert to hexadecimal string
    hex_value = "#{:02x}{:02x}{:02x}".format(red, green, blue)
    
    return hex_value

@st.experimental_fragment
def getRandomFrame(videofile,frame=None,save=False):
    #frame 0 for first frame
    vidcap = cv2.VideoCapture(videofile)
    if frame is None:
        randomFrameNumber=random.randint(0,getNumberofFrames(videofile))
        vidcap.set(cv2.CAP_PROP_POS_FRAMES,randomFrameNumber)
    else:
        vidcap.set(cv2.CAP_PROP_POS_FRAMES,frame)
    success, image = vidcap.read()
    if success:
        if save:
            cv2.imwrite(f"{frame}.jpg", image)  # save frame as JPEG file
        return image

@st.experimental_fragment
def getFrame(videofile,frame=0,save=False):
    #frame 0 for first frame
    vidcap = cv2.VideoCapture(videofile)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES,frame)
    success, image = vidcap.read()
    if success:
        if save:
            cv2.imwrite(f"{frame}.jpg", image)  # save frame as JPEG file
        return image

def getNumberofFrames(videofile):
    vidcap = cv2.VideoCapture(videofile)
    return vidcap.get(cv2.CAP_PROP_FRAME_COUNT)

def scale_points(coordinates,input_shape,output_shape):
    """
    Scales a set of points from the center of an input shape to an output shape.

    Parameters:
    - coordinates: A list of tuples, where each tuple represents a point (x, y).
    - input_shape: A tuple representing the input shape dimensions (width, height).
    - output_shape: A tuple representing the output shape dimensions (width, height).

    Returns:
    - A list of tuples, where each tuple represents the scaled point (x, y).
    """


    scale_x = output_shape[0] / input_shape[0]
    scale_y = output_shape[1] / input_shape[1]
    
    transformed_coordinates = (coordinates[0]*scale_x,coordinates[1]*scale_y)

    return transformed_coordinates

def warp_points(pts, homography):
    dst = cv2.perspectiveTransform(np.array(pts).reshape(-1, 1, 2), homography)

    # # matplotlib coord starts bottom left instead of upper left hence inverting y axis
    #     transformed_points =(transformed_points[0][0][0],st_env.size[1]-transformed_points[0][0][1])
    return dst[0][0]


def invert_y(pts, shape):
    return (pts[0],shape[1]-pts[1])
    