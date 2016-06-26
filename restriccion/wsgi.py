# -*- coding: utf-8 -*-
import json

from flask import Flask, request, Response
from flask_cors import CORS
import moment
import pymongo
from validate_email import validate_email

from restriccion import CONFIG
from restriccion.models.device import Device
from restriccion.models.restriction import Restriction


EMPTY_VALUES = [None, '']


mongo_client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
mongo_db = mongo_client[CONFIG['pymongo']['database']]

app = Flask(__name__)
cors = CORS(app)


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

    return json_response(Restriction.get(mongo_db, query))


@app.route("/0/dispositivos", methods=['GET'])
def devices_get():
    '''This method is only intended for devices with a "long"
    ID to check if they are registered'''

    device_type = request.args.get('tipo', '').strip()
    device_id = request.args.get('id', '').strip()
    delete_flag = request.args.get('borrar', '0')

    # Avoid getting emails database using bruteforce
    if '' in [device_type, device_id] or (device_type == 'email' and delete_flag == '0'):
        return json_response([], 404)

    devices = Device.get(mongo_db, device_type, device_id)

    if len(devices) == 0:
        return json_response(devices, 404)

    if delete_flag == '1':
        # Only emails allowed to do this
        if device_type == 'email' and validate_email(device_id):
            Device.delete_one(mongo_db, devices[0])
            devices[0]['mensaje'] = 'El dispositivo ha sido borrado con éxito'
        else:
            return json_response([], 400)

    return json_response(devices[0:1])


@app.route("/0/dispositivos", methods=['POST'])
def devices_post():
    device_type = request.form.get('tipo', '').strip()
    device_id = request.form.get('id', '').strip()

    if '' in [device_type, device_id]:
        return json_response({'status': 'error', 'mensaje': 'Faltan parámetros.'}, 400)

    model_response = Device.insert_one(mongo_db, device_type, device_id)
    if model_response['status'] == 'ok':
        return json_response(model_response['data'])
    else:
        return json_response(model_response, 400)
