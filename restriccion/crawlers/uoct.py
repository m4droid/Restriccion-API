import re

import moment
from pyquery import PyQuery as pq

from restriccion import CONFIG
from ..models.air_quality import AirQuality
from ..models.restriction import Restriction


class UOCT_Crawler(object):

    url = 'http://www.uoct.cl/restriccion-vehicular/'

    def __init__(self):
        self.url = UOCT_Crawler.url

    def parse(self):
        reports = {'restrictions': [], 'air_quality': []}

        if self.url.startswith('file://'):
            document = pq(filename=self.url.replace('file://', ''))
        else:
            document = pq(url=self.url)

        current_year = moment.utcnow().timezone(CONFIG['moment']['timezone']).format('YYYY')
        rows = document('.selecthistory #table-%s tbody tr' % current_year)

        for row in rows[2:]:
            date_ = moment.date(row.find('td[3]').text.strip(), '%d-%m-%Y').format('YYYY-M-D')
            reports['air_quality'].append(AirQuality.dict(
                UOCT_Crawler.url,
                {
                    'ciudad': 'Santiago',
                    'fecha': date_,
                    'estado': row.find('td[1]').text.strip()
                }
            ))

            reports['restrictions'].append(Restriction.dict(
                UOCT_Crawler.url,
                {
                    'ciudad': 'Santiago',
                    'fecha': date_,
                    'sin_sello_verde': self.clean_digits_string(row.find('td[4]').text),
                    'con_sello_verde': self.clean_digits_string(row.find('td[5]').text),
                }
            ))

        reports['restrictions'].sort(key=lambda r: r['fecha'], reverse=True)

        # Current day info
        info = document('.eventslist .restriction h3')
        if len(info) != 2:
            return reports

        date_ = moment.utcnow().timezone(CONFIG['moment']['timezone']).format('YYYY-M-D')

        air_quality = AirQuality.dict(
            UOCT_Crawler.url,
            {
                'ciudad': 'Santiago',
                'fecha': date_,
                'estado': 'Normal'
            }
        )
        self.insert_report_in_position(reports['air_quality'], air_quality)

        restriction = Restriction.dict(
            UOCT_Crawler.url,
            {
                'ciudad': 'Santiago',
                'fecha': date_,
                'sin_sello_verde': self.clean_digits_string(info[0].text),
                'con_sello_verde': self.clean_digits_string(info[1].text),
            }
        )
        self.insert_report_in_position(reports['restrictions'], restriction)

        return reports

    @staticmethod
    def insert_report_in_position(reports_list, report):
        # If not in list by date
        if len([r for r in reports_list if r['fecha'] == report['fecha']]) == 0:
            for i in range(len(reports_list)):
                if reports_list[i]['fecha'] < report['fecha']:
                    reports_list.insert(i, report)
                    break

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
