# -*- coding: utf-8 -*-

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parents[1]))

from anpy.service import AmendementSearchService
from anwatch.logger_config import setup_logging
from anwatch.db import database
from anwatch.config import AMENDEMENT_PARAMS
from anwatch.crawler.amendement import download, parse_amendement
from anwatch.models import AmendementSummary, Amendement
from logging import getLogger

setup_logging()

LOGGER = getLogger('init_db')

database.create_tables([AmendementSummary, Amendement], safe=True)

service = AmendementSearchService()

total_count = service.total_count(**AMENDEMENT_PARAMS)

LOGGER.info("total count: %s", total_count)
count = 0
failed_amendements = []

for search_result in service.iterator(**AMENDEMENT_PARAMS):
    count += len(search_result.results)
    LOGGER.info("count: %s", count)

    ids = [am.id for am in search_result.results]
    ids_result = AmendementSummary.select(AmendementSummary.id).where(AmendementSummary.id.in_(ids)).execute()
    existing_ids = [row.id for row in ids_result]
    new_ids = list(set(ids) - set(existing_ids))

    for amendement_summary in search_result.results:
        if amendement_summary.id not in new_ids:
            continue

        AmendementSummary.create(**amendement_summary.__dict__)

    urls = [am.url_amend for am in search_result.results]
    urls_result = Amendement.select(Amendement.url).where(Amendement.url.in_(urls)).execute()
    existing_urls = [row.url for row in urls_result]
    new_urls = list(set(urls) - set(existing_urls))

    for amendement_summary in search_result.results:
        if amendement_summary.url_amend not in new_urls:
            continue

        try:
            parsed_response = download(amendement_summary.url_amend)
            amendement = parse_amendement(parsed_response.url, parsed_response.content)
            Amendement.create(**amendement.__dict__)
        except Exception as e:
            LOGGER.warn("failed to download and parse amendement %s: %s", amendement_summary.url_amend, e)
            time.sleep(10)

            failed_amendements.append(amendement_summary.url_amend)
            with open("failed_amendements.txt", "w") as f:
                f.write("\n".join(failed_amendements))
