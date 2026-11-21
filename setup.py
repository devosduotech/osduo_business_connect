import re
from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent

install_requires = (ROOT / "requirements.txt").read_text(encoding="utf-8").strip().split("\n")

# Single source of truth: keep setup.py in step with the app version so the
# stale hardcoded version does not drift again at release time.
version_source = (ROOT / "osduo_business_connect" / "__init__.py").read_text(encoding="utf-8")
version_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', version_source, re.M)
if not version_match:
    raise RuntimeError("Unable to find __version__ in osduo_business_connect/__init__.py")
version = version_match.group(1)

setup(
    name="osduo_business_connect",
    version=version,
    description="Digital business identity, product/service showcase, lead capture, analytics and CRM integration",
    author="OSDuo",
    author_email="info@osduo.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
