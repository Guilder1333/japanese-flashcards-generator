from typing import List
from word_tokenizer import WordTokenizer, Word

class BatchDatasetGrabber:
  def __init__(self, file_name: str, encoding="utf-8"):
    super().__init__()
    self.__file_name = file_name
    self.__encoding = encoding
    self.__word_tokenizer = WordTokenizer()

  def get_sentences(self, words: List[Word], limit = 5):
    sentences = set()
    word_map = dict()
    for word in words:
      word_map[word] = 0
    
    to_collect = len(words) * limit
    with open(self.__file_name, "r", encoding=self.__encoding) as f:
      for line in f.readlines():
        s = line.strip()
        for word in list(word_map.keys()):
          if self.__word_tokenizer.find_word(word, s):
            s = self.__word_tokenizer.extract_sentence(word, s)
            sentences.add(s)
            to_collect -= 1
            count = word_map[word] + 1
            if count >= limit:
              del word_map[word]
            else:
              word_map[word] = count

    if len(word_map) > 0:
      print("Lack examaples:")
      for word in word_map.keys():
        print(f"{word.word} {limit - word_map[word]}")
    return sentences
          
