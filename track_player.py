import cv2
from ultralytics import YOLO
import numpy as np
from pathlib import Path
from collections import defaultdict
from ultralytics.utils.plotting import Annotator
import supervision as sv
import os
import utils
import st_env
from narya.models.keras_models import KeypointDetectorModel
from narya.utils.masks import _points_from_mask 
from narya.utils.homography import warp_image,get_perspective_transform

def trackplayer(video, save = True,mot="bytetrack"):
    ## mot: botsort, bytetrack
    filename = st_env.File.split("\\")[1].split(".")[0]
    # filename= filename
    #load weights
    checkpoints=os.path.abspath("keypoint_detector.h5")
    kp_model = KeypointDetectorModel(
        backbone='efficientnetb3', num_classes=29, input_shape=(st_env.kp_model_shape),
    )
    kp_model.load_weights(checkpoints)

    os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

    #Convert from RGB space since opencv was defaulted to BGR
    teamcolorlist={"Home":utils.hex_to_rgb(st_env.colors["Home"]),"Home_keeper":utils.hex_to_rgb(st_env.colors["Home_keeper"]),
                "Away":utils.hex_to_rgb(st_env.colors["Away"]),"Away_keeper":utils.hex_to_rgb(st_env.colors["Away_keeper"]),
                "Referee":utils.hex_to_rgb(st_env.colors["Referee"])}
    bgrteamcolorlist=dict()
    matpltlibcolorlist=dict()
    st_env.colorrange =50
    for key, teamcolor in teamcolorlist.items():
        orgcolor=(teamcolor[2],teamcolor[1],teamcolor[0])
        matpltlibcolorlist[key] = (teamcolor[0]/255.,teamcolor[1]/255.,teamcolor[2]/255.)
        b1,b2=[],[]
        for color in teamcolor:
            if color-st_env.colorrange<=0:
                b1.append(0)
                b2.append(color+st_env.colorrange)
            elif color+st_env.colorrange>=255:
                b2.append(255)
                b1.append(color-st_env.colorrange)
            else:
                b1.append(color-st_env.colorrange)
                b2.append(color+st_env.colorrange)
        b1.reverse()
        b2.reverse()
        b1,b2=tuple(b1),tuple(b2)
        bgrteamcolorlist[key]=[orgcolor,b1,b2]


    # Define empty DataFrame for storing data
    data = []
    track_history = defaultdict(lambda: [])
    track_transformed_history = defaultdict(lambda: [])
    team_history = defaultdict(lambda: [])
    model = YOLO("trained_x.pt")
    names = model.model.names
    video_path =st_env.File

    if not Path(video_path).exists():
        raise FileNotFoundError(f"Source path '{video_path}' does not exist.")

    import pandas as pd
    df = pd.DataFrame(columns = ["Frame", "track_id","team","coordinates_2d_x","coordinates_2d_y", "coordinates_3d_x","coordinates_3d_y","homo","color"])
    cap = cv2.VideoCapture(video_path)
    frameno = 0
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pr_mask = kp_model(frame)
            src,dst = _points_from_mask(pr_mask[0])
            
            results = model.track(frame, persist=True, tracker=f"{mot}.yaml")
            detections = sv.Detections.from_ultralytics(results[0])
            if len(detections) > 0:
                boxes = results[0].boxes.xywh.cpu()
                clss = results[0].boxes.cls.cpu().tolist()
                track_ids = results[0].boxes.id.int().cpu().tolist()

                annotator = Annotator(frame, line_width=1,
                                    example=str(names))

                for box, track_id, cls in zip(boxes, track_ids, clss):
                    x, y, w, h = box
                    x1, y1, x2, y2 = (x - w / 2, y - h / 2,
                                    x + w / 2, y + h / 2)
                    by=box[1]+h/2
                    label = str(names[cls]) + " trackid: " + str(track_id)

                    box_color=(173,173,173)
                    for team,color in bgrteamcolorlist.items():
                        tempframe=frame
                        crop_img = tempframe[int(y1):int(y2),int(x1):int(x2)]
                        mask = cv2.inRange(crop_img, color[1],color[2])
                        # get nonblack vs total pixel ratio
                        colorpixelratio=cv2.countNonZero(mask)/(w*h)
                        # print(colorpixelratio)
                        if colorpixelratio > 0.2:
                            box_color=color[0]
                            label = team + label
                            team_name = team_history[track_id]
                            team_name.append(team)
                            # print(label)
                            break
                    annotator.box_label([x1, y1, x2, y2],
                        label, box_color)
                    
                    # Tracking Lines plot on bottom of box, y is inverted,0,0 start at topleftcorner
                    # print(track_history)
                    track = track_history[track_id]
                    
                    track.append((float(box[0]), float(by)))
                    #only keep last 30 frames
                    # if len(track) > 30:
                    #     track.pop(0)
                    try:
                        pred_homo = get_perspective_transform(src,dst)
                        temppoints= np.hstack(track).reshape(-1,1,2).astype(np.float32)[0][0]
                        track_transformed = track_transformed_history[track_id]
                        transformed_points = utils.scale_points(temppoints,(st_env.size),(st_env.kp_model_shape))
                        transformed_points = utils.warp_points([[transformed_points]],pred_homo)
                        track_transformed.append(transformed_points)
                    except:
                        pred_homo = np.NaN
                        transformed_points= (np.NaN,np.NaN)
                    points = np.hstack(track[-30:]).astype(np.int32).reshape((-1, 1, 2))

                    df = pd.concat([df,pd.DataFrame([{"Frame":frameno, "track_id":track_id,"team":team,
                                    "coordinates_2d_x": transformed_points[0],"coordinates_2d_y":transformed_points[1], 
                                    "coordinates_3d_x": float(box[0]),"coordinates_3d_y":float(by),"homo":pred_homo,"color":cv2.COLOR_BGR2RGB(box_color)}])],
                        ignore_index = True)
                    cv2.polylines(frame, [points], isClosed=False,
                                color=(37, 255, 225), thickness=2)

                    # Tracking circle
                    cv2.circle(frame,
                            (int(track[-1][0]), int(track[-1][1])),
                            5, (235, 219, 11), -1)
                    # cv2.ellipse(frame,
                    #             center=(int(track[-1][0]), int(track[-1][1])),
                    #             axes=(int(w), int(0.35 * h)),
                    #             angle=0.0,
                    #             startAngle=-45,
                    #             endAngle=235,
                    #             color=(37, 255, 225),
                    #             thickness=1,
                    #             lineType=cv2.LINE_4)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                pass
            cv2.imshow(f"Running NARV-Z Anayltics custom YOLOv8 model Detection on {st_env.File}", frame)
            frameno+=1
            print(frameno)
            
        else:
            break
        # frameno+=1
        # print(frameno)

    cap.release()
    cv2.destroyAllWindows()

    # Export data to CSV file
    output_file= filename+".csv"
    df.to_csv(f"streamlit_storage\\matches\\{output_file}", index=False)
    print(f"Tracking data exported to {output_file}")


