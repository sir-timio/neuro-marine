import torch
import typing as ty
import albumentations as A 
import logging
import cv2
import numpy as np
from numpy.typing import NDArray
from inference import Inference
from math import sqrt

logging.basicConfig(filename="stream.log", encoding='utf-8')
OutputCOCO:ty.TypeAlias = ty.Dict[str, str|ty.List[float]|float]

class Processor(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.empty_output:OutputCOCO = {"filename":"",
                                         "id":"",
                                         "bbox":[0.0],
                                         "conf":0.0} 
        self.det_transforms = A.Compose([])
        self.video_extensions:ty.List[str] = ["mp4", "webm", "MOV"]
        self.image_extensions:ty.List[str] = ["png", "jpg", "jpeg"]
        self.inference =  Inference(models = ["fold_0.pt", 
                                              ])

        self.time_plot = []
        self.red_plot = [{"red":0, "silver":0}]

        self.size_plot = [{"min":0, "max":0, "mean":0}]

    def guess_filetye(self, file_name:str) -> int | None:
        '''
        0 - video
        1 - image
        None - unknown
        '''
        for ext in self.video_extensions:
            if ext in file_name or ext.upper():
                return 0
        for ext in self.image_extensions:
            if ext in file_name or ext.upper():
                return 1
        return None
    def get_amount_by_type(self, bboxes):

        bboxes= bboxes.tolist()

        if len(bboxes) == 1:
            return {'red': 0, 'default': 1}

        red = 1
        defolt = len(bboxes) - 1

        return {'red': red, 'silver': defolt}

    def get_sizes(self, bboxes:torch.Tensor) -> ty.Dict[str, float]:
        bboxes= bboxes.tolist()
        sizes = []

        for bbox in bboxes:
            x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
            sizes.append(sqrt(((x2 - x1) / 15)  ** 2 + ((y2 - y1) / 15)  ** 2)) 
        sizes = {'min': min(sizes), 'mean': np.mean(sizes), 'max': max(sizes)}
        
        return sizes

    def _infer_photo(self, img_path:str|NDArray) -> torch.Tensor:
        '''
        SAHI single photo inference
        '''
        bbox = self.inference.infer(img_path)
        #
        return bbox

    def _infer_video(self, file_name:str) -> ty.List[OutputCOCO]:
                                    
        vidcap = cv2.VideoCapture(file_name) # load video from disk
        cur_frame = 0
        success = True
        outputs = []
        while success:
            success, frame = vidcap.read()
            if success:
                #im = self.det_transforms(frame)['image']
                img_frame = np.array(frame)
                frame_output:torch.Tensor = self._infer_photo(img_frame)
                base_out = self.empty_output

                self.time_plot.append(frame_output.size(0))
                self.size_plot.append(self.get_sizes(frame_output))
                self.red_plot.append(self.get_amount_by_type(frame_output))                                                
                id_ = 0
                for bbox in frame_output:
                        
                    base_out['id'] = id_
                    id_ +=1
                    base_out['filename'] = file_name
                    base_out['bbox'] = bbox[:4].to(torch.int64).tolist()
                    base_out['conf'] = bbox[4].item()

                    outputs.append(base_out)
                cur_frame +=1
                logging.warn(frame_output) 
        return outputs
                
    def process(self, input_file_name:str) -> ty.List[OutputCOCO]| None:
        file_type = self.guess_filetye(input_file_name) 
        if file_type is None:
           logging.warn(f"filetype {file_type}")
           return None

        if file_type:
           #img:torch.tensor = self._preprocess_image(input_file_name)
            out:torch.Tensor = self._infer_photo(input_file_name)

            base_out = self.empty_output
            id_ = 0
            for bbox in out:
                    
                base_out['id'] = id_
                id_ +=1
                base_out['filename'] =  input_file_name
                base_out['bbox'] = bbox[:4].to(torch.int64).tolist()
                base_out['filename'] = bbox[4].item()
                logging.warn("inferring photo")
            return [base_out]
        else:
            out:ty.List[OutputCOCO] = self._infer_video(input_file_name)
            logging.warn("inferring video")
            return out

    def forward(self, img_path:str|NDArray) -> int:
        return 1

