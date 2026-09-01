from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="osduo_business_connect",
    version="1.0.1",
    description="Digital business identity, product/service showcase, lead generation, and CRM integration for individuals and small businesses",
    author="OSDuo",
    author_email="info@osduo.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
