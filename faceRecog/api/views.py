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
from .anpr import generate_anpr_frames

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
        model_file = "gocolab2.pt"
        model_path = os.path.join(os.path.dirname(__file__), model_file)
        response = StreamingHttpResponse(
            generate_yolo_frames(video_camera, model_path),
            content_type="multipart/x-mixed-replace;boundary=frame",
        )
    elif model_type == "ANPR":
        video_camera = VideoCamera(camera_index)
        anpr_model_file = "best.pt"  # Update with the correct model file
        anpr_model_path = os.path.join(os.path.dirname(__file__), anpr_model_file)
        response = StreamingHttpResponse(
            generate_anpr_frames(video_camera),
            content_type="multipart/x-mixed-replace;boundary=frame",
        )
    # elif model_type == "ANPR":
    #     video_camera = VideoCamera(camera_index)
    #     response = StreamingHttpResponse(
    #         generate_anpr_frames(video_camera),
    #         content_type="multipart/x-mixed-replace;boundary=frame",
    #     )
    else:
        response = HttpResponse("Invalid model_type")

    return response

def generate_yolo_frames(video_camera, model_path):
    yolo_model = YOLO(model_path)
    threshold = 0.5

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

# def generate_anpr_frames(video_camera):
#     reader = easyocr.Reader(['en'])
    
#     while True:
#         ret, frame = video_camera.cap.read()
#         if not ret:
#             break

#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
#         edged = cv2.Canny(bfilter, 30, 200)

#         keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#         contours = imutils.grab_contours(keypoints)
#         contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
#         location = None
#         for contour in contours:
#             approx = cv2.approxPolyDP(contour, 10, True)
#             if len(approx) == 4:
#                 location = approx
#                 break

#         if location is not None:
#             mask = np.zeros(gray.shape, np.uint8)
#             new_image = cv2.drawContours(mask, [location], 0, 255, -1)
#             new_image = cv2.bitwise_and(frame, frame, mask=mask)

#             (x, y) = np.where(mask == 255)
#             (x1, y1) = (np.min(x), np.min(y))
#             (x2, y2) = (np.max(x), np.max(y))
#             cropped_image = gray[x1:x2 + 1, y1:y2 + 1]

#             result = reader.readtext(new_image)

#             # Check if result is not empty before accessing its elements
#             if result:
#                 text = result[0][-2]

#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 frame = cv2.putText(frame, text=text, org=(location[0][0][0], location[1][0][1] + 60),
#                                     fontFace=font, fontScale=1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
#                 frame = cv2.rectangle(frame, tuple(location[0][0]), tuple(location[2][0]), (0, 255, 0), 3)
#         frame = cv2.resize(frame, (720, 360))
#         ret, buffer = cv2.imencode(".jpg", frame)
#         if not ret:
#             break

#         frame = buffer.tobytes()
#         yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
