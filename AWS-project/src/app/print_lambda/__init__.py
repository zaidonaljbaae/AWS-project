"""print_lambda package.

Dependencies for this Lambda are vendored into ``vendor/`` during the build
(see ``pipeline/buildspec-serverless.yml``). We add ``vendor/`` to ``sys.path``
so third-party imports resolve correctly in AWS Lambda.
"""

from __future__ import annotations

import os
import sys


def _add_vendor_to_path() -> None:
    here = os.path.dirname(__file__)
    vendor = os.path.join(here, "vendor")
    if os.path.isdir(vendor) and vendor not in sys.path:
        sys.path.insert(0, vendor)


_add_vendor_to_path()
