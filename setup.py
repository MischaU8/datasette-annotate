from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-annotate",
    description="Datasette plugin for annotating / labelling your training data.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Mischa Untaga",
    url="https://github.com/MischaU8/datasette-annotate",
    project_urls={
        "Issues": "https://github.com/MischaU8/datasette-annotate/issues",
        "CI": "https://github.com/MischaU8/datasette-annotate/actions",
        "Changelog": "https://github.com/MischaU8/datasette-annotate/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License"
    ],
    version=VERSION,
    packages=["datasette_annotate"],
    entry_points={"datasette": ["datasette_annotate = datasette_annotate"]},
    install_requires=["datasette"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    package_data={
        "datasette_annotate": ["templates/*"]
    },
    python_requires=">=3.7",
)
