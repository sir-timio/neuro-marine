# World Youth Festival AI hackaton solution

## Clone source
```
git clone https://github.com/sir-timio/WYF2024
```

### install dependecies
```
pip install -r requirements.txt
```

## Backend
### place yolo weights into label-studio-yolov8-backend
```
cp *.pt label-studio-yolov8-backend/weights
```

### build docker ml backend
```
cd label-studio-yolov8-backend && docker-compose up --build
```

## Label Studio
### install 
```
pip install -U label-studio
```

### build label studio server
```
LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/path/to/data label-studio
```