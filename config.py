import pathlib

BASE_DIR = pathlib.Path(__file__).parent.absolute()

with open(pathlib.Path(BASE_DIR, '.env')) as file:
    ENV = {}
    lines = [line for line in file.read().strip().split()]
    for line in lines:
        delimiter_index = line.index('=')
        ENV.update({line[:delimiter_index]: line[delimiter_index+1:]})

# Пути аудио-файлов
WAVE_PATH = pathlib.Path(BASE_DIR, 'recording.wav')
OGG_PATH = pathlib.Path(BASE_DIR, 'recording.ogg')

# Tinkoff
TINKOFF_API_KEY = ENV.get('TINKOFF_API_KEY')
TINKOFF_SECRET_KEY = ENV.get('TINKOFF_SECRET_KEY')

# VK
VK_SERVICE_TOKEN = ENV.get('VK_SERVICE_TOKEN')

# Yandex
YANDEX_ACCOUNT_ID = ENV.get('YANDEX_ACCOUNT_ID')
YANDEX_FOLDER_ID = ENV.get('YANDEX_FOLDER_ID')
YANDEX_OAUTH_TOKEN = ENV.get('YANDEX_OAUTH_TOKEN')
