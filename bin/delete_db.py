# -*- coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parents[1]))


from anwatch.models import AmendementSummary, Amendement


AmendementSummary.delete().execute()
Amendement.delete().execute()
