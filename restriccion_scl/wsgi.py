import json

from flask import Flask, request, Response
import moment
import pymongo

from restriccion_scl import CONFIG


ALLOWED_DEVICE_TYPES = ['android']
EMPTY_VALUES = [None, '']


client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
db = client[CONFIG['pymongo']['database']]

app = Flask(__name__)

def json_response(data, status_code=200):
    response = Response(response=json.dumps(data), mimetype='application/json')
    response.status_code = status_code
    return response

@app.route("/0/restricciones", methods=['GET'])
def restrictions_get():
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

@app.route("/0/dispositivos", methods=['GET'])
def devices_get():
    device_type = request.args.get('tipo', None)
    device_id = request.args.get('id', None)

    if device_type not in ALLOWED_DEVICE_TYPES \
        or device_id in EMPTY_VALUES:
        return json_response([], 400)

    row = db.devices.find_one({'tipo': device_type.strip(), 'id': device_id.strip()}, {'_id': 0})

    if row is None:
        return json_response([], 404)

    return json_response([row])

@app.route("/0/dispositivos", methods=['POST'])
def devices_post():
    device_type = request.form.get('tipo', None)
    device_id = request.form.get('id', None)

    if device_type not in ALLOWED_DEVICE_TYPES \
        or device_id in EMPTY_VALUES:
        return json_response([], 400)

    query = {'tipo': device_type.strip(), 'id': device_id.strip()}
    row = db.devices.find_one(query, {'_id': 0})

    data = dict(query)
    data['fecha_registro'] = moment.now().isoformat()
    if row is None:
        db.devices.insert_one(data)
    else:
        db.devices.update_one(query, {'$set': data})
    if '_id' in data:
        del data['_id']
    return json_response([data], 200)
