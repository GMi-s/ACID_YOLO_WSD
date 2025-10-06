import subprocess
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse  # Добавлен импорт FileResponse
from pathlib import Path

app = FastAPI()

# Пути к папкам и файлам
base_folder = Path(__file__).resolve().parent
inference_image_folder = base_folder / "inference_image"

@app.post("/start-pipeline")
def start_pipeline():
    """
    Запускает pipeline.py и возвращает результаты выполнения.
    """
    try:
        # Запуск pipeline.py
        result = subprocess.run(["python3", "pipeline.py"], capture_output=True, text=True)
        
        # Проверка успешности выполнения
        if result.returncode != 0:
            return JSONResponse(
                status_code=500,
                content={"error": "Ошибка выполнения pipeline.py", "details": result.stderr}
            )
        
        # Поиск последнего сохраненного изображения
        inference_images = list(inference_image_folder.glob("*.png"))
        if not inference_images:
            return JSONResponse(
                status_code=404,
                content={"error": "Изображение с разметкой не найдено"}
            )
        
        # Получение последнего изображения
        latest_image = max(inference_images, key=lambda f: f.stat().st_mtime)
        
        # Формирование URL для изображения
        image_url = f"/inference-image/{latest_image.name}"
        
        # Чтение логов обучения
        train_log_file = base_folder / "train.log"
        train_log = ""
        if train_log_file.exists():
            with open(train_log_file, "r", encoding="utf-8") as f:
                train_log = f.read()
        
        # Возврат результата
        return JSONResponse(
            status_code=200,
            content={
                "message": "Pipeline успешно выполнен",
                "image_url": image_url,
                "train_log": train_log
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Неизвестная ошибка", "details": str(e)}
        )

@app.get("/inference-image/{image_name}")
def get_inference_image(image_name: str):
    """
    Возвращает изображение с разметкой.
    """
    image_path = inference_image_folder / image_name
    if not image_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "Изображение не найдено"}
        )
    return FileResponse(image_path)  # Использование FileResponse

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)