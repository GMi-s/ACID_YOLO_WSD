import os
import shutil
import requests
import zipfile
import time
import random
from config import stored_data, train_percent, valid_percent, test_percent  # Импорт переменных из config.py

# Функция для скачивания и распаковки файла
def data_set_download(link, file_name):
    # Генерация новой ссылки через https://getfile.dokpub.com/yandex/get/
    new_download_link = f'https://getfile.dokpub.com/yandex/get/{link}'    
    # Полный путь к скачанному файлу (в текущей рабочей директории)
    file_path = f"{file_name}.zip"
    # Полный путь к папке для распаковки (на один уровень выше директории src)
    base_dir = os.path.dirname(os.getcwd())  # Переход на один уровень выше
    target_folder = os.path.join(base_dir, "sample_data", file_name)  # Формируем папку sample_data/target_folder
    os.makedirs(target_folder, exist_ok=True)  # Создаем папку, если её нет
    # Удаляем существующие файлы или папки
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)
    # Попытка загрузки файла с повтором
    max_retries = 3
    retry_delay = 5  # Задержка между попытками в секундах
    for attempt in range(max_retries):
        try:
            print(f"Загрузка файла (попытка {attempt + 1} из {max_retries})...")
            response = requests.get(new_download_link, stream=True, timeout=30)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Файл {file_path} успешно загружен.")
                break  # Выход из цикла при успешной загрузке
            else:
                print(f"Ошибка загрузки файла. Код ошибки: {response.status_code}")
        except (requests.exceptions.RequestException, ConnectionResetError) as e:
            print(f"Ошибка соединения: {e}. Повторная попытка через {retry_delay} секунд...")
            time.sleep(retry_delay)
    else:
        print(f"Не удалось загрузить файл после {max_retries} попыток.")
        return
    # Распаковка архива в sample_data/target_folder
    print("Распаковка архива...")
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # Получаем список всех элементов в архиве
        members = zip_ref.namelist()
        # Проверяем, есть ли папка верхнего уровня с именем file_name
        top_level_folder = f"{file_name}/"
        if all(member.startswith(top_level_folder) for member in members):
            # Если в архиве есть папка верхнего уровня с именем file_name,
            # извлекаем содержимое этой папки напрямую в target_folder
            for member in members:
                relative_path = member[len(top_level_folder):]  # Убираем папку верхнего уровня из пути
                if relative_path:  # Если путь не пустой
                    zip_ref.extract(member, target_folder)
                    # Перемещаем файл на нужный уровень
                    src_path = os.path.join(target_folder, member)
                    dst_path = os.path.join(target_folder, relative_path)
                    os.rename(src_path, dst_path)
            # Удаляем пустую папку верхнего уровня
            shutil.rmtree(os.path.join(target_folder, top_level_folder.strip('/')))
        else:
            # Если нет папки верхнего уровня, извлекаем всё как обычно
            zip_ref.extractall(target_folder)
    print(f"Файлы успешно извлечены в папку: {target_folder}")

# Функция для удаления скачанных .zip - архивов
def delete_downloaded_archives(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".zip"):  # Проверка на тип файла - архив
            file_path = os.path.join(directory, filename)  # Получаем путь
            os.remove(file_path)  # Удаляем файл
            print(f"Deleted {file_path} to free up space.")

# Загрузка DataSet
def data_download():
    for key in stored_data:
        data_set_download(stored_data[key], key)
    # Удаление архивов из текущего рабочего каталога
    delete_downloaded_archives(os.getcwd())

# Функция удаления и создания обучающей, валидационной и тестовой папок
def folders_refresh(dest_train_folder, dest_valid_folder, dest_test_folder):
    """
    Удаляет и создаёт папки для обучающей, валидационной и тестовой выборки.
    Args:
        dest_train_folder (str): Путь к папке для обучающей выборки.
        dest_valid_folder (str): Путь к папке для валидационной выборки.
        dest_test_folder (str): Путь к папке для тестовой выборки.
    """
    for folder in [dest_train_folder, dest_valid_folder, dest_test_folder]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

