"""example_api package.

This project installs Python dependencies *per Lambda* into a local ``vendor/``
directory during the CI/CD build (see ``pipeline/buildspec-serverless.yml``).

AWS Lambda includes only the deployment root (e.g., ``/var/task``) in ``sys.path``.
Because our third-party libraries for this Lambda are placed under
``src/app/example_api/vendor``, we add that directory to ``sys.path`` so imports
like ``import flask`` work at runtime.
"""

from __future__ import annotations

import os
import sys


def _add_vendor_to_path() -> None:
    here = os.path.dirname(__file__)
    vendor = os.path.join(here, "vendor")
    if os.path.isdir(vendor) and vendor not in sys.path:
        # Prepend so vendored deps win over any accidentally bundled versions
        sys.path.insert(0, vendor)


_add_vendor_to_path()
