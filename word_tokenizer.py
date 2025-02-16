import fugashi
import unidic
import unicodedata

class Word:
  def __init__(self, word: str, dictionary: str, base: str):
    self.word = word
    self.word_base = base
    self.dictionary = dictionary

  def __hash__(self):
    return hash(self.dictionary)
  
  def __eq__(self, value):
    if value == self:
      return True
    if isinstance(value, Word):
      return value.dictionary == self.dictionary
    return False

class WordTokenizer:
  def __init__(self):
    self.__tokenizer = fugashi.Tagger('-d "{}"'.format(unidic.DICDIR))

  def make_word(self, word: str) -> Word:
    token = self.__tokenizer(word)[0]
    pos = token.feature.pos1  # Part of speech
    dictionary = token.feature.orthBase  # Dictionary form
    conjugated_form = token.feature.cType  # Conjugation type
    stem = dictionary  # Default to base form

    # Check if it's a verb
    if "動詞" in pos:  # If it's a verb
      if "一段" in conjugated_form:  # Ichidan verb (e.g., 食べる)
        stem = dictionary[:-1]  # Remove final る
      elif "五段" in conjugated_form:  # Godan verb (e.g., 書く)
        stem = dictionary[:-1]
      elif dictionary.endswith("する"):
        stem = dictionary[:-2]  # Remove する
    elif "形容詞" in pos:  # I-adjective
      stem = dictionary[:-1]  # Remove final い
    # Noun + suru verbs (e.g., 勉強する)
    elif "名詞" in pos and dictionary.endswith("する"):
      stem = dictionary[:-2]  # Remove する
    
    if dictionary == "":
      return self.make_word(word + "する")
    
    return Word(word, dictionary, stem)

  def is_full_stop(char: str):
    try:
      return unicodedata.category(char) != "Cc" and "FULL STOP" in unicodedata.name(char)
    except Exception as e:
      print(e)
      print(char)

  def find_word(self, word: Word, sentence: str) -> bool:
    index = sentence.find(word.word_base)
    if index < 0:
       return False

    words = self.__tokenizer(sentence)
    for w in words:
      if word.dictionary == w.feature.orth:
        return True
    return False
  
  def extract_sentence(self, word: Word, text: str) -> str:
    index = text.find(word.word_base)
    if index < 0:
      return text

    start = index
    end = len(text)
    inBraket = False
    for i in range(index, 0, -1):
      c = text[i]
      if WordTokenizer.is_full_stop(c):
        start = i + 1
        break
      if c == "「":
        start = i
        inBraket = True
        break

    for i in range(index, end - 1, 1):
      c = text[i]
      if inBraket and c == "」":
        end = i + 1
        break
      if WordTokenizer.is_full_stop(c):
        end = i + 1
        break

    return text[start:end]

