#!/usr/bin/env python3
import sys

import pymongo

from restriccion import CONFIG
from restriccion.crawlers.uoct import UOCT_Crawler
from restriccion.models.device import Device
from restriccion.models.restriction import Restriction


def main(argv):
    mongo_client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
    mongo_db = mongo_client[CONFIG['pymongo']['database']]

    current_restrictions = Restriction.get(mongo_db)

    crawler = UOCT_Crawler()
    new_restrictions = crawler.parse()

    Restriction.insert_many(mongo_db, new_restrictions)

    if '--notify' in argv[1:]:
        _notify_to_devices(mongo_db, new_restrictions[0])
    elif '--notify-new' in argv[1:]:
        del current_restrictions[0]['actualizacion']
        if new_restrictions[0] != current_restrictions[0]:
            _notify_to_devices(mongo_db, new_restrictions[0])

    mongo_client.close()


def _notify_to_devices(mongo_db, data):
    data['tipo'] = 'restricciones'
    Device.notify(mongo_db, data, collapse_key='restricciones')


if __name__ == '__main__':
    main(sys.argv)
