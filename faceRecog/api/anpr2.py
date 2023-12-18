import cv2
import easyocr
import numpy as np
import imutils

# Function to process each frame for ANPR
def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(bfilter, 30, 200)

    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    location = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            location = approx
            break

    if location is not None:
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [location], 0, 255, -1)
        new_image = cv2.bitwise_and(frame, frame, mask=mask)

        (x, y) = np.where(mask == 255)
        (x1, y1) = (np.min(x), np.min(y))
        (x2, y2) = (np.max(x), np.max(y))
        cropped_image = gray[x1:x2 + 1, y1:y2 + 1]

        reader = easyocr.Reader(['en'])
        result = reader.readtext(cropped_image)
        text = result[0][-2]

        font = cv2.FONT_HERSHEY_SIMPLEX
        frame = cv2.putText(frame, text=text, org=(approx[0][0][0], approx[1][0][1] + 60),
                            fontFace=font, fontScale=1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
        frame = cv2.rectangle(frame, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3)

    return frame

# Open a connection to the camera (adjust the camera index if needed)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    processed_frame = process_frame(frame)

    # Display the processed frame
    cv2.imshow('ANPR', processed_frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
