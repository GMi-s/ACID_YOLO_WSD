"""
Main pipeline for the project
"""

#import os
#import shutil
#from typing import Dict
from preprocessing import data_download, read_items_list

def run_pipeline():
    """
    Основной пайплайн для обработки данных и подготовки к обучению.
    """
    # Шаг 1: Загрузка данных
    print("Запуск pipeline...")
    data_download()
    

    # Шаг 2: Чтение данных из файлов
    data_name = 'train.txt'  # Имя файла для чтения
    data_storage = read_items_list(data_name)  # Создание списка data_storage

    # Шаг 3: Вывод результатов (для проверки)
    print("Список успешно создан:")
    for key, value in data_storage.items():
        print(f"{key}: {value}")

    print("Pipeline завершен.")

# Основная программа
if __name__ == "__main__":
    run_pipeline()
