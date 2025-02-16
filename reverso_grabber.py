import requests
import urllib.parse
from html.parser import HTMLParser
from dataset_grabber import DatasetGrabber
from typing import List
from word_sentence_item import WordSentenceItem
import credentials

headers = {
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
  "accept-encoding": "gzip, deflate, br, zstd",
  "accept-language": "en-GB,en-RU;q=0.9,en;q=0.8,ru-RU;q=0.7,ru;q=0.6,ja-JP;q=0.5,ja;q=0.4,en-US;q=0.3",
  "cache-control": "no-cache",
  "cookie": credentials.REVERSO_COOKIES,
  "pragma": "no-cache",
  "priority": "u=0, i",
  "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": "Windows",
  "sec-fetch-dest": "document",
  "sec-fetch-mode": "navigate",
  "sec-fetch-site": "same-origin",
  "sec-fetch-user": "?1",
  "upgrade-insecure-requests": "1",
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

class CRHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.example = False
        self.exampleLevel = -1
        self.exampleOriginalDiv = -1
        self.exampleTranslateDiv = -1
        self.exampleOriginal = ""
        self.exampleTranslate = ""
        self.exampleText = -1
        self.examples : List[WordSentenceItem] = list()
        self.level = 0

    def handle_starttag(self, tag, attrs):
        self.level = self.level + 1
        if not self.example:
          for attr in attrs:
            if attr[0] == "class" and attr[1] == "example":
              self.example = True
              self.exampleLevel = self.level
        else:
          for attr in attrs:
            if attr[0] == "class":
              if attr[1] == "src ltr":
                self.exampleOriginalDiv = self.level
              elif attr[1] == "trg ltr":
                self.exampleTranslateDiv = self.level
              elif self.exampleOriginalDiv > 0 and attr[1] == "text":
                self.exampleText = self.level
                self.exampleOriginal = ""
              elif self.exampleTranslateDiv > 0 and attr[1] == "text":
                self.exampleText = self.level
                self.exampleTranslate = ""

    def handle_endtag(self, tag):
        if self.exampleLevel == self.level:
          self.example = False
          self.exampleLevel = -1
          self.examples.append(WordSentenceItem(self.exampleOriginal.strip(), self.exampleTranslate.strip()))
        if self.exampleOriginalDiv == self.level:
          self.exampleOriginalDiv = -1
        if self.exampleTranslateDiv == self.level:
          self.exampleTranslateDiv = -1
        if self.exampleText == self.level:
          self.exampleText = -1
        self.level = self.level - 1

    def handle_data(self, data):
        if self.exampleText > 0:
            if self.exampleOriginalDiv > 0:
              self.exampleOriginal = self.exampleOriginal + " " + data.strip().replace('\u3000', '')
            if self.exampleTranslateDiv > 0:
              self.exampleTranslate = self.exampleTranslate + " " + data.strip().replace('\u3000', '')

def request_examples(word, fromLang, toLang):
  print("Reverso: " + word)
  queryWord = urllib.parse.quote_plus(word)
  res = requests.get(f"https://context.reverso.net/translation/{fromLang}-{toLang}/{queryWord}", headers=headers)

  if res.status_code == 200:
    parser = CRHtmlParser()
    parser.feed(res.text)
    return parser.examples
  else:
    print(res.status_code)
    return []
  
class ReversoDatasetGrabber(DatasetGrabber):
  def __init__(self):
    super().__init__()
  
  def get_sentences(self, word: str, limit = 5):
    print(f"RC word: {word} with limit {limit}")
    limit = max(limit, 0)
    if (limit <= 0):
      return []

    queryWord = urllib.parse.quote_plus(word)
    res = requests.get(f"https://context.reverso.net/translation/japanese-english/{queryWord}", headers=headers)

    if res.status_code == 200:
      parser = CRHtmlParser()
      parser.feed(res.text)
      return parser.examples[:limit]
    else:
      return []