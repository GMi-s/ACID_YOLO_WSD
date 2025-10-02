import os

# Имя файла данных
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
base_folder = '/content'  # Базовая папка для данных
images_folder = os.path.join(base_folder, 'images')  # Папка для изображений
labels_folder = os.path.join(base_folder, 'labels')  # Папка для меток
backup_folder = os.path.join(base_folder, 'backup')  # Папка для резервных копий