import os
import random
import shutil
from PIL import Image as PILImage, ImageDraw
from ultralytics import YOLO
from config import (
    images_folder,
    labels_folder,
    models_folder,
    inference_image_folder,
    INFERENCE_MODEL_TYPE,
    INFERENCE_DEVICE,
    INFERENCE_BATCH_SIZE,
    INFERENCE_IMAGE_SIZE
)

# Функция для поиска последней папки с результатами
def get_latest_folder(base_path):
    folder_list = [folder for folder in os.listdir(base_path) if folder.startswith('runs_')]
    if folder_list:
        latest_folder = max(folder_list)
        return os.path.join(base_path, latest_folder)
    return None

# Функция для поиска последних весов модели
def get_latest_weights(latest_folder):
    if latest_folder:
        weights_path = os.path.join(latest_folder, 'best.pt')
        if os.path.exists(weights_path):
            return weights_path
    return None

# Функция для выбора рандомного кадра для проведения инференса
def random_image_name(source_folder):
    folder_path = os.path.join(images_folder, source_folder)
    if not os.path.exists(folder_path):
        return "Указанная папка не существует"
    
    files_list = os.listdir(folder_path)
    image_files = [f for f in files_list if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    if len(image_files) == 0:
        return "В папке нет изображений"
    
    random_image = random.choice(image_files)
    image_file = os.path.join(folder_path, random_image)
    frame_number = random_image.split('/')[-1].split('.')[0]
    label_file = os.path.join(labels_folder, source_folder, f'{frame_number}.txt')
    
    print(f'Random frame: {image_file}')
    return image_file, label_file

# Функция для инференса YOLO моделью
def predict_and_display(image_file, label_file, model_type):
    try:
        # Определение путей к моделям
        if model_type == 'last_trained_model':
            latest_folder = get_latest_folder(models_folder)
            model_path = get_latest_weights(latest_folder)
            if not model_path:
                raise FileNotFoundError("Не удалось найти последние веса модели.")
        elif model_type == 'default_model':
            model_path = os.path.join(models_folder, 'model_weights.pt')
        else:
            raise ValueError("Invalid model_type. Please choose either 'last_trained_model' or 'default_model'.")
        
        # Загрузка модели YOLO
        model = YOLO(model_path)
        
        # Открытие изображения
        source = PILImage.open(image_file)
        
        # Если INFERENCE_IMAGE_SIZE задан в config.py, изменяем размер изображения
        if INFERENCE_IMAGE_SIZE:
            source = source.resize(INFERENCE_IMAGE_SIZE)
        
        # Предсказание bounding boxes
        results = model.predict(source, batch=INFERENCE_BATCH_SIZE, device=INFERENCE_DEVICE)
        
        # Чтение разметки для изображения
        bounding_boxes = read_annotation(label_file)
        
        # Подсчет количества размеченных областей в Bounding Boxes
        num_label_boxes = len(bounding_boxes)
        
        # Подсчет количества размеченных областей в results
        num_predicted_boxes = sum([len(r) for r in results])
        print(f"Общее количество сварочных точек, размеченных вручную: {num_label_boxes}")
        print(f"Общее количество сварочных точек, определённых моделью: {num_predicted_boxes}")
        
        # Визуализация результатов с bounding boxes
        for i, r in enumerate(results):
            im_bgr = r.plot()  # Возвращает массив numpy в порядке BGR
            im_rgb = PILImage.fromarray(im_bgr[..., ::-1])  # Преобразование к формату RGB
            
            for box in bounding_boxes:
                class_id, x, y, w, h = box
                left = int((x - w / 2) * im_bgr.shape[1])
                top = int((y - h / 2) * im_bgr.shape[0])
                right = int((x + w / 2) * im_bgr.shape[1])
                bottom = int((y + h / 2) * im_bgr.shape[0])
                color = (0, 255, 0)  # Цвет Bounding Box (зелёный в данном случае)
                thickness = 6  # Толщина линии
                draw = ImageDraw.Draw(im_rgb)
                draw.rectangle([left, top, right, bottom], outline=color, width=thickness)
            
            # Сохранение изображения в папку inference_image
            inference_image_path = os.path.join(inference_image_folder, f'inference_result_{i}.png')
            im_rgb.save(inference_image_path)
            print(f"Изображение сохранено: {inference_image_path}")
    
    except Exception as e:
        print(f"Ошибка при выполнении инференса: {e}")

# Функция для инференса YOLO моделью рандомного кадра из тестовой выборки
def random_inference_display(source_folder, model_type):
    # Проверка и очистка папки inference_image
    if not os.path.exists(inference_image_folder):
        os.makedirs(inference_image_folder)
    else:
        shutil.rmtree(inference_image_folder)
        os.makedirs(inference_image_folder)
    
    # Выбор рандомного изображения и выполнение инференса
    image_file, label_file = random_image_name(source_folder)
    predict_and_display(image_file, label_file, model_type)

# Вспомогательная функция для чтения аннотаций
def read_annotation(label_file):
    bounding_boxes = []
    with open(label_file, 'r') as file:
        for line in file.readlines():
            class_id, x, y, w, h = map(float, line.strip().split())
            bounding_boxes.append((int(class_id), x, y, w, h))
    return bounding_boxes

# Пример вызова функции для инференса
if __name__ == "__main__":
    random_inference_display('test', INFERENCE_MODEL_TYPE)