# -*- coding: utf-8 -*-
import hashlib

import moment

from restriccion import CONFIG


class Restriction(object):

    @staticmethod
    def dict(city, date, with_green_seal, without_green_seal, source):
        data = {
            'ciudad': city,
            'fecha': date,
            'sin_sello_verde': with_green_seal,
            'con_sello_verde': without_green_seal,
            'fuente': source,
        }

        # Clear empty data
        for key in ['sin_sello_verde', 'con_sello_verde']:
            if data[key] is None or data[key] == '':
                data[key] = []

        # Hash data to detect changes
        sha1_message = hashlib.sha1()
        sha1_message.update(data['ciudad'].encode('utf-8'))
        sha1_message.update(data['fecha'].encode('utf-8'))
        sha1_message.update('-'.join(data['sin_sello_verde']).encode('utf-8'))
        sha1_message.update('-'.join(data['con_sello_verde']).encode('utf-8'))

        data['hash'] = sha1_message.hexdigest()
        return data

    @staticmethod
    def get(mongo_db, query=None, limit=10):
        if query is None:
            query = {}

        mongo_query = {'$query': query, '$orderby': {'fecha': -1}}

        restrictions = []
        rows = mongo_db.restrictions.find(mongo_query, {'_id': 0}, limit=limit)
        for row in rows:
            restrictions.append(row)
        return restrictions

    @staticmethod
    def insert_many(mongo_db, restrictions_list):
        update_time = moment.utcnow().timezone(CONFIG['moment']['timezone']).isoformat()

        projection = {
            '_id': 0,
            'fecha': 1,
            'sin_sello_verde': 1,
            'con_sello_verde': 1,
            'hash': 1,
            'fuente': 1,
            'ciudad': 1,
        }

        for restriction in restrictions_list:
            row = mongo_db.restrictions.find_one(
                {
                    'ciudad': restriction['ciudad'],
                    'fecha': restriction['fecha']
                },
                projection
            )

            if row == restriction:
                continue

            restriction['actualizacion'] = update_time

            if row is None:
                mongo_db.restrictions.insert_one(restriction)
            else:
                mongo_db.restrictions.update_one(
                    {
                        'ciudad': row['ciudad'],
                        'fecha': row['fecha']
                    },
                    {'$set': restriction}
                )

            if '_id' in restriction:
                del restriction['_id']