# Функция для перемещения данных в обучающую, валидационную и тестовую папки
def move_and_clean_folders(src_folder, dest_train_folder, dest_valid_folder, dest_test_folder):
    """
    Перемещает данные из исходной папки в обучающую, валидационную и тестовую папки.
    Args:
        src_folder (str): Путь к исходной папке с данными.
        dest_train_folder (str): Путь к папке для обучающей выборки.
        dest_valid_folder (str): Путь к папке для валидационной выборки.
        dest_test_folder (str): Путь к папке для тестовой выборки.
    """
    try:
        if not os.path.isdir(src_folder):
            raise FileNotFoundError(f"Папка {src_folder} не найдена.")
        # Проверка наличия папки obj_train_data внутри src_folder
        if not os.path.isdir(os.path.join(src_folder, 'obj_train_data')):
            # Копирование содержимого папки images в папку obj_train_data
            shutil.copytree(os.path.join(src_folder, 'images'), os.path.join(src_folder, 'obj_train_data'))
        # Обработка файлов в папке obj_train_data
        src_train_folder = os.path.join(src_folder, 'obj_train_data')
        for f in os.listdir(src_train_folder):
            file_path = os.path.join(src_train_folder, f)
            if os.path.isfile(file_path):
                # Распределение файлов по выборкам
                rand_num = random.randint(1, 100)
                if rand_num <= train_percent:
                    shutil.copy(file_path, dest_train_folder)
                elif rand_num <= train_percent + valid_percent:
                    shutil.copy(file_path, dest_valid_folder)
                else:
                    shutil.copy(file_path, dest_test_folder)
        # Удаление исходной папки obj_train_data
        shutil.rmtree(src_train_folder)
    except Exception as e:
        print(f"Ошибка: {e}")

# Функция для обработки всех папок из словаря
def process_data_folders():
    """
    Обрабатывает все папки из словаря stored_data, разделяя данные на обучающую, валидационную и тестовую выборки.
    """
    # Получаем путь к папке на один уровень выше текущей директории
    base_dir = os.path.dirname(os.getcwd())
    # Пути к папкам для обучающей, валидационной и тестовой выборок
    dest_train_folder = os.path.join(base_dir, 'obj_train_data')
    dest_valid_folder = os.path.join(base_dir, 'obj_valid_data')
    dest_test_folder = os.path.join(base_dir, 'obj_test_data')
    # Обновление папок
    folders_refresh(dest_train_folder, dest_valid_folder, dest_test_folder)
    # Обработка каждой папки из словаря stored_data
    for folder in stored_data.keys():
        src_folder = os.path.join(base_dir, 'sample_data', folder)
        move_and_clean_folders(src_folder, dest_train_folder, dest_valid_folder, dest_test_folder)

# Функция для создания списков файлов обучающей, валидационной и тестовой выборки
def create_split_files(base_folder):
    """
    Создает списки файлов для обучающей, валидационной и тестовой выборки.
    Args:
        base_folder (str): Базовая директория, где находятся папки с данными.
    """
    for split in ['train', 'valid', 'test']:
        split_file_path = os.path.join(base_folder, f"{split}.txt")
        split_folder_path = os.path.join(base_folder, f"obj_{split}_data")
        
        with open(split_file_path, 'w') as file:
            for root, dirs, files in os.walk(split_folder_path):
                for file_name in files:
                    if file_name.endswith('.txt'):
                        file_name = f'/content/images/{file_name[:-4]}.jpg'
                    file.write(file_name + '\n')

