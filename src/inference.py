"""
Module: inference.py
Description: 
    This module is used to load the model and make predictions on the test data.
"""

from ultralytics import YOLO
from PIL import Image, ImageDraw
from utils import read_annotation
import os
import random
def run_inference(image_path: str) -> dict:
    """
    Запуск инференса модели YOLOv8 на изображении.
    """
    model = YOLO("/app/data/weights/best.pt")
    results = model.predict(image_path)
    return {"predictions": results}
def random_image_name(source_folder: str):
    """
    Выбор случайного изображения из указанной папки.
    """
    folder_path = f'/app/data/images/{source_folder}'
    files_list = os.listdir(folder_path)
    image_files = [f for f in files_list if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    random_image = random.choice(image_files)
    image_file = f'/app/data/images/{source_folder}/{random_image}'
    frame_number = random_image.split('/')[-1].split('.')[0]
    label_file = f'/app/data/labels/{source_folder}/{frame_number}.txt'
    return image_file, label_file
def random_inference_display(source_folder: str, model_type: str):
    """
    Запуск инференса на случайном изображении.
    """
    image_file, label_file = random_image_name(source_folder)
    model_path = "/app/data/weights/best.pt" if model_type == "last_trained_model" else "/app/data/model_weights.pt"
    model = YOLO(model_path)
    source = Image.open(image_file)
    results = model.predict(source)
    bounding_boxes = read_annotation(label_file)
    for i, r in enumerate(results):
        im_bgr = r.plot()
        im_rgb = Image.fromarray(im_bgr[..., ::-1])
        draw = ImageDraw.Draw(im_rgb)
        for box in bounding_boxes:
            left = int((box[1] - box[3] / 2) * im_bgr.shape[1])
            top = int((box[2] - box[4] / 2) * im_bgr.shape[0])
            right = int((box[1] + box[3] / 2) * im_bgr.shape[1])
            bottom = int((box[2] + box[4] / 2) * im_bgr.shape[0])
            draw.rectangle([left, top, right, bottom], outline=(0, 255, 0), width=6)
    return {"image_file": image_file, "label_file": label_file}