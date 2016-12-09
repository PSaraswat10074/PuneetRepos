import json
from datetime import datetime
from google.cloud import datastore
from google.cloud import storage, exceptions
from google.cloud.storage import Blob
from flask import jsonify,Response

class Capital:

    def __init__(self):
        self.ds = datastore.Client(project="hackathon-team-008")
        self.gcs = storage.Client(project="hackathon-team-008")
        self.kind = "WorldCapital"

    def store_capital(self, id, js):
        key = self.ds.key(self.kind, int(id))
        entity = datastore.Entity(key)
       # js = json.dumps(capital)
        entity['id'] = int(id)
        entity['country'] = js['country']
        entity['name'] = js['name']
        entity['latitude'] = float(js['location']['latitude'])
        entity['longitude'] = float(js['location']['longitude'])        
        entity['countryCode'] = js['countryCode']
        entity['continent'] = js['continent']

        return self.ds.put(entity)

    def fetch_capitals(self, queryText=None, searchText=None):
        query = self.ds.query(kind=self.kind)
        results = list()
        if queryText:
            texts = queryText.split(":")
            for entity in query.fetch():
                if entity[texts[0]]== texts[1]:
                    key = self.ds.key(self.kind, int(entity['id']))
                    city = self.ds.get(key)
                    new_city = {}
                    new_city['id'] =  city['id']
                    new_city['country'] = city['country']
                    new_city['name'] = city['name']
                    x = { 'latitude' : city['latitude'],
                    'longitude' : city['longitude']}
                    new_city['location'] = x
                    new_city['countryCode'] = city['countryCode']
                    new_city['continent'] = city['continent']
                    results.append(new_city)
            return results                               
            #query.add_filter('country', '=', 'France')
            #query.add_filter(texts[0], '=', texts[1])
        elif searchText:
            for entity in query.fetch():
                for propertyItem in entity:
                    if entity[propertyItem]== searchText:
                        key = self.ds.key(self.kind, int(entity['id']))
                        city = self.ds.get(key)
                        new_city = {}
                        new_city['id'] =  city['id']
                        new_city['country'] = city['country']
                        new_city['name'] = city['name']
                        x = { 'latitude' : city['latitude'],
                        'longitude' : city['longitude']}
                        new_city['location'] = x
                        new_city['countryCode'] = city['countryCode']
                        new_city['continent'] = city['continent']
                        results.append(new_city)
            return results
        query.order = ['id']
        return self.get_query_results(query)
    
    def fetch_capital(self, id):
        try:
            key = self.ds.key(self.kind, int(id))
            city = self.ds.get(key)
            new_city = {}
            new_city['id'] =  city['id']
            new_city['country'] = city['country']
            new_city['name'] = city['name']
            x = { 'latitude' : city['latitude'],
                'longitude' : city['longitude']}
            new_city['location'] = x
            new_city['countryCode'] = city['countryCode']
            new_city['continent'] = city['continent']
            return json.dumps(new_city)  
        except:
            return "404"


    def fetch_capitalDel(self, id):
        try:
            key = self.ds.key(self.kind, int(id))
            city = self.ds.get(key)
            self.ds.delete(city.key)
            return jsonify({"code":0, "message": " found"}),200
        except:
            return jsonify({"code":0, "message": "no found"}),404
  
    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results

    def fetch_capitalDelAll(self):
        query = self.ds.query(kind=self.kind)
        for entity in query.fetch():     
            self.ds.delete(entity.key)
            return jsonify({"code":0, "message": " found"}),200
        return jsonify({"code":0, "message": "no found"}),404
    
    def store(self, bucket_name, id, entity):
        bucket_exists = self.check_bucket(bucket_name)

        if bucket_exists is not None and not bucket_exists:
            try:
                print ('creating bucket {}'.format(bucket_name))
                bucket = self.gcs.create_bucket(bucket_name)
                blob = Blob(id, bucket)
                js= json.dumps(entity)
                resp = Response(js, status=200, mimetype='application/json')
                blob.upload_from_string(entity) 
            except Exception as e:
                print "Error: Create bucket Exception"
                print e
                return None
        else:
            bucket = self.gcs.get_bucket(bucket_name)
            blob = Blob(id, bucket)
            js= json.dumps(entity)
            resp = Response(js, status=200, mimetype='application/json')
            blob.upload_from_string(entity)      

        return 200

    def check_bucket(self, bucket_name):
        try:
            self.gcs.get_bucket(bucket_name)
            return True
        except exceptions.NotFound:
            print ('Error: Bucket {} does not exists.'.format(bucket_name))
            return False
        except exceptions.BadRequest:
            print ('Error: Invalid bucket name {}'.format(bucket_name))
            return None
        except exceptions.Forbidden:
            print ('Error: Forbidden, Access denied for bucket {}'.format(bucket_name))
            return None 

   