# Функция для перемещения файлов в соответствии со списком файлов, содержащих текущие адреса расположения
def move_files_update_paths_for_files(file_list):
    """
    Перемещает файлы из папки images в соответствующие подпапки train/valid/test и обновляет пути в файлах.
    Args:
        file_list (list): Список файлов (train.txt, valid.txt, test.txt), содержащих пути к файлам.
    """
    base_dir = os.path.dirname(os.getcwd())  # Получаем базовый путь на один уровень выше текущей директории
    images_folder = os.path.join(base_dir, 'images')  # Общая папка images

    for file_path in file_list:
        file_path = os.path.join(base_dir, os.path.basename(file_path))  # Полный путь к файлу
        if not os.path.exists(file_path):
            print(f"Файл {file_path} не найден.")
            continue

        # Определяем целевую папку в зависимости от имени файла
        target_folder_name = os.path.splitext(os.path.basename(file_path))[0]  # train, valid или test
        target_folder = os.path.join(images_folder, target_folder_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Чтение путей из файла
        with open(file_path, 'r') as file:
            paths = file.readlines()
            paths = [path.strip() for path in paths]

        # Перемещение файлов и обновление путей
        with open(file_path, 'w') as file:
            for path in paths:
                file_name = os.path.basename(path)  # Имя файла из пути
                src_path = os.path.join(images_folder, file_name)  # Полный путь к файлу в images
                dst_path = os.path.join(target_folder, file_name)  # Полный путь к файлу в целевой папке

                if os.path.exists(src_path):
                    # Перемещение файла
                    shutil.move(src_path, dst_path)
                    # Запись обновленного пути в файл
                    file.write(dst_path + '\n')
                    #print(f"Файл {file_name} перемещен из {src_path} в {dst_path}.")
                else:
                    print(f"Файл {src_path} не найден, пропуск.")

        print(f"Файлы из {file_path} успешно перемещены в папку {target_folder}, и пути обновлены в файле {os.path.basename(file_path)}.")

# Функция для перемещения файлов в общую папку
def move_images_to_common_folder(data_dict):
    """
Перемещает файлы из выбранных папок в новую общую папку.
Args:
data_dict (dict): Словарь с ключами, соответствующими именам папок.
 """
    # Определяем путь к общей папке images
    base_dir = os.path.dirname(os.getcwd())
    destination_folder = os.path.join(base_dir, 'images')

    # Создаем папку images, если она не существует
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Переменная для отслеживания наличия папок images в исходных папках
    images_folders_exist = any(os.path.exists(os.path.join(base_dir, 'sample_data', key, 'images')) for key in data_dict)

    if not images_folders_exist and os.path.exists(destination_folder):
        # Если папки images не найдены и папка destination_folder существует,
        # загружаем данные заново
        data_download()
        images_folders_exist = any(os.path.exists(os.path.join(base_dir, 'sample_data', key, 'images')) for key in data_dict)

    if images_folders_exist:
        # Перемещаем файлы из папок images в общую папку
        for key in data_dict:
            folder_path = os.path.join(base_dir, 'sample_data', key, 'images')
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        # Проверяем, существует ли файл в целевой папке
                        dst_file_path = os.path.join(destination_folder, filename)
                        if os.path.exists(dst_file_path):
                            # Если файл уже существует, удаляем его перед перемещением
                            os.remove(dst_file_path)
                        shutil.move(file_path, destination_folder)

                # Удаление папки images после перемещения файлов
                shutil.rmtree(folder_path)

# Функция для сравнения файлов obj и перемещения в главную папку при совпадении
def read_files_from_folders(data_dict):
    """
Сравнивает файлы obj.data и obj.names из разных папок и перемещает их в главную папку при совпадении.

Args:
data_dict (dict): Словарь с ключами, соответствующими именам папок.
 """
    # Получаем базовый путь на один уровень выше текущей директории
    base_dir = os.path.dirname(os.getcwd())
    data_equal = False
    names_equal = False

    # Проверка наличия файлов obj.data и obj.names в каждой папке
    for key in data_dict:
        source_folder_path = os.path.join(base_dir, 'sample_data', key)
        objdata_file = os.path.join(source_folder_path, 'obj.data')
        objnames_file = os.path.join(source_folder_path, 'obj.names')

        if not os.path.exists(objdata_file) or not os.path.exists(objnames_file):
            # Если файлы отсутствуют, загружаем данные заново
            data_download()
            # Проверяем наличие файлов после загрузки
            if not os.path.exists(objdata_file) or not os.path.exists(objnames_file):
                print(f"Папка {source_folder_path} не обнаружена после загрузки с помощью data_download()")

    # Создаем словарь для хранения содержимого файлов
    all_files_data = {}

    for key, value in data_dict.items():
        folder_path = os.path.join(base_dir, 'sample_data', key)
        file_data = {}

        # Чтение содержимого файлов
        file_data['obj.data'] = open(os.path.join(folder_path, 'obj.data')).read()
        file_data['obj.names'] = open(os.path.join(folder_path, 'obj.names')).read()
        all_files_data[key] = file_data

    # Проверка содержимого файлов obj.data
    for k1, v1 in all_files_data.items():
        for k2, v2 in all_files_data.items():
            if k1 != k2 and v1['obj.data'] != v2['obj.data']:
                print(f"Содержимое файлов obj.data в папках {k1} и {k2} отличается")
                data_equal = False
            else:
                data_equal = True

    # Проверка содержимого файлов obj.names
    for k1, v1 in all_files_data.items():
        for k2, v2 in all_files_data.items():
            if k1 != k2 and v1['obj.names'] != v2['obj.names']:
                print(f"Содержимое файлов obj.names в папках {k1} и {k2} отличается")
                names_equal = False
            else:
                names_equal = True

    if data_equal and names_equal:  # Если содержимое файлов obj.data и obj.names эквивалентно между папками
        # Создание файла obj.data в основной папке
        with open(os.path.join(base_dir, 'obj.data'), 'w') as d:
            d.write("classes = 1\n")
            d.write(f"train = {os.path.join(base_dir, 'train.txt')}\n")
            d.write(f"names = {os.path.join(base_dir, 'obj.names')}\n")
            d.write(f"backup = {os.path.join(base_dir, 'backup')}/\n")
        print("Файл obj.data успешно создан")

        # Создание файла obj.names в основной папке
        with open(os.path.join(base_dir, 'sample_data', key, 'obj.names'), "r") as file:
            file_contents = file.read()

        with open(os.path.join(base_dir, 'obj.names'), 'w') as n:
            n.write(file_contents)
        print("Файл obj.names успешно created")

        # Создание папки backup
        backup_path = os.path.join(base_dir, 'backup')
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        else:
            shutil.rmtree(backup_path)
            os.makedirs(backup_path)

        # Удаление файлов obj.data и obj.names из исходных папок
        for key in data_dict:
            os.remove(os.path.join(base_dir, 'sample_data', key, 'obj.data'))
            os.remove(os.path.join(base_dir, 'sample_data', key, 'obj.names'))

    return all_files_data

# Функция для создания папки labels и перемещения train, valid, test папок
def move_and_rename_folders():
    base_dir = os.path.dirname(os.getcwd())
    labels_folder = os.path.join(base_dir, 'labels')

    # Проверка на пустоту папки labels
    if os.path.exists(labels_folder) and os.path.isdir(labels_folder):
        if os.listdir(labels_folder):
            for item in os.listdir(labels_folder):
                item_path = os.path.join(labels_folder, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

    if not os.path.exists(labels_folder):
        os.makedirs(labels_folder)

    # Перемещение и переименование папок
    folders = [
        os.path.join(base_dir, 'obj_test_data'),
        os.path.join(base_dir, 'obj_train_data'),
        os.path.join(base_dir, 'obj_valid_data')
    ]
    new_names = ['test', 'train', 'valid']

    for index, folder_path in enumerate(folders):
        target_folder = os.path.join(labels_folder, new_names[index])
        if os.path.exists(folder_path):
            os.rename(folder_path, target_folder)
    print("Папки успешно перемещены и переименованы в /content/labels.")

# Общая функция для вызова в pipeline.py
def split_data():
    """
Основная функция для разделения данных на обучающую, валидационную и тестовую выборки.
 """
    print("Разделение данных на обучающую, валидационную и тестовую выборки...")
    process_data_folders()
    print("Разделение данных завершено.")
    
    # Создание списков файлов для каждой выборки
    base_dir = os.path.dirname(os.getcwd())
    create_split_files(base_dir)

    # Перемещение файлов в общую папку images
    move_images_to_common_folder(stored_data)

    # Сравнение и перемещение файлов obj.data и obj.names
    files_data = read_files_from_folders(stored_data)

    # Перемещение файлов в соответствии со списками и обновление путей
    file_list = ["train.txt", "valid.txt", "test.txt"]
    move_files_update_paths_for_files(file_list)

    # Перемещение и переименование папок
    move_and_rename_folders()

# Основная программа
if __name__ == "__main__":
    data_download()
    split_data()