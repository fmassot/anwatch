# -*- coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parents[1]))

from anpy.service import AmendementSearchService
from anwatch.logger_config import setup_logging
from anwatch.db import database
from anwatch.config import AMENDEMENT_PARAMS
from anwatch.crawler.amendement import download_and_parse_amendement
from anwatch.models import AmendementSummary, Amendement
from logging import getLogger

setup_logging()

LOGGER = getLogger('init_db')

database.create_tables([AmendementSummary, Amendement], safe=True)

service = AmendementSearchService()

total_count = service.total_count(**AMENDEMENT_PARAMS)

LOGGER.info("total count: %s", total_count)
count = 0


for search_result in service.iterator(**AMENDEMENT_PARAMS):
    count += len(search_result.results)
    LOGGER.info("count: %s", count)

    for amendement_summary in search_result.results:
        if AmendementSummary.select().where(AmendementSummary.id == amendement_summary.id).count() == 0:
            AmendementSummary.create(**amendement_summary.__dict__)

        if Amendement.select().where(Amendement.url == amendement_summary.url_amend).count() == 0:
            amendement = download_and_parse_amendement(amendement_summary.url_amend)
            Amendement.create(**amendement.__dict__)
