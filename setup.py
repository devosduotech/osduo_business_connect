import re

from setuptools import find_packages, setup

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# Single source of truth: keep setup.py in step with the app version so the
# stale hardcoded version does not drift again at release time.
with open("osduo_business_connect/__init__.py") as f:
    version_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', f.read(), re.M)
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
