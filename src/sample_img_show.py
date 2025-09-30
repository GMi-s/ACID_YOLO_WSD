import os
import cv2
import random
import matplotlib.pyplot as plt
import shutil
import numpy as np
from config import data_name, stored_data  # Импорт переменных из config.py

# Функция для получения папки на один уровень выше текущей директории
def get_parent_dir():
    return os.path.dirname(os.getcwd())

# Функция для очистки папки
def clear_folder(folder_path):
    """
    Удаляет всё содержимое папки. Если папки не существует, создаёт её.
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

# Функция для чтения *.txt data:
def reading_data(folder, content):
    """
    Чтение данных из текстового файла.
    Args:
        folder (str): Название папки внутри `sample_data`.
        content (str): Название файла (например, "file.txt").
    Returns:
        np.array: Массив строк из файла.
    """
    # Получаем путь к папке sample_data на один уровень выше текущей директории
    base_dir = os.path.dirname(os.getcwd())  # Переход на один уровень выше
    file_path = os.path.join(base_dir, "sample_data", folder, content)  # Формируем путь к файлу
    # Чтение файла
    with open(file_path, 'r') as file:
        file_content = file.readlines()  # Чтение строк из файла
        file_content = [line.strip() for line in file_content]  # Удаляем символы новой строки
    return np.array(file_content)

# Функция для создания списка из Data Sets:
def read_items_list():
    """
    Чтение списка элементов из файлов в папках dataset.
    Returns:
        dict: Словарь, где ключи — имена папок, а значения — массивы строк из файлов.
    """
    data_storage = {}  # Словарь для хранения данных
    for key in stored_data:
        photo_item = reading_data(key, data_name)  # Чтение файла с использованием функции reading_data
        data_storage[key] = photo_item  # Сохранение данных в словарь
    return data_storage

# Функция чтения информации из текстовых файлов
def read_annotation(annotation_path: str):
    """
    Чтение аннотаций из файла TXT.
    """
    with open(annotation_path, "r") as file:
        lines = file.readlines()
    bounding_boxes = []
    for line in lines:
        parts = line.strip().split(" ")
        class_id = int(parts[0])
        x, y, w, h = map(float, parts[1:])
        bounding_boxes.append((class_id, x, y, w, h))
    return bounding_boxes

# Функция отрисовки bounding boxes
def draw_bounding_boxes(image_path, bounding_boxes, output_path="output.jpg"):
    """
    Отрисовка bounding boxes на изображении и сохранение результата.
    """
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    for box in bounding_boxes:
        class_id, x, y, w, h = box
        left = int((x - w / 2) * image.shape[1])
        top = int((y - h / 2) * image.shape[0])
        right = int((x + w / 2) * image.shape[1])
        bottom = int((y + h / 2) * image.shape[0])
        color = (0, 255, 0)  # Зелёный цвет
        thickness = 6  # Толщина линии
        cv2.rectangle(image, (left, top), (right, bottom), color, thickness)
    plt.figure(figsize=(8, 8))
    plt.imshow(image)
    plt.axis('off')
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Изображение сохранено как {output_path}")

# Функция для отображения изображения с Bounding Boxes
def img_show():
    """
    Отображение случайного изображения с bounding boxes и сохранение результата.
    """
    # Получаем путь к папке на один уровень выше текущей директории
    base_dir = get_parent_dir()
    # Путь к папке для сохранения изображений
    output_folder = os.path.join(base_dir, "sample_image")
    clear_folder(output_folder)
    # Формируем data_storage на основе входных данных
    data_storage = read_items_list()
    for key in data_storage.keys():
        random_file_name = random.choice(list(data_storage[key]))
        frame_number = random_file_name.split('/')[-1].split('.')[0]
        print(f'Случайный кадр: {random_file_name}')
        # Пути к файлам (относительные пути)
        image_path = os.path.join(base_dir, "sample_data", key, "images", f"{frame_number}.jpg")
        annotation_path = os.path.join(base_dir, "sample_data", key, "obj_train_data", f"{frame_number}.txt")
        # Проверка существования файлов
        if os.path.exists(image_path) and os.path.exists(annotation_path):
            # Чтение аннотаций
            bounding_boxes = read_annotation(annotation_path)
            # Итерирование и вывод координат Bounding Boxes
            #for box in bounding_boxes:
                #print("Class ID:", box[0]) #Вывод класса bounding boxes
                #print("x, y, w, h:", box[1:]) #Вывод координат bounding boxes
                #print()  # Пустая строка для разделения групп координат
            # Сохранение изображения с bounding boxes
            output_path = os.path.join(output_folder, f"{frame_number}.jpg")
            draw_bounding_boxes(image_path, bounding_boxes, output_path)
        else:
            print(f"Файл по пути {image_path} не найден или отсутствует файл аннотации.")

# Вызов функции при запуске скрипта
if __name__ == "__main__":
    # Вызов функции
    img_show()