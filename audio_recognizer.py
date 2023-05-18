from abc import ABC, abstractmethod
from pathlib import Path


class ISpeechRecognizer(ABC):
    @classmethod
    @abstractmethod
    def recognize(cls, audio) -> str: ...

    @classmethod
    def _get_audio_data(cls, audio_path: Path) -> bytes:
        with open(audio_path, 'rb') as f:
            return f.read()
