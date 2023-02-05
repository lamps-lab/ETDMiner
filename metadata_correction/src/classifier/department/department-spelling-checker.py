"""
This script will check spelling error for department names

"""
from spellchecker import SpellChecker
import re
import pandas as pd

def check_word_spelling(word):
    value = []
    value.append(word)

    spell = SpellChecker()
    misspelled = spell.unknown(value)
    for word in misspelled:
      correction = spell.correction(word)

    # Get a list of `likely` options
      # print(spell.candidates(word))
    
      if (word == correction):
          pass
      else:
          print(f'Spelling of "{word}" is not correct!')
          

def check_sentence_spelling(sentence):
    
    words = sentence.split()
    
    words = [word.lower() for word in words]
    
    words = [re.sub(r'[^A-Za-z0-9]+', '', word) for word in words]


    for word in words:
        check_word_spelling(word)


dataset = pd.read_csv('filename') // TODO; It takes a CSV file as input which has 2 coulmns (ETDID, DEPARTMENT)
etds = pd.DataFrame(dataset)
for index, row in etds.iterrows():
    etd_id = row[0]
    try:
      department_name = row[1]
        check_sentence_spelling(department_name)
    except:
      pass
