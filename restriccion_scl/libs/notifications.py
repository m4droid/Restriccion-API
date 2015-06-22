from gcm import GCM
import moment
import pymongo

from restriccion_scl import CONFIG


def send_to_android_devices(device_list, data_dict):
    mongo_client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
    mongo_db = mongo_client[CONFIG['pymongo']['database']]

    gcm = GCM(CONFIG['notifications']['gcm']['api_key'])
    response = gcm.json_request(registration_ids=device_list, data=data_dict)

    # Delete not registered or invalid devices
    if 'errors' in response:
        device_ids = response['errors'].get('NotRegistered', [])
        device_ids += response['errors'].get('InvalidRegistration', [])
        mongo_db.devices.delete_many({'tipo': 'android', 'id': {'$in': device_ids}})

    current_datetime = moment.now().isoformat()

    # Delete old device IDs
    if 'canonical' in response:
        old_ids = []
        canonical_ids = []

        for old_id, canonical_id in response['canonical'].items():
            old_ids.append(old_id)
            canonical_ids.append(canonical_id)

        mongo_db.devices.delete_many({'tipo': 'android', 'id': {'$in': old_ids}})

        for id_ in canonical_ids:
            row = mongo_db.devices.find_one({'tipo': 'android', 'id': id_})

            if row is None:
                mongo_db.devices.insert_one({'tipo': 'android', 'id': id_, 'fecha_registro': current_datetime})
