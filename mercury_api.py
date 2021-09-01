import web
import json
import re
import requests
import spacy
import configparser

 
urls = (
    '/(.*)', 'DestinationRequestHandler' #all maps to destination request handler class
)
app = web.application(urls, globals())
 
 
class DestinationRequestHandler:

    """list suggested places"""
    def POST(self, collection):
        config = configparser.ConfigParser()
        config.read('./configs/api_config.cfg')
        model_folder = config.get('model_path','folder')
        model =  config.get('model_path','model_to_execute')
        
        nlp = spacy.load(R''+model_folder+model)
        
        itinerary_object = json.loads(web.data())
        suggestionsPlaces = []
        for itinerary_item in itinerary_object:
            input_string = itinerary_item['title']
            
            temp_string = input_string
            temp_string = re.sub(' - ', ' to ', temp_string)
            temp_string = re.sub(' via ', ' through ', temp_string)
            temp_string = re.sub(r"\([^()]*\)", "", temp_string)
            temp_string = re.sub(r'[^a-zA-Z0-9 \n\.]', '', temp_string)
            temp_string = re.sub(r'/', '', temp_string)
            
            doc = nlp(temp_string)
            doc.ents = set(doc.ents)
            place=[]
            for w in doc.ents:
                place.append(w.text)
            item = {
                    "product_id" : id,
                    "day" : itinerary_item['day'],
                    "input" : input_string, 
                    "temp_string" : temp_string,
                    "recommended_destination" : place
                }
            suggestionsPlaces.append(item)  
            
        return suggestionsPlaces

    """only for test purpose"""
    # def POST(self, collection):
    #     suggestionsPlaces = []
    #     nlp = spacy.load(R".\training\model-best")
    #     for id in range(3000, 3300):
    #         r = requests.get(url='https://www.bookmundi.com/ws/GetItineraryData?id=' + str(id))
    #         itinerary_object = r.json()
    #         if len(itinerary_object)>0:
    #             for itinerary_item in itinerary_object:
    #                 input_string = itinerary_item['title']
    #                 temp_string = input_string
    #                 temp_string = re.sub(' - ', ' to ', temp_string)
    #                 temp_string = re.sub(' via ', ' through ', temp_string)
    #                 temp_string = re.sub(r"\([^()]*\)", "", temp_string)
    #                 temp_string = re.sub(r'[^a-zA-Z0-9 \n\.]', '', temp_string)
    #                 temp_string = re.sub(r'/', '', temp_string)
                    
    #                 doc = nlp(temp_string)
    #                 doc.ents = set(doc.ents)
    #                 place=[]
    #                 for w in doc.ents:
    #                     place.append(w.text)
    #                 item = {
    #                         "product_id" : id,
    #                         "day" : itinerary_item['day'],
    #                         "input" : input_string, 
    #                         "temp_string" : temp_string,
    #                         "recommended_destination" : place
    #                     }
    #                 suggestionsPlaces.append(item)
            
    #     return suggestionsPlaces
 
 
if __name__ == "__main__":
    app.run()