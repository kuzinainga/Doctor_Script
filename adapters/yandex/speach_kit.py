from pathlib import Path

import requests

import config
from audio_recognizer import ISpeechRecognizer


class YandexSpeachKitRecognizer(ISpeechRecognizer):
    CHUNK_SIZE: int = 4000
    AIM_TOKEN: str | None = None

    @classmethod
    def recognize(cls, audio_path: Path) -> str:

        audio_data = cls._get_audio_data(audio_path)

        params = {
            "topic": "general",
            "folderId": config.YANDEX_FOLDER_ID,
            "lang": "ru-RU"
        }

        headers = {
            "Authorization": f"Bearer {cls.AIM_TOKEN or cls.generate_aim_token()}"
        }

        url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

        response = requests.post(url, params=params, headers=headers, data=audio_data)

        return response.json()['result']

    @classmethod
    def generate_aim_token(cls) -> str:
        try:
            aim_token_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
            headers = {
                "Content-Type": "application/json",
                "Authorization": f'Bearer {config.YANDEX_OAUTH_TOKEN}'
            }
            request_body = {
                "yandexPassportOauthToken": config.YANDEX_OAUTH_TOKEN
            }
            response = requests.post(aim_token_url, headers=headers, json=request_body)
            response_data = response.json()
            cls.AIM_TOKEN = response_data["iamToken"]
            return cls.AIM_TOKEN
        except requests.exceptions.RequestException as e:
            print("Ошибка при отправке запроса:", e)
