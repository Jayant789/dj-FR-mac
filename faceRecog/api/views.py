from .camera import VideoCamera
from django.http import StreamingHttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponse
import cv2
import os
from ultralytics import YOLO  # Import your YOLO model class


@xframe_options_exempt
def video_feed(request):
    camera_index = int(
        request.GET.get("camera", 0)
    )  # Default to camera index 0 if not provided
    model_type = request.GET.get(
        "model", "FR"
    )  # Default to face recognition if not provided

    if model_type == "FR":
        # Original functionality
        video_camera = VideoCamera(camera_index)
        response = StreamingHttpResponse(
            video_camera.generate_frames(),
            content_type="multipart/x-mixed-replace;boundary=frame",
        )
    elif model_type == "SD":
        # New functionality with YOLO model on camera feed
        video_camera = VideoCamera(camera_index)

        response = StreamingHttpResponse(
            generate_yolo_frames(video_camera),
            content_type="multipart/x-mixed-replace;boundary=frame",
        )
    else:
        # Handle invalid model_type
        response = HttpResponse("Invalid model_type")

    # Set CORS headers explicitly
    return response


def generate_yolo_frames(video_camera):
    model_path = os.path.join(
        r"C:\Users\jayan\Desktop\Argenbright\Spill and Leaks", "gocolab.pt"
    )

    # Load a model
    yolo_model = YOLO(model_path)  # load a custom model

    threshold = 0.1

    while True:
        frame = video_camera.get_frame()

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

        _, jpeg = cv2.imencode(".jpg", frame)
        frame_bytes = jpeg.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n"
        )

    # The generator function will keep running indefinitely, providing frames for the streaming response.
