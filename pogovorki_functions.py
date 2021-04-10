#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle
import csv
from random import randint as dice
import random


# Чтение файла
def readfile(filename, divide, divider='|'):
    filelines = []
    newfile = open(filename, encoding='utf-8')
    for line in newfile:
        if divide and line.find(divider) != -1:
            filelines.append(line.rstrip('\n').split(divider))
        elif not divide:
            filelines.append(line.rstrip('\n'))
    newfile.close()
    return filelines

# Запись в файл
def writefile(filename, wisdom):
    file = open(filename, 'a')
    file.write(wisdom + '\n')
    file.close()

# Причесывание строки
def trim(wisdom):
    wisdom = wisdom.replace(',,', ',')
    wisdom = wisdom.replace('?,', ',')
    wisdom = wisdom.replace(', —', ' —')
    wisdom = wisdom.replace(', –', ' -')
    wisdom = wisdom.replace(': —', ':')
    wisdom = wisdom.replace(': -', ':')
    wisdom = wisdom.replace(':,', ':')
    return wisdom

def readcsv (file, row):
    result = []
    with open(file, encoding='utf-8') as r_file:
        # Создаем объект reader, указываем символ-разделитель ","
        file_reader = csv.reader(r_file, delimiter=",")
        for line in file_reader:
                result.append(line[row])
        return result

def nn_writefile(file, source):
    new_file = open(file, 'a')
    for line in source:
        new_file.write(line + '\n')
    new_file.close()


def splitfile(filename, filename1, filename2, weight):
    newfile = open(filename, 'r', encoding='utf-8')
    file1 = open(filename1, 'a')
    file2 = open(filename2, 'a')
    for line in newfile:
        if dice(1, weight) == 1:
            file2.write(line)
        else:
            file1.write(line)
    newfile.close()
    file1.close()
    file2.close()
    return True

def symbol_to_digits(symbol):
    return (ord(symbol) - 1071) / 35

def nn_readfile(filename, target):
    if target not in [0, 1]:
        return False
    result = []
    filelines = []
    source = []
    res = [0]*2
    res[target] = 1
    with open(filename, 'r', encoding='utf-8') as newfile:
        for line in newfile:
            line = line.rstrip('\n')
            source.append(line)
            if len(line) < 150 and line != '':
                temp = [0] * 150
                result.append(target)
                temp[0] = res
                temp_line = []
                for letter in line:
                    if letter in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЫЭЮЯабвгдеёжзийклмнопрстуфхцчшщьъыэюя ':
                        temp_line.append(letter.lower())
                for i in range(len(temp_line)):
                    if temp_line[i] != ' ':
                        temp[i+1] = symbol_to_digits(temp_line[i])
                    else:
                        temp[i+1] = 0.99
                filelines.append(temp)
                #print(line)
                #print(temp)
    return filelines, source

def str_to_data(input_string, target):
    if target not in [0, 1]:
        return False
    result = [0.01]*2
    result[target] = 0.99
    line = [0]*150
    line[0] = result
    temp_line = []
    for letter in input_string:
        if letter in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЫЭЮЯабвгдеёжзийклмнопрстуфхцчшщьъыэюя ':
            temp_line.append(letter.lower())
    for i in range(len(temp_line)):
        if temp_line[i] != ' ':
            line[i+1] = symbol_to_digits(temp_line[i])
        else:
            line[i+1] = 0.99
    return line

def load_net(file):
    with open(file, 'rb') as f:
        net = pickle.load(f)
    return net

def data_shuffle(data1, data2):
    random.shuffle(data1)
    random.shuffle(data2)
    length = min([len(data1), len(data2)])
    trainData = data1[0:length] + data2[0:length]
    print('yesdata: ', len(data1), ' nodata: ', len(data2), ' traindata: ', len(trainData))
    random.shuffle(trainData)
    return trainData

