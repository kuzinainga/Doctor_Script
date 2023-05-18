from pathlib import Path

import requests

import config
from audio_recognizer import ISpeechRecognizer


class VKCloudAudioRecognizer(ISpeechRecognizer):

    @classmethod
    def recognize(cls, audio_path: Path) -> str:
        audio_data = cls._get_audio_data(audio_path)
        result = cls._request(audio_data)
        text = cls._parse_result(result)
        return text

    @classmethod
    def _request(cls, audio_data: bytes) -> dict:
        response = requests.post(
            'https://voice.mcs.mail.ru/asr',
            headers={
                'Content-Type': 'audio/wave',
                'Authorization': f'Bearer {config.VK_SERVICE_TOKEN}'
            },
            data=audio_data
        )
        print(f'VKCloudAudioRecognizer: {response.json()=}')
        response = response.json()
        return response

    @classmethod
    def _parse_result(cls, result: dict) -> str:
        return '.\n'.join([i['punctuated_text'] for i in result['result']['texts']])
