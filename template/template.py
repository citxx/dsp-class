#!/usr/bin/env python3

import wave

# Шаблон для обработки звука.
#
# В секции "вспомогательный код" внизу файла уже написаны функции для чтения
# и записи .wav файлов (read_wav и write_wav).
#
# В основной функции main:
# 1. Читается .wav файл, путь к которому указан в переменной INPUT_FILE
# 2. Вызывается функция process, которая должна обработать сигнал и вернуть
#    результат обработки
# 3. Результат проверяется на корректность (количество каналов, равное количество
#    сэмплов в канале и т.д.)
# 4. Результат записывается в .wav файл, путь к которому указан в переменной
#    OUTPUT_FILE
#
# Как сделать новый фильтр:
# 1. Определить новую функцию, используя change_amp как пример
# 2. Изменить функцию process, чтобы она использовала новый фильтр для обработки
#    и возвращала результат
# 3. Если вы хотите применить к исходному сигналу несколько разных фильтров,
#    то можно последовательно вызвать эти фильтры в функции process

# Тут можно поменять пути к входному и результирующему файлам
INPUT_FILE = "linejka.wav"
OUTPUT_FILE = "result.wav"

# Функция process вызывается из функции main для обработки сигнала
#
# Аргументы:
# channels - Список каналов. Каждый канал - список сэмплов. 
# channels[ch][i] - i-й сэмпл в канале с номером ch. Дробное число от -1 до 1.
# sample_rate - частота сэмплирования. Сколько сэмплов в одной секунде.
#
# Возвращаемое значение:
# Результат обработки в том же формате, что и channels
def process(channels, sample_rate):
    # Здесь вызывайте свою функцию или последовательность функций для обработки
    # звука.
    return change_amp(channels, 0.5)


# Сейчас эта функция просто копирует сигнал. Вам надо изменить её так, чтобы она
# домножала амплитуду на factor.
def change_amp(channels, factor):
    # Двумерный список для результирующего сигнала такого же размера, как channels
    result = [[0] * len(ch) for ch in channels]

    # Код для обработки аудио-сигнала.
    n_channels = len(channels)
    for k in range(n_channels):
        for i in range(len(channels[k])):
            result[k][i] = channels[k][i]

    return result


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

    all_samples = (min(max(-1, sample), 1) for frame in zip(*channels) for sample in frame)
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
