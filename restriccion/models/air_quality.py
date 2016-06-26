# -*- coding: utf-8 -*-
from .base_report import BaseReport


class AirQuality(BaseReport):

    @staticmethod
    def get_mongo_collection():
        return 'reports_air_quality'

    @staticmethod
    def get_fields():
        return ['ciudad', 'fecha', 'estado']

    @staticmethod
    def get_unique_fields():
        return ['ciudad', 'fecha']
