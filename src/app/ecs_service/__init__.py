"""ecs_service package.

If you choose to deploy this service with vendored Python dependencies, they can
be placed under a local ``vendor/`` directory. This helper ensures that directory
is importable.
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
