import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
from ensemble_boxes import weighted_boxes_fusion


class Inference:
    def __init__(
        self,
        models: list[str],
        is_tta: bool = False,
        is_imgsz: bool = True,
        imgszs = [1024],
    ):
        self.is_tta = is_tta
        self.is_imgsz = is_imgsz
        self.imgszs = imgszs

        self.models = (YOLO(path) for path in models)

    def tta(self, model, image: np.ndarray, imgsz: int, iou: float = 0.7, conf: float = 0.1) -> list[list[float]]:
        return

    def predict(self, image: np.ndarray, iou: float = 0.7, conf: float = 0.1) -> tuple[list[list[float]]]:
        '''
        return: xyxyn formath
        '''

        preds = []
        for model in self.models:
            if self.is_imgsz:
                imgszs = self.imgszs
            else:
                imgszs = [1024]

            for imgsz in imgszs:
                if self.is_tta:
                    tta_preds = self.tta(model, image, imgsz, iou, conf)
                    for pred in tta_preds:
                        preds.extend(pred)
                else:
                    pred = model.predict(image, imgsz=imgsz, iou=iou, conf=conf)[0]
                    preds.extend(pred)
        
        boxes_list = [preds[i].boxes.xyxyn for i in range(len(preds))]
        scores_list = [preds[i].boxes.conf for i in range(len(preds))]
        labels_list = [preds[i].boxes.cls for i in range(len(preds))]
        weights = [1 for i in preds]

        iou_thr = 0.2
        skip_box_thr = 0.0001

        boxes, scores, labels = weighted_boxes_fusion(boxes_list, scores_list, labels_list, weights=weights, iou_thr=iou_thr, skip_box_thr=skip_box_thr)
        
        return boxes, scores

if "name" == "__main__":
    inf = Inference(models = ["small_lr_yolox.pt", "small_lr_yolox.pt"])

    image_path = "test.JPG"

    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes, scores = inf.predict(image)

    new_image = image.copy()
    H = new_image.shape[1]
    W = new_image.shape[0]

    for idx, bbox in enumerate(boxes):
        if scores[idx] > 0.01:
            x1, y1, x2, y2 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])

            x1 *= H
            x2 *= H
            y1 *= W
            y2 *= W

            cv2.rectangle(new_image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 5)
    plt.imshow(new_image)
    plt.show()