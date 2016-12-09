"""Main Entrypoint for the Application"""

import logging
import json
import base64

from flask import Flask, request
from flask import Blueprint, render_template, request, redirect, url_for, Response
from flask import jsonify
import worldcapitals
from google.cloud import pubsub
import googlemaps
app = Flask(__name__)


@app.route('/')
def hello_world():
    """hello world"""
    return 'Hello From Seisable!'

@app.route('/api/status', methods=['GET'])
def status():
    """dumps a received pubsub message to the log"""

    if request.method == 'GET':
        data = {"insert": True, "fetch": True, "delete": True, "list": True, "query":True, "search": True, "pubsub": True, "storage": True}
 
    return jsonify(data),200

@app.route('/api/capitals', methods=['GET'])
def list_capitals(): 
    capital = worldcapitals.Capital()
    query = request.args.get('query')
    search= request.args.get('search')
    results = capital.fetch_capitals(query, search)
    js = json.dumps(results)
    resp = Response(js, status=200, mimetype='application/json')
   
    return resp
	
@app.route('/api/capitals/html', methods=['GET'])
def list_capitals_UI(): 
    capital = worldcapitals.Capital()
    query = request.args.get('query')
    search= request.args.get('search')
    results = capital.fetch_capitals(query, search)

    list_to_be_sorted = []
    countries = []
    for entity in results:
        #determine uniqueness
        country = entity['country']
        if country in countries:
            continue
        countries.append(country)
        capital = entity['name']
        list_to_be_sorted.append({'country' : country, 'name' : capital})
        
    newlist = sorted(list_to_be_sorted, key=lambda k: k['country'])

    for i in newlist:
        print i['country']

    js = json.dumps(newlist)
    resp = Response(js, status=200, mimetype='application/json')
   
    return render_template('index.html', results=newlist)

@app.route('/api/capitals/maps', methods=['GET'])
def list_capitals_maps(): 
    #return render_template('maps.html')
    capital = worldcapitals.Capital()
    results = capital.fetch_capitals()

    latlongs = []
    countries = []
    for entity in results:
        #determine uniqueness
        country = entity['country']
        if country in countries:
            continue
        countries.append(country)
        lat = entity['latitude']
        lon = entity['longitude']
        latlongs.append({'lat' : lat, 'lon' : lon})

    return render_template("maps.html", results=latlongs)

@app.route('/api/capitals/<id>', methods=['PUT','DELETE'])
def put_captial(id):
    if request.method == 'PUT':
        data = request.get_json()
        capital = worldcapitals.Capital()
        store = capital.store_capital(id, data)
        resp = Response(store, status=200, mimetype='application/json')
        return resp
    elif request.method == 'DELETE':
        capital = worldcapitals.Capital()
        return capital.fetch_capitalDel(id)

@app.route('/api/capitals/<id>/', methods=['GET'])
def get_captial(id):
    capital = worldcapitals.Capital()
    results = capital.fetch_capital(id)
    if(results=="404"):
            return  jsonify({"code":0, "message": "no found"}),404
    #js = json.dumps(results)
    resp = Response(results, status=200, mimetype='application/json')
    return resp 

@app.route('/api/capitals/<id>/store', methods=['POST'])
def store_captial(id):
        data = request.get_json()
        capital = worldcapitals.Capital()
        results = capital.fetch_capital(id)
        if(results=="404"):
            return  jsonify({"code":0, "message": "no found"}),404        
        capital = capital.store(data['bucket'], id, results)
        return jsonify({"code":0, "message": "found"}),200

@app.route('/api/capitals/<id>/publish', methods=['POST'])
def publish_captial(id):
    try:
        data = request.get_json()
        topicName= data['topic']
        texts= topicName.split('/')
        projectName= texts[1]
        api = pubsub.Client(project=projectName)
        capital = worldcapitals.Capital()
        message = capital.fetch_capital(id)
        if message=="404":
            print "id not found"
            return jsonify({"code":0, "message": "not found"}),404
        try:
            print "before topic"
            print texts[-1]
            topic = api.topic(texts[-1])
            print "post topic"
            messageId= topic.publish(message)
            print messageId
            return jsonify({"messageId":int(messageId)}),200
        except:
            return jsonify({"code":0, "message": "not found"}),404
        #Topic=api.topic(topicName)
        #Topic.publish(message)
        return jsonify({"code":0, "message": "not found"}),404       
    except Exception as e:
            print e
            print "hihihi"
            return jsonify({"code":0, "message": " not found"}),404
        
@app.route('/api/capitals', methods=['DELETE'])
def put_captial_all():
        capital = worldcapitals.Capital()
        return capital.fetch_capitalDelAll()

@app.errorhandler(500)
def server_error(err):
    """Error handler"""
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(err), 500


if __name__ == '__main__':
    # Used for running locally
    app.run(host='127.0.0.1', port=8080, debug=True)
