# model_manager.py

import os
from ultralytics import YOLO
import easyocr
from .simple_facerec import SimpleFacerec

class ModelManager:
    def __init__(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        self.yolo_model_path = os.path.join(script_directory, "gocolab3.pt")
        self.anpr_model_path = os.path.join(script_directory, "best.pt")

    def load_yolo_model(self):
        return YOLO(self.yolo_model_path)

    def load_anpr_model(self):
        return easyocr.Reader(['en'])

    def load_face_recognition_model(self, images_folder_path):
        sfr = SimpleFacerec()
        sfr.load_encoding_images(images_folder_path)
        return sfr
