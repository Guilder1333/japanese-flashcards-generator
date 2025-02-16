from dataset_grabber import DatasetGrabber
from word_tokenizer import Word, WordTokenizer
from openai import OpenAI

DEFAULT_PROMPT_JP = "日本語の勉強の教育アシスタントです。受けた言葉に{count}つの例文を作って。例文のレベルは日本語能力試験のN{complexity}ぐらいです。それ以外何も書き出せないことです。フォーマットなしです。各文にその言葉を含む必要です。"
DEFAULT_PROMPT_EN = "You are a japanese language learning assistant. You need to generate example sentences for the word you are asked about. Answer consists of {count} example senteces on japanese. Examples must be approximately of level JLPT N{complexity}. No additional formatting. Each sentence is new line. No numeration required."
LOCAL_MODEL="schroneko/gemma-2-2b-jpn-it"

class OpenAIGrabber(DatasetGrabber):
  def __init__(self, api_key: str, url : str=None, prompt : str|None = None, sentence_complexity=2, model=None):
    super().__init__()
    self.__client = OpenAI(base_url=url, api_key=api_key)
    self.__prompt = prompt
    if self.__prompt == None:
      self.__prompt = DEFAULT_PROMPT_JP
    self.__complexity = sentence_complexity
    self.__tokenizer = WordTokenizer()
    self.__model = model

  def get_sentences(self, word: Word, limit=5):
    count = 0
    while count < limit:
      response = self.__client.chat.completions.create(
        model=self.__model,
        messages=[
          {"role": "system", "content": self.__prompt.format(count=limit, complexity=self.__complexity)},
          {"role": "user", "content": word.word},
        ]
      )
      print(response.choices[0].message.content)
      for sentence in self.__valid_sentences(word, response.choices[0].message.content):
        count += 1
        yield sentence
        if count >= limit:
          return


  def __valid_sentences(self, word: Word, response: str):
    for line in response.splitlines():
      line : str = line.strip().strip("*/-'\"`()[]\{\}・|｜｛｝［］【】”’‘（）").strip()
      if (line.startswith("「") and line.endswith("」")) or (line.startswith("『") and line.endswith("』")):
        line = line.strip("『』「」")
      line = line.replace(f"「{word.word}」", word.word)
      if self.__tokenizer.find_word(word, line):
        yield line
      
class OllamaGrabber(OpenAIGrabber):
  def __init__(self, prompt = DEFAULT_PROMPT_JP, sentence_complexity=2, model=LOCAL_MODEL):
    super().__init__("ollama", "http://localhost:11434/v1", prompt, sentence_complexity, model)