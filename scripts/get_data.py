#!/usr/bin/env python3
import pymongo

from restriccion_scl import CONFIG
from restriccion_scl.crawlers.uoct import UOCT_Crawler
from restriccion_scl.models.restriction import Restriction


mongo_client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
mongo_db = mongo_client[CONFIG['pymongo']['database']]

crawler = UOCT_Crawler()
restrictions = crawler.parse()

Restriction.insert_many(mongo_db, restrictions)

mongo_client.close()
