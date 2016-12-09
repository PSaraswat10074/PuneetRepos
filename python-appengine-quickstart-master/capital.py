import json
from datetime import datetime
from google.cloud import datastore


class Capital:

    def __init__(self):
        self.ds = datastore.Client(project="bootcamp-bplost")
        self.kind = "WorldCapital"

    def store_capital(self, id, capital):
        key = self.ds.key(self.kind)
        entity = datastore.Entity(key)
        js = json.dumps(capital)
        entity['id'] = id
        entity['capital_data'] = js

        return self.ds.put(entity)

    def fetch_capitals(self):
        query = self.ds.query(kind=self.kind)
        query.order = ['id']
        return self.get_query_results(query)

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results
		
	def delete_capital(self, id):
		return None

