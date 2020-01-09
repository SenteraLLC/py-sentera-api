import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentera",
    version="0.0.0",
    description="Python api to access Sentera data through GraphQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
        "aiohttp",
        "pandas",
        "tqdm"
    ],
    extras_require={
        'dev': [
            'pytest',
            'sphinx_rtd_theme',
            'pylint',
            'm2r',
            "sphinx",
            "jupyter"
        ]
    },
)
