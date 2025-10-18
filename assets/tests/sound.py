#import sounddevice as sd
import numpy as np
import time
import pyaudio

#from other.moe.SoundCloudFM.FM import *

class Sound():
    def __init__(self,sound):
        self.sound = sound

        self.length = None

#def normalize(arr,arr2):
#    for i in range(arr)

"""def generate_white_noise(duration=5, sample_rate=44100, amplitude=0.5):
    # Рассчитать количество кадров
    num_frames = int(duration * sample_rate)
    # Сгенерировать случайные выборки из стандартного нормального распределения
    noise = np.random.normal(0, amplitude, num_frames)
    # Убедиться, что шум находится в приемлемом диапазоне для аудио
    noise = np.clip(noise, -1, 1)
    print(noise)

    # Играть белый шум с помощью библиотеки sounddevice
    sd.play(noise, samplerate=sample_rate,blocking=False,loop=True)

generate_white_noise()
print(1)
print(1)
print(1)
print(1)
time.sleep(45)"""