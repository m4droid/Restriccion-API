# -*- coding: utf-8 -*-
from .base_report import BaseReport


class Restriction(BaseReport):

    @classmethod
    def get_mongo_collection(cls):
        return 'reports_restriction'

    @classmethod
    def get_fields(cls):
        return ['ciudad', 'fecha', 'sin_sello_verde', 'con_sello_verde']

    @classmethod
    def get_unique_fields(cls):
        return ['ciudad', 'fecha']
