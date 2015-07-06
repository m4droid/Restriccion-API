# -*- coding: utf-8 -*-
from mock import patch
import moment
from pyquery import PyQuery as pq

from .base_tests import BaseTestCase
from restriccion_scl import CONFIG
from restriccion_scl.crawlers.uoct import UOCT_Crawler


class TestUoct_Crawler(BaseTestCase):

    def test_crawler_uoct_clean_digits_string_ok(self):
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('1-2-3'))

    def test_crawler_uoct_clean_digits_string_none_value(self):
        self.assertIsNone(UOCT_Crawler.clean_digits_string(None))

    def test_crawler_uoct_clean_digits_string_multiple_dash(self):
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('1-2--3'))
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('1---2-3'))

    def test_crawler_uoct_clean_digits_string_ends_dashes(self):
        # Single
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('1-2-3-'))
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('-1-2-3'))
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('-1-2-3-'))

        # Multiple
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('1-2-3--'))
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('--1-2-3'))
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('--1-2-3--'))

    def test_crawler_uoct_clean_digits_string_order(self):
        self.assertEqual('1-2-3', UOCT_Crawler.clean_digits_string('2-1-3'))

    def test_crawler_uoct_clean_digits_string_with_spaces(self):
        self.assertEqual('0-1-2-7-8-9', UOCT_Crawler.clean_digits_string('7-8-9-0 -1-2'))

    def test_crawler_uoct_clean_digits_string_text(self):
        self.assertEqual('', UOCT_Crawler.clean_digits_string('Sin restricción'))

    @patch('restriccion_scl.crawlers.uoct.moment.utcnow')
    def test_crawler_uoct_parse_file(self, mock_moment):
        mock_moment.side_effect = lambda: moment.utc('2015-06-21', '%Y-%m-%d')

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')

        new_restrictions = crawler.parse()
        self.assertEqual(list, type(new_restrictions))
        self.assertEqual(26, len(new_restrictions))

    @patch('restriccion_scl.crawlers.uoct.moment.utcnow')
    @patch('restriccion_scl.crawlers.uoct.pq')
    def test_crawler_uoct_parse_url(self, mock_pyquery, mock_moment):
        mock_moment.side_effect = lambda: moment.utc('2015-06-21', '%Y-%m-%d')

        mock_pyquery.side_effect = lambda **kw: pq(
            filename=self.get_fixture_file_path('uoct.cl_restriccion-vehicular_1.html').replace('file://', '')
        )

        new_restrictions = UOCT_Crawler().parse()
        self.assertEqual(list, type(new_restrictions))
        self.assertEqual(27, len(new_restrictions))

    @patch('restriccion_scl.crawlers.uoct.moment.utcnow')
    def test_crawler_uoct_parse_data_integrity(self, mock_moment):
        mock_moment.side_effect = lambda: moment.utc('2015-06-21', '%Y-%m-%d')

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        new_restrictions = crawler.parse()

        self.assertEqual(
            {
                'fecha': '2015-06-21',
                'hash': '5e15b0168c9978cb5a50ad4c27c8065942d7fd30',
                'estado': 'Preemergencia Ambiental',
                'sin_sello_verde': '3-4-5-6-7-8',
                'con_sello_verde': '0-9',
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            },
            new_restrictions[0]
        )

    @patch('restriccion_scl.crawlers.uoct.moment.utcnow')
    def test_crawler_uoct_parse_current_date_data(self, mock_moment):
        mock_moment.side_effect = lambda: moment.utc('2015-07-05', '%Y-%m-%d')

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_3.html')
        new_restrictions = crawler.parse()

        self.assertEqual(
            {
                'fecha': '2015-07-05',
                'hash': '435b759d0dcae07a5a87c3e27fc8d1c559f77e1e',
                'estado': 'Alerta Ambiental',
                'sin_sello_verde': '3-4',
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            },
            new_restrictions[0]
        )

        mock_moment.side_effect = lambda: moment.utc('2015-07-06', '%Y-%m-%d')
        new_restrictions = crawler.parse()

        self.assertEqual(
            {
                'fecha': '2015-07-06',
                'hash': '0df49f1c9fd9a59a44a05ed6e346720a61ecf399',
                'estado': 'Normal',
                'sin_sello_verde': '5-6-7-8',
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            },
            new_restrictions[0]
        )
