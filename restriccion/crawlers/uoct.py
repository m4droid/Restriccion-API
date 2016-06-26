import re

import moment
from pyquery import PyQuery as pq

from restriccion import CONFIG
from ..models.restriction import Restriction


class UOCT_Crawler(object):

    url = 'http://www.uoct.cl/restriccion-vehicular/'

    def __init__(self):
        self.url = UOCT_Crawler.url

    def parse(self):
        if self.url.startswith('file://'):
            document = pq(filename=self.url.replace('file://', ''))
        else:
            document = pq(url=self.url)

        current_year = moment.utcnow().timezone(CONFIG['moment']['timezone']).format('YYYY')
        rows = document('.selecthistory #table-%s tbody tr' % current_year)

        raw_data = []
        for row in rows[2:]:
            raw_data.append(Restriction.dict(
                UOCT_Crawler.url,
                {
                    'ciudad': 'Santiago',
                    'fecha': moment.date(row.find('td[3]').text.strip(), '%d-%m-%Y').format('YYYY-M-D'),
                    'sin_sello_verde': self.clean_digits_string(row.find('td[4]').text),
                    'con_sello_verde': self.clean_digits_string(row.find('td[5]').text),
                }
            ))

        raw_data.sort(key=lambda r: r['fecha'], reverse=True)

        # Current day info
        info = document('.eventslist .restriction h3')
        if len(info) != 2:
            return raw_data

        data = Restriction.dict(
            UOCT_Crawler.url,
            {
                'ciudad': 'Santiago',
                'fecha': moment.utcnow().timezone(CONFIG['moment']['timezone']).format('YYYY-M-D'),
                'sin_sello_verde': self.clean_digits_string(info[0].text),
                'con_sello_verde': self.clean_digits_string(info[1].text),
            }
        )

        if len([r for r in raw_data if r['fecha'] == data['fecha']]) == 0:
            for i in range(len(raw_data)):
                if raw_data[i]['fecha'] < data['fecha']:
                    raw_data.insert(i, data)
                    break

        return raw_data

    @staticmethod
    def clean_digits_string(string):
        if string is None:
            return []

        string = re.sub(r'[^-\d]', '', string)
        string = re.sub(r'-+', '-', string)
        string = string.strip('-')

        if string == '':
            return []

        return sorted(set(string.split('-')))
