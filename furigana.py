import fugashi
import unidic
import unicodedata
from typing import Set
from kanjidict import Kanjidict

class Furigana:
  def __init__(self):
    self.__tagger = fugashi.Tagger('-d "{}"'.format(unidic.DICDIR))
    self.__known_kanji : Set[str] = set()
    self.__level = 6
    self.__kanjidict = Kanjidict()

  def set_known_kanji(self, known_kanji: Set[str]):
    self.__known_kanji = known_kanji

  def set_known_kanji_file(self, file_name: str, encoding = "utf-8"):
    self.__known_kanji = set()

    with open(file_name, "r", encoding=encoding) as f:
      for line in f.readlines():
        self.__known_kanji.add(line.strip())
    
  """
  Show furigana for all kanji above the specified JLPT level.
  Word level is based on the highest level of component kanji.
  Lowest level is 5, setting 6 or above means that furigana for all kanji will be shown.
  Highest level is 0, setting 0 or below means that none of the kanji will have furigana.
  """
  def set_known_jlpt_level(self, level: int):
    self.__level = level

  def __is_kana(word: str):
      return all(unicodedata.name(char).startswith("HIRAGANA") or unicodedata.name(char).startswith("KATAKANA") for char in word)
  
  def __is_known(self, word: str):
    known = True
    for char in word:
      if not unicodedata.name(char).startswith("HIRAGANA") and not unicodedata.name(char).startswith("KATAKANA"):
        known = known and (char in self.__known_kanji)
    return known
  
  def __is_known_level(self, word: str):
    level = 6
    for char in word:
      if not unicodedata.name(char).startswith("HIRAGANA") and not unicodedata.name(char).startswith("KATAKANA"):
        level = min(level, self.__kanjidict.get_level(char))
    return level >= self.__level

  def make_full_furigana(self, sentence: str):
    words = self.__tagger(sentence)

    res = ""
    for word in words:
      if word.feature.pos1 == "補助記号" or word.feature.pos1 == "助詞" or Furigana.__is_kana(word.surface) or word.feature.kana is None:
        res = res + word.surface
      else:
        res = res + " " + word.surface + "［" + word.feature.kana + "］"

    return res
  
  def make_furigana(self, sentence: str):
    words = self.__tagger(sentence)

    res = ""
    for word in words:
      if word.feature.pos1 == "補助記号" or word.feature.pos1 == "助詞" or Furigana.__is_kana(word.surface) or word.feature.kana is None or self.__is_known(word.surface) or self.__is_known_level(word.surface):
        res = res + word.surface
      else:
        res = res + " " + word.surface + "［" + word.feature.kana + "］"

    return res