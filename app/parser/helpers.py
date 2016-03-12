# -*- coding: utf-8 -*-
import re
from datetime import datetime

"""
    Common functions
"""

def poemMatch(lines_stat):
    """
        Возвращает словари вида: { 'start': int, 'end': int }
        где 'start' начало стиха, а 'end' конец.
        Будут возвращены только те стихотворения, что следуют правилам:
        Первая строка: 9 слогов
        Вторая строка: 8 слогов
        Третья строка: 9 слогов(если нет, то отправятся только первые две строки)
        Четвёртая строка: 8 слогов или 2 слога(так называемый 'порошок')
    """
    result = []

    i = 1
    half_cake = False
    while i < len(lines_stat):
        first  = lines_stat[i - 1]
        second = lines_stat[i - 0]
        match98 = (first['vowels'] == 9) and (second['vowels'] == 8)
        match92 = (first['vowels'] == 9) and (second['vowels'] == 2)

        if match98 and half_cake:
            result.append({'start': lines_stat[i - 3]['pos'], 'end': lines_stat[i]['pos']})
            half_cake = False
            i += 2
        elif match98 and not half_cake:
            half_cake = True
            i += 2
        elif half_cake and match92:
            half_cake = False
            result.append({'start': lines_stat[i - 3]['pos'], 'end': lines_stat[i]['pos']})
            i += 2
        elif half_cake:
            half_cake = False
            result.append({'start': lines_stat[i - 1]['pos'], 'end': lines_stat[i]['pos']})
            i += 2
        else:
            i += 1

    return result

def textStat(text):
    vowels = u'ауоыиэяюёе'
    lines = text.split('\n')
    lines_stat = []
    i = 0
    for line in lines:
        line_stat = {'pos': i, 'vowels': 0, 'line': line}
        for letter in line:
            if letter in vowels:
                line_stat['vowels'] += 1

        lines_stat.append(line_stat)
        i += 1

    return lines_stat

def iso8601(utc):
    """
        From UnixTime to iso8601
    """
    return datetime.fromtimestamp(utc).isoformat()

def br(text):
    """
        Replace <br> to '\n'
    """
    result = re.sub('\s*<br>\s*', '\n', text)
    return result

def getPoems(raw_text):
    """
        Returns [{poem, author}]
    """
    text = br(raw_text)
    text_stat = textStat(text)
    items = poemMatch(text_stat)
    poems = []
    lines = text.split('\n')
    for item in items:
        poem = {'text':'', 'author_raw': '', 'text_raw': text}
        start = item['start']
        end   = item['end'] + 1
        # poem
        for line in lines[start:end]:
            poem['text'] += line + "\n"
        # author
        for line in lines[end:(end + 2)]:
            poem['author_raw'] += line + "\n"
        poems.append(poem)

    return poems

def author(raw_text):
    """
        Makes author nick pretty
    """
    result = re.sub('\[(id|club)[0-9^\|]+\||[\]]', '', raw_text).replace('&amp;', '&').strip()
    return re.sub(' +', ' ', result)

def makePretty(text):
    return author(br(text))