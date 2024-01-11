from .camera import VideoCamera
from django.http import StreamingHttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponse
import cv2
import os
import easyocr
import numpy as np
import imutils
from ultralytics import YOLO
# from .anpr import generate_anpr_frames

@xframe_options_exempt
def video_feed(request):
    camera_index = int(request.GET.get("camera", 0))
    model_type = request.GET.get("model", "FR")

    if model_type == "FR":
        video_camera = VideoCamera(camera_index)
        response = StreamingHttpResponse(
            video_camera.generate_frames(),
            content_type="multipart/x-mixed-replace;boundary=frame",
        )
    elif model_type == "SD":
        video_camera = VideoCamera(camera_index)
        model_file = "gocolab3.pt"
        model_path = os.path.join(os.path.dirname(__file__), model_file)
        response = StreamingHttpResponse(
            generate_yolo_frames(video_camera, model_path),
            content_type="multipart/x-mixed-replace;boundary=frame",
        )
    # elif model_type == "ANPR":
    #     video_camera = VideoCamera(camera_index)
    #     anpr_model_file = "best.pt"  # Update with the correct model file
    #     anpr_model_path = os.path.join(os.path.dirname(__file__), anpr_model_file)
    #     response = StreamingHttpResponse(
    #         generate_anpr_frames(video_camera),
    #         content_type="multipart/x-mixed-replace;boundary=frame",
    #     )
    elif model_type == "ANPR":
        video_camera = VideoCamera(camera_index)
        model_file = "best.pt"
        model_path = os.path.join(os.path.dirname(__file__), model_file)
        response = StreamingHttpResponse(
            generate_anpr_frames(video_camera,model_path),
            content_type="multipart/x-mixed-replace;boundary=frame",
        )
    else:
        response = HttpResponse("Invalid model_type")

    return response

def generate_yolo_frames(video_camera, model_path):
    yolo_model = YOLO(model_path)
    threshold = 0
    print("Spill")
    while True:
        ret, frame = video_camera.cap.read()
        if not ret:
            break
        results = yolo_model(frame)[0]
        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score > threshold:
                cv2.rectangle(
                    frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4
                )
                cv2.putText(
                    frame,
                    results.names[int(class_id)].upper(),
                    (int(x1), int(y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.3,
                    (0, 255, 0),
                    3,
                    cv2.LINE_AA,
                )

        frame = cv2.resize(frame, (720, 360))
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            break

        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

def generate_anpr_frames(video_camera, model_path):
    reader = easyocr.Reader(['en'])
    yolo_model = YOLO(model_path)
    threshold=0.1
    print("ANPR")
    while True:
        ret, frame = video_camera.cap.read()
        if not ret:
            break

        results = yolo_model(frame)[0]
        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score > threshold:
                
                
                cropped_plate = frame[int(y1):int(y2), int(x1):int(x2)]

                # Send the cropped image to EasyOCR for text recognition
                plate_result = reader.readtext(cropped_plate)

                # Check if result is not empty before accessing its elements
                if plate_result:
                    plate_text = plate_result[0][-2]
                    
                    if plate_text == "MH 02 DC 1234" or plate_text == "RJ 07 RM 6905":
                        # Draw text on the original frame
                        cv2.rectangle(
                        frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4
                        )
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        frame = cv2.putText(frame, text=plate_text, org=(int(x1), int(y1) - 30),
                                            fontFace=font, fontScale=2, color=(0, 255, 0), thickness=5, lineType=cv2.LINE_AA)
                    elif len(plate_text)== 13:
                        # Draw text on the original frame
                        cv2.rectangle(
                        frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 4
                        )
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        frame = cv2.putText(frame, text=plate_text, org=(int(x1), int(y1) - 30),
                                            fontFace=font, fontScale=2, color=(0, 0, 255), thickness=5, lineType=cv2.LINE_AA)
                    
                    else:
                        cv2.rectangle(
                        frame, (int(x1), int(y1)), (int(x2), int(y2)), (125, 125, 125), 4
                        )
                        

        frame = cv2.resize(frame, (720, 360))
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            break

        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")