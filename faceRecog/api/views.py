from .camera import VideoCamera
from django.http import StreamingHttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponse


@xframe_options_exempt
def video_feed(request):
    camera_index = int(
        request.GET.get("camera", 0)
    )  # Default to camera index 0 if not provided
    #camera_index="rtsp://admin:Admin123@192.168.0.100:554/streaming/channels/101"
    video_camera = VideoCamera(camera_index)
    # video_camera.switch_camera()

    response = StreamingHttpResponse(
        video_camera.generate_frames(),
        content_type="multipart/x-mixed-replace;boundary=frame",
    )

    # Set CORS headers explicitly

    return response
