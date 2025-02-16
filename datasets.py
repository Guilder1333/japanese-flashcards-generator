import codecs
import deepl
from reverso_grabber import ReversoDatasetGrabber
import book_grabber
from book_grabber import BooksGrabber, Book
from furigana import Furigana
from dataset_grabber import MultiDatasetGrabber, TextWithTranslationDatasetGrabber, JsonConversationDatasetGrabber, JumboDatasetGrabber
from openai_grabber import OllamaGrabber
from word_sentence_item import WordSentenceItem
from typing import List
import credentials
import csv

examples : List[WordSentenceItem] = list()
words = []

with codecs.open("words.txt", "r", "utf-8") as f:
  lines = f.readlines()
  for line in lines:
    words.append(line.strip())

books : List[Book] = list()
with csv.reader("books.csv", delimiter=";") as books_csv:
  for row in books_csv:
    books.append(Book(row[0], row[1]))

sets = [
  JsonConversationDatasetGrabber("D:/dworkspace/BSD/train.json"),
  TextWithTranslationDatasetGrabber("D:/dworkspace/PheMT/proper/proper.ja", "D:/dworkspace/PheMT/proper/proper.en"),
  TextWithTranslationDatasetGrabber("D:/dworkspace/PheMT/abbrev/abbrev.orig.ja", "D:/dworkspace/PheMT/abbrev/abbrev.en"),
  TextWithTranslationDatasetGrabber("D:/dworkspace/PheMT/colloq/colloq.orig.ja", "D:/dworkspace/PheMT/colloq/colloq.en"),
  TextWithTranslationDatasetGrabber("D:/dworkspace/PheMT/variant/variant.orig.ja", "D:/dworkspace/PheMT/variant/variant.en"),
  TextWithTranslationDatasetGrabber("D:/dworkspace/PheMT/proper/proper.ja", "D:/dworkspace/PheMT/proper/proper.en"),
  BooksGrabber(books),
  

  # JumboDatasetGrabber("D:/dworkspace/ja.txt"),
  ReversoDatasetGrabber()
]
reader = MultiDatasetGrabber(sets)
print("Ready")
for word in words:
  print(f"Word {word}")

  wl = list(reader.get_sentences(word, 5))
  if len(wl) == 0:
    print(f"Word {word} not found")
  examples.extend(wl)

translator = deepl.Translator(credentials.DEEPL_API_KEY)

furigana = Furigana()
furigana.set_known_jlpt_level(1)
furigana.set_known_kanji_file("known_kanji.txt")

with codecs.open("cards.csv", "w", "utf-8") as f:
  for item in examples:

    if len(item.translation) <= 0:
      item.translation = translator.translate_text(item.sentence, target_lang="EN-US").text
    
    sentence = furigana.make_furigana(item.sentence)
    res = furigana.make_full_furigana(item.sentence)

    f.write(sentence)
    f.write(";")
    f.write(res)
    f.write("<br>")
    f.write(item.translation)
    f.write("\n")