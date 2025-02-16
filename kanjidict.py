import xml.etree.ElementTree as ET

"""
Download kanjidict2.xml from here
http://www.edrdg.org/kanjidic/kanjidic2.xml.gz
"""
class Kanjidict:
  def __init__(self):
    tree = ET.parse("kanjidic2.xml")
    root = tree.getroot()

    self.__kanji_dict = dict()

    for character in root.findall("character"):
      literal = character.find("literal").text
      for misc in character.findall("misc"):
        jlpt = misc.find("jlpt")
        if jlpt is not None:
          self.__kanji_dict[literal] = int(jlpt.text)

  def get_level(self, kanji: str):
    if kanji in self.__kanji_dict:
      return self.__kanji_dict[kanji]
    return 0