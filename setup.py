"""Python library to access Sentera data through GraphQL API."""

import re

import setuptools

VERSIONFILE = "sentera/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentera",
    version=verstr,
    description="Python library to access Sentera data through GraphQL API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=["requests", "aiohttp", "pandas", "tenacity", "tqdm"],
    extras_require={
        "dev": ["pytest", "sphinx_rtd_theme", "pre_commit", "m2r", "sphinx"]
    },
)
