from requests import status_codes
import web
import json
import re
import requests
import spacy
import configparser
from web import webapi


from web.webapi import BadRequest


 
urls = (
    '/(.*)', 'DestinationRequestHandler' #all maps to destination request handler class
)
# Start web server
app = web.application(urls, globals())
web.header( 'Content-Type',
            'application/json' )
 
 
class DestinationRequestHandler:
    def POST(self, collection):
        model = self.__get_config()
        nlp = spacy.load(model)
        itinerary_object = json.loads(web.data())
        response_data = []
        try:
            for itinerary_item in itinerary_object:
                input_string = self.__clean_text(itinerary_item['title'])
                day = itinerary_item['day']
                doc = nlp(input_string)
                doc.ents = set(doc.ents)
                place=[]
                for w in doc.ents:
                    place.append(w.text)
                item = {
                        "day" : day,
                        "input" : itinerary_item['title'], 
                        "temp_string" : input_string,
                        "recommended_destination" : place
                    }
                response_data.append(item)
            return json.dumps(response_data)
        except :
            raise web.badrequest
            # raise NotFound(404, "Sorry, the page you were looking for was not found.")
 
    def __get_config(self):
        config = configparser.ConfigParser()
        config.read('./configs/api_config.cfg')
        model_folder = config.get('model_path','folder')
        model = config.get('model_path','model_to_execute')
        return model_folder + model

    def __clean_text(self, input_string):
        temp_string = input_string
        temp_string = re.sub(' - ', ' to ', temp_string)
        temp_string = re.sub(' via ', ' through ', temp_string)
        temp_string = re.sub(r"\([^()]*\)", "", temp_string)
        temp_string = re.sub(r'[^a-zA-Z0-9 \n\.]', '', temp_string)
        temp_string = re.sub(r'/', '', temp_string)
        return temp_string

    def notfound(self):
        return web.notfound
        return web.notfound("Sorry, the page you were looking for was not found.")
    
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