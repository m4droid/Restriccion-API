import hashlib
import re

import moment
import pymongo
from pyquery import PyQuery as pq

from restriccion_scl import CONFIG


class UOCT_Crawler(object):

    def __init__(self):
        self.url = CONFIG['crawlers_urls']['uoct']
        self.mongo_client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
        self.mongo_db = self.mongo_client[CONFIG['pymongo']['database']]

    def parse(self):
        if self.url.startswith('file://'):
            document = pq(filename=self.url.replace('file://', ''))
        else:
            document = pq(url=self.url)

        rows = document('.selecthistory #table-2015 tbody tr')

        raw_data = []
        for row in rows[2:]:
            data = {
                'estado': row.find('td[1]').text.strip(),
                'fecha': moment.date(row.find('td[3]').text.strip(), '%d-%m-%Y').format('YYYY-M-D'),
                'sin_sello_verde': self.clean_digits_string(row.find('td[4]').text),
                'con_sello_verde': self.clean_digits_string(row.find('td[5]').text),
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            }

            # Clear empty data
            for key in ['sin_sello_verde', 'con_sello_verde']:
                if data[key] is None or data[key] == '':
                    del data[key]

            # Hash data to detect changes
            sha1_message = hashlib.sha1()
            for key in ['fecha', 'estado', 'sin_sello_verde', 'con_sello_verde']:
                if key not in data.keys():
                    continue
                sha1_message.update(data[key].encode('utf-8'))

            data['hash'] = sha1_message.hexdigest()

            raw_data.append(data)

        return raw_data

    @staticmethod
    def clean_digits_string(string):
        if string is None:
            return string

        string = re.sub(' ', '', string)
        string = re.sub('-+', '-', string)
        string = string.strip('-')
        string = '-'.join(sorted(string.split('-')))

        return string
