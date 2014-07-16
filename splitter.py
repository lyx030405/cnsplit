#!/usr/bin/python -B
#-*- encoding: utf-8 -*-

#
# Author: Zhang Li, HUST (algorithm partially from http://leeing.org/2009/11/01/mmseg-chinese-segmentation-algorithm)
#
import sys
import dictionary


class Word(object):
    def __init__(self, content, length, frequency):
        self.content = content
        self.length = length
        self.frequency = frequency
        return
    def __cmp__(self, obj):
        return cmp(self.content, obj.content)
    pass

class Chunk(object):
    def __init__(self, *args):
        self.words = args
        return

    def total_frequency(self):
        return sum(x.frequency for x in self.words)

    def total_length(self):
        return sum(x.length for x in self.words)

    def empty_count(self):
        return reduce(lambda count, x: count + int(x.length == 0), self.words, 0)

    pass

class Splitter(object):
    def __retrieve_starting_words(self, pos):
        if pos >= self.length:
            return [Word(unicode(), length = 0, frequency = 0)]

        # process English words
        if ord(self.content[pos]) < 128 and self.content[pos].isalnum():
            words = [Word(self.content[pos], 0, 0)]
            pos += 1
            while pos < self.length and ord(self.content[pos]) < 128 and self.content[pos].isalnum():
                words[0].content += self.content[pos]
                pos += 1
            words[0].length = len(words[0].content)
            words[0].frequency = 1000 / words[0].length
            return words

        # process Chinese words by looking up dictionary
        words = []
        maxlen = min(dictionary.words_maxlen, (self.length - pos))

        for length in range(1, 1 + maxlen):
            segment = self.content[pos : pos + length]
            if dictionary.words.has_key(segment):
                words.append(Word(segment, length, dictionary.words[segment]))

        if len(words) == 0:
            words.append(Word(self.content[pos], length = 1, frequency = 0))
        return words

    def __filter_chunks(self, chunks, filter_func):
        maxval = max(map(filter_func, chunks))
        chunks = filter(lambda x: filter_func(x) == maxval, chunks)
        return chunks

    def process(self, content = unicode()):
        self.content, self.length = content, len(content)
        pos = 0
        words = []

        while pos < self.length:
            chunks = []

            # generate all possible 3-word chunks
            for x1 in self.__retrieve_starting_words(pos):
                for x2 in self.__retrieve_starting_words(pos + x1.length):
                    for x3 in self.__retrieve_starting_words(pos + x1.length + x2.length):
                        chunks.append(Chunk(x1, x2, x3))

            # filter bad chunks
            if len(chunks) > 1: chunks = self.__filter_chunks(chunks, Chunk.total_length)
            if len(chunks) > 1: chunks = self.__filter_chunks(chunks, Chunk.empty_count)
            if len(chunks) > 1: chunks = self.__filter_chunks(chunks, Chunk.total_frequency)

            # got a word
            words.append(chunks[0].words[0])
            pos += words[-1].length
        return words
