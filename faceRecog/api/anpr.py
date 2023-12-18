# anpr_webcam.py

from ultralytics import YOLO
import cv2
import numpy as np
from .sort import Sort

from .util import get_car, read_license_plate, license_complies_format, format_license
import string

import easyocr

reader = easyocr.Reader(['en'], gpu=True)

# Mapping dictionaries for character conversion
dict_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}


def visualize_results(frame, results):
    for result in results:
        # Check if 'license_plate' key is present in the result dictionary
        if 'license_plate' in result:
            # Extract information from the result dictionary
            license_plate_bbox = result['license_plate']['bbox']
            license_plate_text = result['license_plate']['text']

            # Ensure bounding box coordinates are integers
            license_plate_bbox = [int(coord) for coord in license_plate_bbox]

            # Draw a filled rectangle with a dark background for the license plate text
            # Increase text size by modifying font size and thickness
            font_size = 2.0  # You can adjust this value to increase or decrease text size
            font_thickness = 3  # You can adjust this value to increase or decrease text thickness

            # Draw the filled rectangle
            
            # Draw the license plate text
            frame = cv2.putText(frame, license_plate_text,
                                (license_plate_bbox[0], license_plate_bbox[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), font_thickness)

    return frame





# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=True)


def generate_anpr_frames(camera_index):
    # Load models
    coco_model = YOLO('yolov8n.pt')
    license_plate_detector = YOLO('/Users/vinodkumar/Desktop/Security OS/dj-FR/faceRecog/api/best.pt')

    # Initialize SORT tracker
    mot_tracker = Sort()
    if camera_index == 1:
        camera_index = "rtsp://admin:Admin123@192.168.0.162:554/streaming/channels/201"
    else:
        camera_index = "rtsp://admin:Admin123@192.168.0.162:554/streaming/channels/101"
    # Open webcam
    cap = cv2.VideoCapture(camera_index)

    vehicles = [2, 3, 5, 7]

    frame_nmr = -1

    while True:
        frame_nmr += 1

        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            break

        # Initialize results dictionary
        results = [{}]
        # frame = cv2.resize(frame, (720, 360))

        # Detect license plates
        license_plates = license_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate
        
            # Crop license plate
            license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]
            print("crop")
            # Process license plate
            license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)
            print("process")
            # Read license plate number
            license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)
            print(license_plate_text)
            if license_plate_text is not None:
                # Check license plate format
                if license_complies_format(license_plate_text):
                # if license_plate_text:
                    # Format license plate
                    # formatted_license_plate = license_plate_text
                    formatted_license_plate = format_license(license_plate_text)
                    print(formatted_license_plate)
                    results.append({'license_plate': {'bbox': [x1, y1, x2, y2],
                                'text': formatted_license_plate,
                                'bbox_score': score,
                                'text_score': license_plate_text_score}})
                    # print(results)
        # Perform visualization
        frame = visualize_results(frame, results)

        # Display the frame
        frame = cv2.resize(frame, (720, 360))
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            break
        
        #print(frame.shape)
        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

if __name__ == "__main__":
    generate_anpr_frames()
