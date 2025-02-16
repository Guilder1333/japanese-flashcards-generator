import codecs
import deepl
from furigana import Furigana
from batch_grabber import BatchDatasetGrabber
from word_sentence_item import WordSentenceItem
from typing import List
from word_tokenizer import Word, WordTokenizer
import credentials

INPUT_FILE = "words2.txt"
OUTPUT_FILE = "cards2.csv"
TRANSLATE = True
FURIGANA_JLPT_LEVEL = 1
EXAMPLES_PER_WORD = 3

examples : List[WordSentenceItem] = list()
words : List[Word] = list()

with codecs.open(INPUT_FILE, "r", "utf-8") as f:
  lines = f.readlines()
  t = WordTokenizer()
  for line in lines:
    if not line.startswith("#"):
      words.append(t.make_word(line.strip()))

# "D:/dworkspace/ja.txt"
reader = BatchDatasetGrabber("D:/dworkspace/ja.txt")
print("Ready")

sentences = reader.get_sentences(words, EXAMPLES_PER_WORD)

examples = [WordSentenceItem(s) for s in sentences]

translator = deepl.Translator(credentials.DEEPL_API_KEY)

furigana = Furigana()
furigana.set_known_jlpt_level(FURIGANA_JLPT_LEVEL)
furigana.set_known_kanji_file("known_kanji.txt")

with codecs.open(OUTPUT_FILE, "w", "utf-8") as f:
  for item in examples:

    if TRANSLATE and len(item.translation) <= 0:
      item.translation = translator.translate_text(item.sentence, target_lang="EN-US").text
    
    sentence = furigana.make_furigana(item.sentence)
    res = furigana.make_full_furigana(item.sentence)

    f.write(sentence)
    f.write(";")
    f.write(res)
    f.write("<br>")
    f.write(item.translation)
    f.write("\n")