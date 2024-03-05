import os
import random
import requests
import socket
from PIL import Image
from io import BytesIO

from ultralytics import YOLO
from label_studio_ml.model import LabelStudioMLBase
from label_studio_ml.utils import get_single_tag_keys, get_local_path

ROOT = '/'
def local_from_url(path: str) -> str:
    name = path.split('-')[-1]
    path = f"/data/images/{name}"
    return path

# hostname = socket.gethostname()
# LS_URL = socket.gethostbyname(hostname)
# print("Hostname: ", hostname)
# print("IP Address: ", ip_address)

LS_URL = "http://localhost:8080/"
LS_API_TOKEN = "a8782fff67bee98f6e0e1e18ffdb167bd9f479cb"
MODEL_NAME = 'full_size.pt'
IMGSZ = 1536
IOU = 0.5
CONF = 0.1

# Initialize class inhereted from LabelStudioMLBase
class YOLOv8Model(LabelStudioMLBase):
    def __init__(self, **kwargs):
        # Call base class constructor
        super(YOLOv8Model, self).__init__(**kwargs)

        # Initialize self variables
        self.from_name, self.to_name, self.value, self.classes = get_single_tag_keys(
            self.parsed_label_config, 'RectangleLabels', 'Image')
        self.labels = ['fish']
        # Load model
        self.model = YOLO(MODEL_NAME)
        
    def predict(self, tasks, **kwargs):
        """
        Returns the list of predictions based on input list of tasks for 1 image
        """
        task = tasks[0]

        # Getting URL of the image
        image_url = task['data'][self.value]
        full_url = LS_URL + image_url
        
        print("FULL URL: ", full_url)
        
        full_url = local_from_url(full_url)
        print("NEW LOCAL PATH: ", full_url)
        # Header to get request
        header = {
            "Authorization": "Token " + LS_API_TOKEN
        }

        # Getting URL and loading image
        image = Image.open(full_url)
        # image = Image.open(BytesIO(requests.get(
        #     full_url, headers=header).content))
        # Height and width of image
        
        original_width, original_height = image.size

        # Creating list for predictions and variable for scores
        predictions = []
        score = 0
        i = 0

        # Getting prediction using model
        results = self.model.predict(full_url,
                                     imgsz=IMGSZ,
                                     iou=IOU,
                                     conf=CONF,
                                     device='mps',
                                     )
        
        # Getting mask segments, boxes from model prediction
        for result in results:
            for i, prediction in enumerate(result.boxes):
                xyxy = prediction.xyxy[0].tolist()

                predictions.append({
                    "id": str(i),
                    "from_name": self.from_name,
                    "to_name": self.to_name,
                    "type": "rectanglelabels",
                    "score": prediction.conf.item(),
                    "original_width": original_width,
                    "original_height": original_height,
                    "image_rotation": 0,
                    "value": {
                        "rotation": 0,
                        "x": xyxy[0] / original_width * 100,
                        "y": xyxy[1] / original_height * 100,
                        "width": (xyxy[2] - xyxy[0]) / original_width * 100,
                        "height": (xyxy[3] - xyxy[1]) / original_height * 100,
                        "rectanglelabels": [self.labels[int(prediction.cls.item())]]
                    }})
                score += prediction.conf.item()

        print(f"Prediction Score is {score:.3f}.")

        # Dict with final dicts with predictions
        final_prediction = [{
            "result": predictions,
            "score": score / (i + 1),
            "model_version": "v8x"
        }]
        
        return final_prediction

    def fit(self, completions, workdir=None, **kwargs):
        """ 
        Dummy function to train model
        """
        return {'random': random.randint(1, 10)}
