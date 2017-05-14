# -*- coding: utf-8 -*-
import collections
import hashlib

import moment

from restriccion import CONFIG


class BaseReport(object):

    @classmethod
    def get_mongo_collection(cls):
        raise NotImplementedError()

    @classmethod
    def get_fields(cls):
        raise NotImplementedError()

    @classmethod
    def get_unique_fields(cls):
        raise NotImplementedError()

    @classmethod
    def dict(cls, source, data):
        new_dict = {}

        fields = cls.get_fields()

        for field in fields:
            new_dict[field] = data[field]

        # Hash data to detect changes
        sha1_message = hashlib.sha1()
        for field in fields:
            if isinstance(data[field], collections.Hashable):
                string = data[field]
            else:
                string = str(data[field])
            sha1_message.update(string.encode('utf-8'))

        new_dict['hash'] = sha1_message.hexdigest()
        new_dict['fuente'] = source

        return new_dict

    @classmethod
    def get(cls, mongo_db, query=None, limit=10):
        if query is None:
            query = {}

        mongo_query = {
            '$query': query,
            '$orderby': {field: -1 for field in cls.get_unique_fields()}
        }

        reports = []
        rows = mongo_db[cls.get_mongo_collection()].find(
            mongo_query,
            {'_id': 0},
            limit=limit
        )
        for row in rows:
            reports.append(row)
        return reports

    @classmethod
    def insert_many(cls, mongo_db, reports):
        update_time = moment.utcnow().timezone(CONFIG['moment']['timezone']).isoformat()

        projection = {
            '_id': 0,
            'hash': 1,
        }
        for field in ['hash', 'fuente'] + list(cls.get_fields()):
            projection[field] = 1

        class_collection = cls.get_mongo_collection()
        unique_fields = cls.get_unique_fields()

        for report in reports:
            find_query = {field: report[field] for field in unique_fields}
            row = mongo_db[class_collection].find_one(find_query, projection)

            if row == report:
                continue

            report['actualizacion'] = update_time

            if row is None:
                mongo_db[class_collection].insert_one(report)
            else:
                update_query = {field: row[field] for field in unique_fields}

                mongo_db[class_collection].update_one(
                    update_query,
                    {'$set': report}
                )

            if '_id' in report:
                del report['_id']
