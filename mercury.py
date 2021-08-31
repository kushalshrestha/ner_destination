import spacy
import requests
import re


id='5757'
r = requests.get(url='https://www.bookmundi.com/ws/GetItineraryData?id=' + id)
jsonObject = r.json();
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)


suggestions = []

nlp1 = spacy.load(R".\training\model-last") #load the best model

doc = nlp1("Kathmandu Trek to Goa to Pheriche (4,320 m\/14,173 ft.)") # input sample text

for key in jsonObject:
    # string = remove_tags(jsonObject[key])
    # string = jsonObject[key]

    string = key['title'] + ' '+key['description']
    string = re.sub(' - ', ' to ', string)
    print(key['title'])
    doc = nlp1(string)
    doc.ents = set(doc.ents)
    suggestionsPlaces = []
    for w in doc.ents:
        suggestionsPlaces.append(w.text)
    if len(suggestionsPlaces) > 0:
        suggestionsPlaces = set(suggestionsPlaces)
        suggestions.append(suggestionsPlaces)
    else:
        suggestions.append({})
print(suggestions)

print(doc.ents)

# spacy.displacy.render(doc, style="ent", jupyter=True) # display in Jupyter
