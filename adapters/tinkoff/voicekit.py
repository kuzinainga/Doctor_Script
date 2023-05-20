from pathlib import Path

import grpc

import config
from adapters.tinkoff.auth import authorization_metadata
from adapters.tinkoff.stt.v1 import stt_pb2_grpc, stt_pb2
from audio_recognizer import ISpeechRecognizer


class VoiceKitRecognizer(ISpeechRecognizer):
    endpoint = 'api.tinkoff.ai:443'
    api_key = config.TINKOFF_API_KEY
    secret_key = config.TINKOFF_SECRET_KEY

    @classmethod
    def recognize(cls, audio_path: Path) -> str:
        stub = stt_pb2_grpc.SpeechToTextStub(grpc.secure_channel(cls.endpoint, grpc.ssl_channel_credentials()))
        metadata = authorization_metadata(cls.api_key, cls.secret_key, 'tinkoff.cloud.stt')
        audio_data = cls._get_audio_data(audio_path)
        response = stub.Recognize(cls.build_request(audio_data), metadata=metadata)
        text = cls.parse_response(response)
        return text

    @classmethod
    def parse_response(cls, response) -> str:
        transcripts = [alternative.transcript for result in response.results for alternative in result.alternatives]
        text = ' '.join(transcripts)
        return text

    @classmethod
    def build_request(cls, audio: bytes):
        request = stt_pb2.RecognizeRequest()
        request.audio.content = audio
        request.config.encoding = stt_pb2.AudioEncoding.LINEAR16
        request.config.sample_rate_hertz = 44100
        request.config.num_channels = 1
        return request
