"""Doctest utils (moved to test2doc)"""

from contextlib import suppress

with suppress(ImportError, ModuleNotFoundError):
    from test2doc.doctest_utils import *

