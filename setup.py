# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    author="Lighthouse Team",
    author_email="engineering@opengear.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    description="An API client library for Opengear Lighthouse",
    include_package_data=True,
    install_requires=[
        'requests', 'pyyaml',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="oglhclient",
    package_data={"oglhclient": ["*.raml", "*.html"]},
    packages=setuptools.find_packages(),
    project_urls={
        "Bug Tracker": "https://github.com/opengear/oglhclient/issues",
    },
    python_requires=">=3.6",
    url="https://github.com/opengear/oglhclient",
    version="1.0.1",
)
