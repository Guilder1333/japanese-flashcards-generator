from word_sentence_item import WordSentenceItem
from typing import List
from typing import Generator
from word_tokenizer import WordTokenizer, Word
import json

class DatasetGrabber:
  def __init__(self):
    pass

  def get_sentences(self, word: Word, limit = 5) -> Generator[WordSentenceItem, None, None]:
    pass

class BaseDatasetGrabber(DatasetGrabber):
  def __init__(self):
    super().__init__()
    self.items : List[WordSentenceItem] = list()
    self.__word_tokenizer = WordTokenizer()

  def get_sentences(self, word: Word, limit = 5) -> Generator[WordSentenceItem, None, None]:
    count = 0
    for item in self.items:
      if self.__word_tokenizer.find_word(word, item.sentence):
        yield item
        count += 1
        if count >= limit:
          return
  
class TextWithTranslationDatasetGrabber(BaseDatasetGrabber):
  def __init__(self, jp_file_name: str, tr_file_name: str, encoding="utf-8"):
    super().__init__()

    with open(jp_file_name, "r", encoding=encoding) as f:
      for line in f.readlines():
        self.items.append(WordSentenceItem(line.strip()))

    with open(tr_file_name, "r", encoding=encoding) as f:
      i = 0
      for line in f.readlines():
        self.items[i].translation = line.strip()
        i += 1

class JsonConversationDatasetGrabber(BaseDatasetGrabber):
  def __init__(self, file_name: str, encoding="utf-8"):
    super().__init__()

    j : list = None
    with open(file_name, "r", encoding=encoding) as f:
      j = json.loads(f.read())

    for conversation in j:
      for item in conversation["conversation"]:
        self.items.append(WordSentenceItem(item["ja_sentence"].strip(), item["en_sentence"].strip()))

class MultiDatasetGrabber(DatasetGrabber):
  def __init__(self, list: List[DatasetGrabber]):
    super().__init__()
    self.__list = list

  def get_sentences(self, word: Word, limit = 5) -> Generator[WordSentenceItem, None, None]:
    count = 0
    for g in self.__list:
      for item in g.get_sentences(word, limit - count):
        yield item
        count += 1
        if count >= limit:
          return
