from pathlib import Path

import requests

import config
from audio_recognizer import ISpeechRecognizer


class YandexSpeachKitRecognizer(ISpeechRecognizer):
    CHUNK_SIZE = 4000

    @classmethod
    def recognize(cls, audio_path: Path) -> str:

        audio_data = cls._get_audio_data(audio_path)

        params = {
            "topic": "general",
            "folderId": config.YANDEX_FOLDER_ID,
            "lang": "ru-RU"
        }

        headers = {
            "Authorization": f"Bearer {config.iam_token}"
        }

        url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

        response = requests.post(url, params=params, headers=headers, data=audio_data)

        return response.json()['result']