import threading
import time
import tkinter as tk
import wave
import numpy as np
import pyaudio
import soundfile as sf
from pathlib import Path

import config
from adapters.tinkoff.voicekit import VoiceKitRecognizer
from adapters.vk.cloud import VKCloudAudioRecognizer
from adapters.yandex.speach_kit import YandexSpeachKitRecognizer


class SpeechRecorderApp:
    SAMPLE_FORMAT = pyaudio.paInt16
    CHANNELS = 1
    SAMPLE_RATE = 44100
    CHUNK = 2048

    play_button: tk.Button
    timer: tk.Label
    yandex_text_output: tk.Text
    tinkoff_text_output: tk.Text
    vk_text_output: tk.Text

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Doctor Script")
        self.window.geometry('1170x630')
        self.window.configure(background='#D4F5FE')

        self.recording = False

        self.create_widgets()

    def create_widgets(self):
        self.create_play_button()
        self.create_timer_label()
        self.create_text_output_frames()

    def create_play_button(self):
        self.play_button = tk.Button(self.window, text="Play", command=self.toggle_recording)
        self.play_button.grid(row=0, column=1, pady=5)

    def create_timer_label(self):
        self.timer = tk.Label(background='#D4F5FE')
        self.timer.grid(row=1, column=1)

    def create_text_output_frames(self):
        yandex_frame = tk.LabelFrame(self.window, text='Яндекс')
        self.yandex_text_output = tk.Text(yandex_frame, height=30, width=45)
        self.yandex_text_output.grid()
        yandex_frame.grid(row=2, column=0, padx=10)

        tinkoff_frame = tk.LabelFrame(self.window, text='Тинькофф')
        self.tinkoff_text_output = tk.Text(tinkoff_frame, height=30, width=45)
        self.tinkoff_text_output.grid()
        tinkoff_frame.grid(row=2, column=1, padx=10)

        vk_frame = tk.LabelFrame(self.window, text='ВК')
        self.vk_text_output = tk.Text(vk_frame, height=30, width=45)
        self.vk_text_output.grid()
        vk_frame.grid(row=2, column=2, padx=10)

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.play_button.config(text="Stop")
        threading.Thread(target=self.record).start()

    def stop_recording(self):
        self.recording = False
        self.play_button.config(text="Play")

    def record(self):
        audio_frames = self.record_audio()
        self.save_wav(audio_frames)
        self.save_ogg(audio_frames)
        self.recognize()

    def record_audio(self) -> list[bytes]:
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.SAMPLE_FORMAT,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        frames = []
        start_time = time.time()

        while self.recording:
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            frames.append(data)
            self.update_timer(start_time)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        return frames

    def update_timer(self, start_time: float):
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timer.config(text=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

    def save_wav(self, frames: list[bytes]):
        wave_file = wave.open(str(config.WAVE_PATH), 'wb')
        wave_file.setnchannels(self.CHANNELS)
        wave_file.setsampwidth(pyaudio.get_sample_size(self.SAMPLE_FORMAT))
        wave_file.setframerate(self.SAMPLE_RATE)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

    def save_ogg(self, frames: list[bytes]):
        array = [np.frombuffer(frame, dtype=np.int16) for frame in frames]
        data = np.concatenate(array).astype(np.float32)
        sf.write(file=str(config.OGG_PATH), data=data, samplerate=self.SAMPLE_RATE, format="ogg")

    def recognize(self):
        self.timer.config(text='Идет распознавание текста...')

        threads = [
            threading.Thread(target=self.recognize_by_yandex, args=[config.OGG_PATH]),
            threading.Thread(target=self.recognize_by_tinkoff, args=[config.WAVE_PATH]),
            threading.Thread(target=self.recognize_by_vk, args=[config.WAVE_PATH])
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.timer.config(text='')

    def recognize_by_yandex(self, audio_path: Path):
        recognized_text = YandexSpeachKitRecognizer.recognize(audio_path)
        self.update_text_output(self.yandex_text_output, recognized_text)

    def recognize_by_tinkoff(self, audio_path: Path):
        recognized_text = VoiceKitRecognizer.recognize(audio_path)
        self.update_text_output(self.tinkoff_text_output, recognized_text)

    def recognize_by_vk(self, audio_path: Path):
        recognized_text = VKCloudAudioRecognizer.recognize(audio_path)
        self.update_text_output(self.vk_text_output, recognized_text)

    @staticmethod
    def update_text_output(text_output: tk.Text, text: str):
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, text)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = SpeechRecorderApp()
    app.run()
