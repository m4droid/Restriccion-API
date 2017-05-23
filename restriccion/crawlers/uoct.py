import re

import moment
from pyquery import PyQuery as pq

from restriccion import CONFIG

from ..models.air_quality import AirQualityReport
from ..models.restriction import RestrictionReport


class UOCT_Crawler(object):

    MONTHS = [
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Diciembre',
    ]

    url = 'http://www.uoct.cl/restriccion-vehicular/'

    def __init__(self):
        self.url = UOCT_Crawler.url

    def parse(self):
        reports = {'restriction': [], 'air_quality': []}

        if self.url.startswith('file://'):
            document = pq(filename=self.url.replace('file://', ''))
        else:
            document = pq(url=self.url)

        current_year = moment.utcnow().timezone(CONFIG['moment']['timezone']).format('YYYY')

        self._parse_day_report(reports, document)
        self._parse_historic_reports(reports, document, current_year)

        return reports

    @staticmethod
    def _parse_day_report(reports, document):

        # Current day info
        info = document('.eventslist .restriction h3')
        if len(info) != 2:
            return reports

        day_element = document('.events .eventstitle')

        month = UOCT_Crawler.MONTHS.index(day_element.find('h5')[1].text.strip()) + 1
        day = int(day_element.find('h4')[0].text.strip())

        date = moment.utcnow().timezone(CONFIG['moment']['timezone'])

        tomorrow = day_element.find('h5')[0].text.lower() == 'mañana'

        if tomorrow:
            date.add(days=1)

        if month != date.month or day != date.day:
            return reports

        air_quality_status = 'Normal'
        air_quality_element = document('.middleheader .restrictiontop a span')

        if len(air_quality_element) > 1 and len(air_quality_element[1].attrib['class']) > 0:
            air_quality_status = air_quality_element[1].text.strip()

        air_quality_report = AirQualityReport.dict(
            UOCT_Crawler.url,
            {
                'ciudad': 'Santiago',
                'fecha': date.format('YYYY-M-D'),
                'estado': air_quality_status
            }
        )
        UOCT_Crawler._insert_report_in_position(reports['air_quality'], air_quality_report)

        restriction_report = RestrictionReport.dict(
            UOCT_Crawler.url,
            {
                'ciudad': 'Santiago',
                'fecha': date.format('YYYY-M-D'),
                'sin_sello_verde': UOCT_Crawler.clean_digits_string(info[0].text),
                'con_sello_verde': UOCT_Crawler.clean_digits_string(info[1].text),
            }
        )
        UOCT_Crawler._insert_report_in_position(reports['restriction'], restriction_report)

    @staticmethod
    def _parse_historic_reports(reports, document, current_year):
        rows = document('.selecthistory #table-{0:s} tbody tr'.format(current_year))

        for row in rows[2:]:
            date_ = moment.date(row.find('td[3]').text.strip(), '%d-%m-%Y').format('YYYY-M-D')

            reports['air_quality'].append(AirQualityReport.dict(
                UOCT_Crawler.url,
                {
                    'ciudad': 'Santiago',
                    'fecha': date_,
                    'estado': row.find('td[1]').text.strip()
                }
            ))

            reports['restriction'].append(RestrictionReport.dict(
                UOCT_Crawler.url,
                {
                    'ciudad': 'Santiago',
                    'fecha': date_,
                    'sin_sello_verde': UOCT_Crawler.clean_digits_string(row.find('td[4]').text),
                    'con_sello_verde': UOCT_Crawler.clean_digits_string(row.find('td[5]').text),
                }
            ))

        reports['restriction'].sort(key=lambda r: r['fecha'], reverse=True)

    @staticmethod
    def _insert_report_in_position(reports_list, report):
        if len(reports_list) == 0:
            reports_list.append(report)
            return

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
