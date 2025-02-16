import codecs
import deepl
from book_grabber import BooksGrabber, Book
from furigana import Furigana
import credentials
from typing import List
import csv

examples = list()
words = []

with codecs.open("words.txt", "r", "utf-8") as f:
  lines = f.readlines()
  for line in lines:
    words.append(line.strip())

books : List[Book] = list()
with csv.reader("books.csv", delimiter=";") as books_csv:
  for row in books_csv:
    books.append(Book(row[0], row[1]))

reader = BooksGrabber(books)
for word in words:
  wl = reader.get_sentences(word)
  if len(wl) <= 0:
    print("No examples: " + word)
  else:
    examples.extend(wl)

translator = deepl.Translator(credentials.DEEPL_API_KEY)

furigana = Furigana()
furigana.set_known_jlpt_level(1)
furigana.set_known_kanji_file("known_kanji.txt")

with codecs.open("cards.csv", "w", "utf-8") as f:
  for example in examples:

    # translation = translator.translate_text(example, target_lang="EN-US").text
    translation = ""
    
    sentence = furigana.make_furigana(example)
    res = furigana.make_full_furigana(example)

    f.write(sentence)
    f.write(";")
    f.write(res)
    f.write("<br>")
    f.write(translation)
    f.write("\n")