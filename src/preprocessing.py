import os
import shutil
import requests
import zipfile
import time
from config import stored_data  # Импорт переменной stored_data из config.py

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
    
# Основная программа
if __name__ == "__main__":
    data_download()