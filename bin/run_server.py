# -*- coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parents[1]))


from anwatch.logger_config import setup_logging
from anwatch.server.main import app


setup_logging()
app.run()