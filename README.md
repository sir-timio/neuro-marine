# World Youth Festival AI hackaton solution

- clone source 
```
git clone https://github.com/sir-timio/WYF2024
```

- install dependecies
```
pip install -r requirements.txt
```

## Backend

- build docker ml backend
```
cd label-studio-yolov8-backend && docker-compose up --build
```

- load weights into label-studio-yolov8-backend/full_size.pt
```
https://drive.google.com/file/d/1-TpgLVsmR34RC0IQtals1wM2nWnsJxcB/view?usp=sharing
```


## Label Studio
- installation
```
pip install -U label-studio
```

- build label studio server
```
LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/path/to/data label-studio
```

## Frontend
- run streamlit application from "pages" parent folder
```
streamlit run main.py
```
