import codecs
import fugashi
import unidic
from typing import List
from dataset_grabber import DatasetGrabber
from word_tokenizer import WordTokenizer, Word
from word_sentence_item import WordSentenceItem

class Book:
  def __init__(self, file_name: str, encoding = "utf-8"):
    self.content = ""
    self.__file_name = file_name
    self.__encoding = encoding

  def read_book(self):
    with codecs.open(self.__file_name, "r", self.__encoding) as f:
        self.content = f.read()

class BooksGrabber(DatasetGrabber):
  def __init__(self, books: List[Book]):
    super().__init__()
    self.__all_read = False
    self.__books = books
    self.__tokenizer = WordTokenizer()
    

  def __read_books(self):
    for book in self.__books:
      book.read_book()

    self.__all_read = True

  def get_sentences(self, word: Word, limit = 5):
    if not self.__all_read:
      self.__read_books()
    
    index = -2
    sentences = []
    for book in self.__books:
      content = book.content
      size = len(content) - 1
      while True:
        index = content.find(word.word_base, index + 2)
        if index < 0:
          break

        start = index
        end = index
        inBraket = False
        for i in range(index, 0, -1):
          c = content[i]
          if self.__tokenizer.is_full_stop(c):
            start = i + 1
            break
          if c == "「":
            start = i
            inBraket = True
            break

        for i in range(index, size, 1):
          c = content[i]
          if inBraket and c == "」":
            end = i + 1
            break
          if self.__tokenizer.is_full_stop(c):
            end = i + 1
            break

        sentence = content[start:end].replace("\n", "").replace("\r", "").strip()

        if self.__tokenizer.find_word(sentence):
          sentences.append(WordSentenceItem(sentence))

    sentences.sort(key=lambda x: -len(x.sentence))
    sentences = sentences[max(len(sentences) // 2 - limit // 2, 0):min(len(sentences) // 2 + limit // 2 + limit % 2, len(sentences))]
    return sentences
    