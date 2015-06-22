import json

from flask import Flask, request
import moment
import pymongo

from restriccion_scl import CONFIG


client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
db = client[CONFIG['pymongo']['database']]

app = Flask(__name__)

@app.route("/registro")
def registry():
    date = request.args.get('fecha', None)

    data = []
    query = {}
    if date is not None:
        try:
            date = moment.date(date.strip(), '%Y-%m-%d').format('YYYY-M-D')
            query = {'fecha': date}
        except ValueError:
            return json.dumps(data)

    rows = db.registro.find(query, {'_id': 0})

    if rows is None:
        return json.dumps(data)

    for row in rows:
        data.append(row)

    return json.dumps(data)
