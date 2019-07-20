#!/usr/bin/env python3

import wave
import math

INPUT_FILE = "linejka.wav"
OUTPUT_FILE = "linejka-slow.wav"

def process(channels, sample_rate):
    # Здесь вызывайте свою функцию
    # return normalize(flanger(channels, sample_rate, 0.003, 1), -2)
    return change_speed_dumb(channels, 0.67)


def normalize(channels, dB):
    target_p = 10 ** (dB / 10)
    max_p = max(abs(sample) for ch in channels for sample in ch)
    return [
        [sample * target_p / max_p for sample in ch]
        for ch in channels
    ]


def delay(channels, sample_rate, dt, decay):
    result = [[0] * len(ch) for ch in channels]

    ds = round(sample_rate * dt)
    n_channels = len(channels)
    for k in range(n_channels):
        for i in range(len(channels[k])):
            past_sample = 0 if i - ds < 0 else channels[k][i - ds]
            result[k][i] = channels[k][i] + decay * past_sample

    return result


def echo(channels, sample_rate, dt, decay):
    result = [[0] * len(ch) for ch in channels]

    ds = round(sample_rate * dt)
    n_channels = len(channels)
    for k in range(n_channels):
        for i in range(len(channels[k])):
            past_sample = 0 if i - ds < 0 else result[k][i - ds]
            result[k][i] = channels[k][i] + decay * past_sample

    return result


def speed_2x(channels):
    n_channels = len(channels)
    n_samples = len(channels[0])
    n_samples_res = n_samples // 2

    result = [[0] * n_samples_res for ch in channels]
    for k in range(n_channels):
        for i in range(n_samples_res):
            result[k][i] = (channels[k][2 * i] + channels[k][2 * i + 1]) / 2

    return result


def change_speed_dumb(channels, factor):
    n_channels = len(channels)
    n_samples = len(channels[0])
    n_samples_res = int(n_samples / factor)

    result = [[0] * n_samples_res for ch in channels]
    for k in range(n_channels):
        for i in range(n_samples_res):
            sample_src = int(i * factor)
            result[k][i] = channels[k][sample_src]

    return result


def flanger(channels, sample_rate, dt, freq):
    result = [[0] * len(ch) for ch in channels]

    ds = round(sample_rate * dt)
    n_channels = len(channels)
    for k in range(n_channels):
        for i in range(len(channels[k])):
            t = i / sample_rate
            phase = lfo(t, freq)
            sample_shift = int(sample_rate * dt * (phase + 1) / 2)
            past_i = i - sample_shift
            result[k][i] = channels[k][i] + (channels[k][past_i] if past_i >= 0 else 0)

    return result


def lfo(t, freq):
    return math.sin(freq * t * 2 * math.pi)

def main():
    channels, sample_rate, sample_width = read_wav(INPUT_FILE)

    print('Обработка... ', end='')
    channels_out = process(channels, sample_rate)
    if not check_result(channels_out):
        return
    print('Готово')

    write_wav(OUTPUT_FILE, channels_out, sample_rate, sample_width)


################################################################################
# Вспомогательный код
################################################################################


def read_wav(filename):
    wav_file = wave.open(filename, 'r')

    n_channels = wav_file.getnchannels()
    print('Количество каналов:', n_channels)

    sample_width = wav_file.getsampwidth()
    print('Размер сэмпла:', sample_width)

    sample_rate = wav_file.getframerate()
    print('Частота сэмплирования:', sample_rate)

    n_frames = wav_file.getnframes()
    print('Количество фреймов:', n_frames)

    mn, mx = bounds_for_sample_width(sample_width)

    print('\nЧтение файла... ', end='')
    frames = wav_file.readframes(n_frames)
    all_samples = [
        (int.from_bytes(frames[i:i+sample_width], byteorder='little', signed=True) - mn) / (mx - mn) * 2 - 1
        for i in range(0, len(frames), sample_width)
    ]
    channels = [all_samples[i::n_channels] for i in range(n_channels)]
    print('Готово')

    return channels, sample_rate, sample_width


def write_wav(filename, channels, sample_rate, sample_width):
    print('Запись файла... ', end='')

    mn, mx = bounds_for_sample_width(sample_width)

    all_samples = (sample for frame in zip(*channels) for sample in frame)
    frames = b''.join(round((sample + 1) / 2 * (mx - mn) + mn).to_bytes(sample_width, byteorder='little', signed=True) for sample in all_samples)

    result_wav = wave.open(filename, 'w')
    result_wav.setnchannels(len(channels))
    result_wav.setsampwidth(sample_width)
    result_wav.setframerate(sample_rate)
    result_wav.setnframes(len(channels[0]))
    result_wav.writeframes(frames)
    print('Готово')


def check_result(channel_samples):
    if len(channel_samples) == 0:
        print('Ошибка: результат обработки содержит 0 каналов')
        return False

    for i in range(len(channel_samples)):
        len_0 = len(channel_samples[0])
        len_i = len(channel_samples[i])
        if len_0 != len_i:
            print('Ошибка: количество сэмплов в каналах 1 ({}) и {} ({}) не совпадает'.format(len_0, i + 1, len_i))
            return False
    
    # TODO: слишком большие сэмплы
        
    return True

def bounds_for_sample_width(sample_width):
    power = 1 << (8 * sample_width - 1)
    return -power, power - 1

main()
