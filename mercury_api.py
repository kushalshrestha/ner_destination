import web
import json
import re
import requests
import spacy
 
urls = (
    '/(.*)', 'DestinationRequestHandler' #all maps to hello class
)
app = web.application(urls, globals())
 
 
class DestinationRequestHandler:
    
    
    def GET(self, name):
        return name
    
    # def POST(self, collection):
    #     data = web.input()
    #     name, password = data.name, data.password
    #     return name, password
    #     return collection
    #     data = web.data()
    #     data_input = web.input()
    #     return data

    def POST(self, collection):
        nlp = spacy.load(R".\training\model-best")
        itinerary_object = json.loads(web.data())
        title_list = []
        suggestionsPlaces = []
        for itinerary_item in itinerary_object:
            
            input_string = itinerary_item['title']
            temp_string = input_string
            temp_string = re.sub(' - ', ' to ', temp_string)
            temp_string = re.sub(r'[0-9]', '', temp_string)
            temp_string = re.sub(r'/', '', temp_string)
            title_list.append(temp_string)
            doc = nlp(temp_string)
            doc.ents = set(doc.ents)
            
            for w in doc.ents:
                suggestionsPlaces.append((input_string, w.text))
            
        return suggestionsPlaces
 
 
if __name__ == "__main__":
    app.run()