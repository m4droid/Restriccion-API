# -*- coding: utf-8 -*-
import moment


class Restriction(object):

    @staticmethod
    def get(mongo_db, query=None, limit=10):
        if query is None:
            query = {}

        mongo_query = {'$query': query, '$orderby': {'fecha' : -1}}

        restrictions = []
        rows = mongo_db.restrictions.find(mongo_query, {'_id': 0}, limit=limit)
        for row in rows:
            restrictions.append(row)
        return restrictions

    @staticmethod
    def insert_many(mongo_db, restrictions_list):
        update_time = moment.now().isoformat()

        projection = {
            '_id': 0,
            'fecha': 1,
            'estado': 1,
            'sin_sello_verde': 1,
            'con_sello_verde': 1,
            'hash': 1
        }

        for restriction in restrictions_list:
            row = mongo_db.restrictions.find_one({'fecha': restriction['fecha']}, projection)

            if row == restriction:
                continue

            restriction['actualizacion'] = update_time

            if row is None:
                mongo_db.restrictions.insert_one(restriction)
            else:
                mongo_db.restrictions.update_one({'fecha': row['fecha']}, {'$set': restriction})

            if '_id' in restriction:
                del restriction['_id']
