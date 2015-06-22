#!/usr/bin/env python3
import os

from restriccion_scl.crawlers.uoct import UOCT_Crawler


crawler = UOCT_Crawler()
crawler.parse()
