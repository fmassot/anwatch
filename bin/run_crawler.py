# -*- coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parents[1]))

from anwatch.logger_config import setup_logging
from anwatch.crawler.amendement import crawl_amendement_summaries

setup_logging()
crawl_amendement_summaries()
