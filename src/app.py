"""
Application
"""

from fastapi import FastAPI
from train import train_model, validation
from inference import run_inference, random_inference_display
from preprocessing import data_download, process_data_folders, create_yaml_file
from typing import Dict
app = FastAPI()

@app.post("/train/")
async def train(data_links: Dict[str, str]):
    """
    Запуск обучения модели YOLOv8.
    """
    # Загрузка данных
    data_download(data_links)
    process_data_folders(data_links, train_percent=70, valid_percent=15)
    create_yaml_file()
    # Обучение модели
    train_model()
    return {"message": "Обучение завершено"}

@app.post("/inference/")
async def inference(image_path: str):
    """
    Запуск инференса модели YOLOv8.
    """
    result = run_inference(image_path)
    return {"result": result}

@app.post("/validation/")
async def validate():
    """
    Запуск валидации модели YOLOv8.
    """
    results = validation()
    return {"validation_results": results}

@app.post("/random_inference/")
async def random_inference(source_folder: str, model_type: str):
    """
    Запуск инференса на случайном изображении.
    """
    result = random_inference_display(source_folder, model_type)
    return {"result": result}

@app.get("/")
def health_check():
    return {"status": "healthy"}