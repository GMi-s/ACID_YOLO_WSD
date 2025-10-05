import os

# Имя файла данных из разметки в Data Set
data_name = 'train.txt'

# Словарь с данными наборов
stored_data = {
    'Weld_Spot-Large_Scale': 'https://disk.yandex.ru/d/pSGMq59oD9--2w',
    'Weld_Spot-No_Spots': 'https://disk.yandex.ru/d/wWZxC-eFLeMtPQ',
    'Weld_Spot-Small_Scale': 'https://disk.yandex.ru/d/CX0NKNqOKKUGOA'
}

# Проценты для разбиения данных
train_percent = 70  # Процент обучающей выборки
valid_percent = 15  # Процент валидационной выборки
test_percent = 15   # Процент тестовой выборки (вычисляется как 100 - train_percent - valid_percent)

# Папки для хранения данных
base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Базовая папка для данных
images_folder = os.path.join(base_folder, 'images')  # Папка для изображений
labels_folder = os.path.join(base_folder, 'labels')  # Папка для меток
models_folder = os.path.join(base_folder, 'models')  # Папка для моделей
inference_image_folder = os.path.join(base_folder, 'inference_image')  # Папка для изображений инференса
backup_folder = os.path.join(base_folder, 'backup')  # Папка для резервных копий

# Гиперпараметры для YOLO v8
NUM_EPOCHS = 50
BATCH_SIZE = 4  # Уменьшенный размер батча
IMG_SIZE = 640  # Уменьшенный размер изображения
NUM_WORKERS = 4  # Уменьшенное количество рабочих процессов
MODEL_NAME = 'weld_spot_detection_yolo_v8'
MAX_RETRIES = 3

# Параметры инференса
INFERENCE_MODEL_TYPE = 'last_trained_model'  # Тип модели для инференса ('last_trained_model' или 'default_model')
INFERENCE_DEVICE = 'cpu'  # Устройство для инференса ('cuda' или 'cpu')
INFERENCE_BATCH_SIZE = 1  # Размер батча для инференса
INFERENCE_IMAGE_SIZE = (640, 640)  # Размер изображения для инференса