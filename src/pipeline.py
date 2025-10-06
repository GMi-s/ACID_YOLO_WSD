"""
Main pipeline for the project
"""

from preprocessing import data_download, split_data
from sample_img_show import img_show
from train import train_model
from inference import random_inference_display  # Импорт функции инференса
from config import INFERENCE_MODEL_TYPE  # Импорт параметра типа модели для инференса

def main():
    """
    Основная функция для последовательного выполнения задач:
    1. Загрузка данных.
    2. Разделение данных на обучающую, валидационную и тестовую выборки.
    3. Отображение случайных изображений с bounding boxes.
    4. Обучение модели.
    5. Инференс и сохранение случайного размеченного кадра.
    """

    # Шаг 1: Загрузка данных
    print("Загрузка данных...")
    data_download()
    print("Загрузка данных завершена.")

    # Шаг 2: Отображение случайных изображений
    print("Отображение случайных изображений c bounding boxes...")
    img_show()
    print("Отображение завершено.")

    # Шаг 3: Разделение данных
    split_data()

    # Шаг 4: Обучение модели
    print("Обучение модели...")
    train_model()
    print("Обучение завершено.")

    # Шаг 5: Инференс и сохранение случайного размеченного кадра
    print("Запуск инференса...")
    random_inference_display('test', INFERENCE_MODEL_TYPE)
    print("Инференс завершён. Результаты сохранены в папке inference_image.")

# Вызов основной функции при запуске скрипта
if __name__ == "__main__":
    main()