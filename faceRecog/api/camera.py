import cv2
from .simple_facerec import SimpleFacerec
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db  # Import the Realtime Database module
from datetime import datetime
import time
import os


class VideoCamera(object):
    firebase_initialized = False

    def __init__(self, camera_index=0):
        if not VideoCamera.firebase_initialized:
            # Initialize Firebase only if it hasn't been done already
            cred = credentials.Certificate(
                {
                    "type": "service_account",
                    "project_id": "abl-security-b033d",
                    "private_key_id": "ed63ecb605fa96b95c54d642033f71de592f6c97",
                    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC0zYE5H0vdeBPG\nalokzev5DD8MtRltEwGyZLNCDnlXdYyBNYsbzMc0kEyJ6+c3cZIsyFLWVdQBGdJt\noy15RRLEPw1nPY6r025dToRCfxbdrtGo4bg9mOF4CB4jLLyfFjKmvBh1JqGVIpMl\n4RZrH0O7SS226ldtl3EPdd5BPCnsL4CsatnEd89jNvIpShYKjxvoeHVNGxOKnuAG\n69lWGx2Kj2E/qr26WtfJC0CfHQEICIKbLHPDwqkK4xkdFrBoJtKNyWZM9b7MDZ8D\nKr0aGIYQ69D+/WfM47We1+XARNkBlZH/KoyqGEqJYZxljKKFtzOYkvmMKhnaMgwG\nr4JLPOtzAgMBAAECggEAArKri99TON2WQkZ7zFAJmsb1JQRWt3NqYD8e4EyQofg1\nS9SxXn4rMhdXdlKHWKL+J0RRvq94/BmzXJJhwm5mkv041fWmnTlqCgG4ReH9Fp7/\nYY8PbZLCECaRQnrUo2XiqNi4X4KDNE40CG73/6bGuL5ii07d71Cxiy+dx5gu5VMG\nrJqKGfgN2Fks28O056deaShpP59DMJmd+dKkyISOMVNKYxEHs08PL4bCUuFKyo0m\n8unJZ1Xax+dyxO3bFubBKGdBtBHCwlVmJXY9+MMYkgO/fOLoLQhjfFxYiWyb2jeE\nCbrwLuiz/wv6ZxZQ+tO9vgk2hIlL08UD7wet9PetkQKBgQD8+9Z/6yJjfjDKkzcy\n+y3nYc11FX4ss3nlyhDOTmf4TIQWmtRfkXQp9g6b9VNXJyCsGce4wOim7wNBtyZE\nj5eNBzHLZH2QZvv+qgRbVAU31MytOBXwZTxdgmOlvKrel2RP5JYiMVU26zopJ5uz\nRlVg8IpyVJK2i5yfurKkJyTBEQKBgQC29VrHtq+0Mjio4Hlb3SA3PdTN+qyRhFKE\nUuxhpqT/FfszHciHUPfpE/f3G1dquiFzAOJYuCrvLCTWJHEYKvHBtlYMueYNFTOt\nk/6kFd4ZZ+q/XJVGF4NFofTIN9L2UbWHc52VwG3WDmY7U1K7VjVoXw/tdsUJB6Gv\nBuxCSfgkQwKBgQDiSW2jfDKFZjHEcYw1aOG1jxEVQsVavKszdNw1fYKYYfDgu1tt\npJCQnAyTSgxi75fU+TZhtwQjlbWHCYkMWJiJyD6tHNUH3mZXc8Jz4qLMPudZpcpR\n/mvRhLkXXbxFYIuUvvXf3drIRf3/I/OslyP1kxNzktysthLB+WCjXnQM0QKBgQCS\nF2rMrECyx6Ncnhnp07FEyxeg/jhL3fgx9zEPbIy1r2ytTWvxOSMsNyi6ZVexPj01\nYpBavXxzDLHBWMoBvVDcGGevs8VRzws74D/l8Bwv9z2IXjpIBMBqmr8mHQVUcLxe\nE2DS0hwiX88cMhWOx3DQDZBfUoZVBoYBh6qh6AS/lwKBgClU7MFAZZIwLTc/633e\neJFT+wWIyz8GhikCPQ7rnSI81Goeklr2223Rtm5wd86HYqnHKuSJiuwbc77TAzQC\nnL0UFFjxfN2G9qPOC4ZcvUWtnpYfJrH9e3mwX5pm1YgYeIGBoPTPVU12FIXo7A1f\nEKVE0T7BdBBQ9HCnSC8MDfOv\n-----END PRIVATE KEY-----\n",
                    "client_email": "firebase-adminsdk-6rtr5@abl-security-b033d.iam.gserviceaccount.com",
                    "client_id": "106922814617125507892",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-6rtr5%40abl-security-b033d.iam.gserviceaccount.com",
                    "universe_domain": "googleapis.com",
                }
            )
            firebase_admin.initialize_app(
                cred,
                {
                    "databaseURL": "https://console.firebase.google.com/u/2/project/abl-security-b033d/database/abl-security-b033d-default-rtdb/data/~2F"
                },
            )
            VideoCamera.firebase_initialized = True
            print("Firebase initialized")

        print(camera_index)
        # if camera_index == 1:
        #     camera_index = "rtsp://admin:Admin123@192.168.0.36:554/streaming/channels/201"
        # else:
        #     camera_index = "rtsp://admin:Admin123@192.168.0.36:554/streaming/channels/101"
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_ANY)
        # self.cap.set(cv2.CAP_PROP_FPS, frame_rate)  # Set the frame rate

    def __del__(self):
        self.cap.release()

    def generate_frames(self, skip_frames=2):
        print("Face Recognition")
        self.rt_db = db.reference(
            "Suspects"
        )  # Reference to the 'Suspects' node in Realtime Database
        self.sfr = SimpleFacerec()
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the images folder relative to the script directory
        images_folder_path = os.path.join(script_directory, "images")

        self.sfr.load_encoding_images(images_folder_path)
        frame_count = 0
        self.start_time = time.time()
        self.frames_processed = 0
        self.last_data_time = time.time()

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_count += 1
            self.frames_processed += 1
            elapsed_time = time.time() - self.start_time
            current_frame_rate = self.frames_processed / elapsed_time

            # Display the frame rate on the frame
            cv2.putText(
                frame,
                f"Frame Rate: {current_frame_rate:.2f} fps",
                (10, 30),
                cv2.FONT_HERSHEY_DUPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

            # Skip frames if needed
            if frame_count % skip_frames == 0:
                (
                    face_locations,
                    face_names,
                    face_accuracies,
                ) = self.sfr.detect_known_faces(frame)

                for face_loc, name, accuracy in zip(
                    face_locations, face_names, face_accuracies
                ):
                    y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
                    resize = 0.5
                    y1 = int(y1 / resize)
                    x2 = int(x2 / resize)
                    y2 = int(y2 / resize)
                    x1 = int(x1 / resize)

                    if name == "Unknown" or accuracy <= 50:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (128, 128, 128), 4)
                    else:
                        display_text = f"{name} ({accuracy}%)"
                        cv2.putText(
                            frame,
                            display_text,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_DUPLEX,
                            1,
                            (0, 0, 200),
                            2,
                        )
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

                        current_time = time.time()
                        if current_time - self.last_data_time >= 10:
                            # Prepare the data and push it to the Realtime Database
                            data = {
                                "Name": name,
                                "Date": datetime.now().date().strftime("%Y-%m-%d"),
                                "Time": datetime.now().time().strftime("%H:%M:%S"),
                                "Accuracy": accuracy,
                            }

                            # Push the data to the Realtime Database
                            new_suspect_ref = self.rt_db.push(data)
                            print(f"New Suspect added with ID: {new_suspect_ref.key}")

                            # Update the last_data_time
                            self.last_data_time = current_time

            frame = cv2.resize(frame, (720, 360))
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                break

            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
