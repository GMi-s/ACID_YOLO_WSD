import os
import shutil
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
from config import NUM_EPOCHS, BATCH_SIZE, IMG_SIZE, MODEL_NAME, MAX_RETRIES

# Динамические пути
BASE_PATH = Path(__file__).parent.parent  # Корневая директория проекта
IMAGES_PATH = BASE_PATH / "images"  # Папка с изображениями
MODELS_PATH = BASE_PATH / "models"  # Папка для сохранения моделей
RUNS_PATH = BASE_PATH / "runs" / "detect"  # Папка для временных результатов обучения

# Создание директорий, если они не существуют
os.makedirs(MODELS_PATH, exist_ok=True)
os.makedirs(RUNS_PATH, exist_ok=True)

# Путь к файлу конфигурации YAML (создаётся в корневой директории проекта)
YAML_FILE = BASE_PATH / "weld_spot.yaml"

# Создание данных для файла weld_spot.yaml
data = f"""
path: {IMAGES_PATH}
train: {IMAGES_PATH / "train"}
val: {IMAGES_PATH / "valid"}
names:
  0: 'WS'
"""

# Запись данных в файл weld_spot.yaml
with open(YAML_FILE, "w") as file:
    file.write(data)

print(f"Файл {YAML_FILE} успешно создан с требуемым содержимым.")

# Функция для поиска последней папки с результатами
def get_latest_folder(base_path):
    folder_list = [folder for folder in os.listdir(base_path) if folder.startswith('weld_spot_detection_yolo_v')]
    if folder_list:
        latest_folder = max(folder_list, key=lambda x: int(x.split('v')[-1]) if x.split('v')[-1].isdigit() else -1)
        return os.path.join(base_path, latest_folder)
    return None

# Функция для поиска последних весов модели
def get_latest_weights(latest_folder):
    if latest_folder:
        weights_path = os.path.join(latest_folder, 'weights', 'best.pt')
        if os.path.exists(weights_path):
            return weights_path
    return None

# Функция для сохранения результатов обучения
def save_results_to_folder(source_path, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    # Копирование файлов
    for root, dirs, files in os.walk(source_path):
        for file in files:
            shutil.copy(os.path.join(root, file), destination_folder)
    print(f"Результаты обучения сохранены в {destination_folder}")

# Функция для обучения модели
def train_model(model_source=None):
    if model_source is None:
        model_source = 'yolov8n.pt'  # Используйте стандартные веса, если свои отсутствуют
    model = YOLO(model_source)
    results = model.train(
        data=str(YAML_FILE),
        imgsz=IMG_SIZE,
        epochs=NUM_EPOCHS,
        batch=BATCH_SIZE,
        name=MODEL_NAME,
    )
    return model, results

# Функция для валидации модели
def validate_model(model_source):
    if not os.path.exists(model_source):
        raise FileNotFoundError(f"Файл модели не найден: {model_source}")
    model = YOLO(model_source)
    metrics = model.val()  # Валидация модели
    return {
        'map50': metrics.box.map50,  # mAP50
        'map50_95': metrics.box.map,  # mAP50-95
    }

# Основная функция для обучения и валидации
def train_and_validate():
    best_metrics = None
    best_model_path = None

    # Поиск последней папки с результатами
    latest_folder = get_latest_folder(RUNS_PATH)
    latest_weights = get_latest_weights(latest_folder)

    if latest_weights:
        # Валидация последней модели
        latest_metrics = validate_model(latest_weights)
    else:
        # Использование модели по умолчанию, если нет сохранённых результатов
        latest_weights = 'yolov8n.pt'
        latest_metrics = {'map50': 0, 'map50_95': 0}

    for attempt in range(MAX_RETRIES):
        print(f"Попытка обучения {attempt + 1} из {MAX_RETRIES}")

        # Обучение модели
        model, results = train_model(latest_weights)

        # Определение пути к текущим весам
        latest_folder = get_latest_folder(RUNS_PATH)
        current_weights = get_latest_weights(latest_folder)

        if current_weights:
            # Валидация текущей модели
            current_metrics = validate_model(current_weights)

            # Проверка метрик
            if best_metrics is None or current_metrics['map50'] > latest_metrics['map50']:
                best_metrics = current_metrics
                best_model_path = current_weights

                # Сохранение результатов, если текущая модель лучше
                save_results_to_folder(
                    latest_folder,
                    os.path.join(MODELS_PATH, f'runs_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
                )
                print(f"Новые лучшие метрики: mAP50-95 = {current_metrics['map50_95']}, mAP50 = {current_metrics['map50']}")
            else:
                print(f"Метрики ухудшились. Возврат к предыдущим весам.")
                if best_model_path:
                    shutil.copy(best_model_path, MODELS_PATH / "best.pt")
                    break
        else:
            print("Ошибка: Веса модели не найдены после обучения.")
            break

    print("Обучение завершено.")

# Вызов основной функции
if __name__ == "__main__":
    train_and_validate()