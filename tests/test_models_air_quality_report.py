from unittest.mock import patch

import moment

from .base_tests import BaseTestCase

from restriccion.crawlers.uoct import UOCT_Crawler
from restriccion.models.air_quality import AirQualityReport


class TestModelsAirQuality(BaseTestCase):

    @patch('restriccion.models.base_report.moment.utcnow')
    def test_models_restriction_get(self, mock_moment):
        mock_datetime = moment.utc('2015-06-21', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')

        AirQualityReport.insert_many(self.mongo_db, crawler.parse()['air_quality'])

        air_quality_reports = AirQualityReport.get(self.mongo_db)
        self.assertEqual(10, len(air_quality_reports))
        self.assertEqual(
            {
                'ciudad': 'Santiago',
                'fecha': '2015-06-21',
                'hash': '81ec93a759e6d309a135fa7af1b87bdff77b5459',
                'estado': 'Preemergencia Ambiental',
                'actualizacion': mock_datetime.isoformat(),
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            },
            air_quality_reports[0]
        )
