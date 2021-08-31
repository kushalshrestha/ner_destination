import spacy
from spacy.tokens import DocBin
import typer
from pathlib import Path
import pandas as pd
import unicodedata
import re
import datetime
from difflib import SequenceMatcher
import io


def remove_accents(input_str):
  nfkd_form = unicodedata.normalize('NFKD', input_str)
  only_ascii = nfkd_form.encode('ASCII', 'ignore')
  return only_ascii.decode('utf-8')

def clean_string(input_str):
  input_str = remove_accents(input_str)
  input_str = re.sub('[^a-zA-Z0-9]+\W', ' ', input_str)
  input_str = re.sub('\(|\)', ' ', input_str)
  return input_str

def check_similarity(first_word, second_word):
  return SequenceMatcher(None, first_word, second_word).ratio()

def convertToSingleWords(lst):
  words = re.split(' |/',lst)
  word_list = []
  for word in words:
      if word.isupper():
          word = word.title()
      word_list.append(word) 
  return word_list

def addEntities(title, name, matchtype='full'):
  entities = []
  for i in re.finditer(name.lower(), title.lower()):
    if matchtype=='full':
      start_index = i.start()
    else:
      start_index = i.start()+1 # for partial match
    entity = (start_index, i.end(), "DESTINATION")
    entities.append(entity)
  return entities
  


def main(input_path:Path, output_path:Path):
  print("\n\n\n\n\n================================")
  print("INTPUT PATH: ", input_path)
  print("OUTPUT PATH: ", output_path)
  RAW_DATA = pd.read_json(input_path, 'r', 'utf-8')
  print("TOTAL DATA IN INPUT DATASET : ", len(RAW_DATA))
  count=0
  full_match_count=0
  partial_match_count=0
  no_match_count=0
  training_data=[]
  unmatched_data=[]
  print("START TIME : ", datetime.datetime.now())
  for raw in RAW_DATA:
    if raw['name'] is None:
      continue
    else:
      partial_match = False
      name = clean_string(raw['name'])
      title = clean_string(raw['title'])
      inputstring = title # + description
      if name in title:
        temp = (inputstring,addEntities(inputstring, name, "full"))
        training_data.append(temp)
        full_match_count = full_match_count + 1
      else:
        split_word_name = convertToSingleWords(name)
        split_word_title = convertToSingleWords(title)
        similar_word_in_title=""
        for word_title in split_word_title:
          for word_name in split_word_name:
            if(check_similarity(word_title.lower(), word_name.lower())>=0.7):
              partial_match = True
              similar_word_in_title = similar_word_in_title + " " + word_title
        if (partial_match):
          entity = addEntities(inputstring, similar_word_in_title, "partial")
          if len(entity)>0:
            temp = (inputstring, entity) # in partial case 2nd param will be from title itself
            training_data.append(temp)
            partial_match_count = partial_match_count + 1
          else:
            unmatch_str = "Need Research - Empty tuple "+ inputstring+ " | word name : ", name + "\n"
            unmatched_data.append(unmatch_str)
            no_match_count = no_match_count + 1 # but this must be corrected. For now, just for the sake of reconciliation
        
        else:
          unmatch_str = "Complete Unmatch for : " + raw['title'] + " which has a name " + raw['name'] + "\n"
          unmatched_data.append(unmatch_str) 
          no_match_count = no_match_count + 1
    count = count + 1

  
  print("END TIME : ", datetime.datetime.now())
  print("TOTAL TRAINING RECORDS : ", count)
  print("FULL MATCH RECORDS : ", full_match_count)
  print("PARTIAL MATCH RECORDS : ", partial_match_count)
  print("NO MATCH RECORDS : ", no_match_count)
  # print("TRAINING DATA: ",training_data)
  with open("unmatched_data_preview.txt", "w", newline='',encoding="utf-8") as file:
    str_dictionary = repr(training_data)
    file.write(str_dictionary)
    file.close()

  with open("unmatched_data_preview.txt", "w", newline='',encoding="utf-8") as f:
    str_dictionary_a = repr(unmatched_data)
    f.write(str_dictionary_a)
    f.close()

  # spacy.prefer_gpu()
  nlp = spacy.blank("en")
  # the DocBin will store the example documents
  doc_bin = DocBin()
  doc_count=0
  for text, annotations in training_data:
    doc = nlp(text)
    ents = []
    for start, end, label in annotations:
        span = doc.char_span(start, end, label=label)
        if doc_count<200:
          print("SPAN: " ,span , " | START : ", start , " | END : ", end , " | LABEL: ", label)
        if span is None:
          continue
        else: 
          ents.append(span)
          doc_count = doc_count + 1
    doc.ents = ents
    doc_bin.add(doc)
  doc_bin.to_disk(output_path)
  print("DOC COUNT INSIDE DOC BIN : ", doc_count)
  print(f"Processed {len(doc_bin)} | Document Location : {output_path}")


if __name__=="__main__":
  typer.run(main)
  
    




  