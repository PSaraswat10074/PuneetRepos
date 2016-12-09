from flask import Blueprint, render_template, request, redirect, url_for, Response

import json
import worldcapitals


api = Blueprint('worldcapitals', __name__)

# api routes


@api.route('/api/status', methods=['GET'])
def get_status():
    data = {"insert": True, "fetch": False, "delete": False, "list": True}
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    return resp


@api.route('/api/capitals', methods=['GET'])
def list_capitals():
	capital = worldcapitals.Capital()
	results = capital.fetch_capitals()
	js = json.dumps(results)
	resp = Response(js, status=200, mimetype='application/json')
	return resp
	
@api.route('/api/capitals/<id>', methods=['PUT'])
def put_captial(id):
	data = request.data
	capital = worldcapitals.Capital()
	store = capital.store_capital(id, data)
	resp = Response(store, status=200, mimetype='application/json')
	return resp
	
	

