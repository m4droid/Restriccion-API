# -*- coding: utf-8 -*-
import moment
from validate_email import validate_email

from restriccion_scl.libs.notifications import send_to_android_devices, send_to_email_addresses


class Device(object):

    ALLOWED_TYPES = ['email', 'android']

    @staticmethod
    def get(mongo_db, type_=None, id_=None):
        if None in [type_, id_]:
            return []

        row = mongo_db.devices.find_one({'tipo': type_, 'id': id_}, {'_id': 0})
        if row is not None:
            return [row]
        return []

    @staticmethod
    def insert_one(mongo_db, type_, id_):
        if type_ not in Device.ALLOWED_TYPES:
            return {'status': 'error', 'mensaje': 'Tipo de dispositivo no permitido.'}

        if type_ == 'email' and not validate_email(id_):
            return {'status': 'error', 'mensaje': 'Email inválido'}

        row = mongo_db.devices.find_one({'tipo': type_, 'id': id_})
        if row is None:
            data = {
                'tipo': type_,
                'id': id_,
                'fecha_registro': moment.now().isoformat()
            }
            mongo_db.devices.insert_one(data)
        else:
            data = row

        if '_id' in data:
            del data['_id']

        return {'status': 'ok', 'data': data}

    @staticmethod
    def delete_one(mongo_db, device_data):
        mongo_db.devices.delete_one({'tipo': device_data['tipo'], 'id': device_data['id']})

    @staticmethod
    def notify(mongo_db, data):
        Device._notify_to_android_devices(mongo_db, data)
        Device._notify_to_email_addresses(mongo_db, data)

    @staticmethod
    def _notify_to_email_addresses(mongo_db, data):
        devices = []
        rows = mongo_db.devices.find({'tipo': 'email'}, {'_id': 0, 'id': 1})
        for row in rows:
            devices.append(row['id'])
        send_to_email_addresses(devices, data)

    @staticmethod
    def _notify_to_android_devices(mongo_db, data):
        devices = []
        rows = mongo_db.devices.find({'tipo': 'android'}, {'_id': 0, 'id': 1})
        for row in rows:
            devices.append(row['id'])
        devices_ok, devices_to_remove = send_to_android_devices(devices, data)

        mongo_db.devices.delete_many({'tipo': 'android', 'id': {'$in': devices_to_remove}})

        for device_ok_id in devices_ok:
            row = mongo_db.devices.find_one({'tipo': 'android', 'id': device_ok_id})

            if row is None:
                Device.insert_one(mongo_db, 'android', device_ok_id)

        return True
