from ultralytics import YOLO
import shutil
from datetime import datetime
def train_model():
    """
    Обучение модели YOLOv8.
    """
    model = YOLO("yolov8n.pt")
    results = model.train(data="/app/data/weld_spot.yaml", imgsz=1080, epochs=50, batch=8, name="weld_spot_detection_yolo_v8")
    save_results_to_local()
    return {"training_results": results}
def validation():
    """
    Валидация модели YOLOv8.
    """
    model = YOLO("/app/data/weights/best.pt")
    metrics = model.val()
    return {"metrics": metrics}
def save_results_to_local():
    """
    Сохранение результатов обучения в локальную папку.
    """
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    source_folder = "/app/data/runs"
    destination_folder = f"/app/data/runs_{current_datetime}"
    shutil.copytree(source_folder, destination_folder)