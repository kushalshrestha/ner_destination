from requests import status_codes
import web
import json
import re
import requests
import spacy
import configparser
from web import webapi
from collections import defaultdict
import unicodedata


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
        beam_width = 16
        beam_density = 0.0001
        model = self.__get_config()
        nlp = spacy.load(model)
        itinerary_object = json.loads(web.data())
        response_data = []
        try:
            for itinerary_item in itinerary_object:
                input_string = self.__clean_text(itinerary_item['title'])
                day = itinerary_item['day']
                docs = nlp(input_string)
                
                beams = nlp.get_pipe("ner").beam_parse([docs], beam_width = beam_width, beam_density = beam_density)
                
                entity_scores = defaultdict(float)
                
                for beam in beams:
                    for score, ents in nlp.get_pipe("ner").moves.get_beam_parses(beam):
                        for start, end, label in ents:
                            entity_scores[(start, end, label)] += score
                place = []
                for key in entity_scores:
                    start, end, label = key
                    score = entity_scores[key]
                    output_string = docs[start:end]
                    if(score>0):
                        place.append({"name" : output_string, "score" : score})
                item = {
                            "day" : day,
                            "input" : itinerary_item['title'], 
                            "temp_string" : input_string,
                            "recommended_destination" : place
                        }
                response_data.append(item)
            return response_data
        except:
            raise webapi.badrequest
 
    def __get_config(self):
        config = configparser.ConfigParser()
        config.read('./configs/api_config.cfg')
        model_folder = config.get('model_path','folder')
        model = config.get('model_path','model_to_execute')
        return model_folder + model

    def __clean_text(self, input_string):
        temp_string = input_string
        temp_string = unicodedata.normalize('NFKD', temp_string).encode('ascii', 'ignore').decode('utf-8')
        temp_string = re.sub(' - ', ' to ', temp_string)
        temp_string = re.sub(r"\([^()]*\)", "", temp_string)
        temp_string = re.sub(' via ', ' through ', temp_string)
        temp_string = re.sub('/', ' to ', temp_string)
        temp_string = re.sub(r"\([^()]*\)", "", temp_string)
        temp_string = re.sub(r'[^a-zA-Z0-9 \n\.]', '', temp_string)
        temp_string = re.sub(r'/', ' ', temp_string)
        return temp_string

    """only for test purpose"""
    # def POST(self, collection):
    #     suggestionsPlaces = []
    #     beam_width = 16
    #     beam_density = 0.0001
    #     nlp = spacy.load(R".\training\model-best")
    #     response_data=[]
    #     for id in range(4000, 5800):
    #         print("PRODUCT ID : ", id)
    #         r = requests.get(url='https://www.bookmundi.com/ws/GetItineraryData?id=' + str(id))
    #         itinerary_object = r.json()
    #         if len(itinerary_object)>0:
    #             for itinerary_item in itinerary_object:
    #                 input_string = self.__clean_text(itinerary_item['title'])
    #                 day = itinerary_item['day']
    #                 docs = nlp(input_string)
                    
    #                 beams = nlp.get_pipe("ner").beam_parse([docs], beam_width = beam_width, beam_density = beam_density)
                     
    #                 entity_scores = defaultdict(float)
                    
    #                 for beam in beams:
    #                     for score, ents in nlp.get_pipe("ner").moves.get_beam_parses(beam):
    #                         for start, end, label in ents:
    #                             entity_scores[(start, end, label)] += score
    #                 place = []
    #                 for key in entity_scores:
    #                     start, end, label = key
    #                     score = entity_scores[key]*100
    #                     output_string = docs[start:end]
    #                     print(output_string)
    #                     if(score>0):
    #                         place.append({"name" : output_string, "score" : score})
    #                 item = {
    #                             "product_id" : id,
    #                             "day" : day,
    #                             "input" : itinerary_item['title'], 
    #                             "temp_string" : input_string,
    #                             "recommended_destination" : place
    #                         }
    #                 response_data.append(item)
    #     return response_data


    

if __name__ == "__main__":
    app.run()