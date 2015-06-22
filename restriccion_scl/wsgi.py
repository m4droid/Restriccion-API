import json

from flask import Flask, request
import moment
import pymongo

from restriccion_scl import CONFIG


client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
db = client[CONFIG['pymongo']['database']]

app = Flask(__name__)

def json_response(data, status_code=200):
    return json.dumps(data), status_code, {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/0/registro")
def registry():
    date = request.args.get('fecha', None)

    data = []
    query = {}
    if date is not None:
        try:
            date = moment.date(date.strip(), '%Y-%m-%d').format('YYYY-M-D')
            query = {'fecha': date}
        except ValueError:
            return json_response(data, status_code=400)

    rows = db.restrictions.find({'$query': query, '$orderby': {'fecha' : -1}}, {'_id': 0})

    for row in rows:
        data.append(row)

    return json_response(data)
