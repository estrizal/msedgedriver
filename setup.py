from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'Automated Microsoft Edge WebDriver manager for Selenium'
LONG_DESCRIPTION = (
    'Automatically detects your Microsoft Edge browser version, downloads '
    'the exact matching msedgedriver binary (win64, mac64, mac64 M1/ARM, linux64), '
    'caches it under ~/.msedgedriver/, and returns its path for use with Selenium. '
    'Supports version pinning, custom install paths, quiet mode, and cross-platform operation.'
)

# Setting up
setup(
    name="msedgedriver",
    version=VERSION,
    author="estriadi (Aditya Maurya)",
    author_email="estritech@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    url="https://github.com/estrizal/msedgedriver",
    project_urls={
        "Source Code": "https://github.com/estrizal/msedgedriver",
        "Bug Tracker": "https://github.com/estrizal/msedgedriver/issues",
        "PyPI":        "https://pypi.org/project/msedgedriver/",
    },
    keywords=[
        'python', 'selenium', 'edge driver', 'ms edge driver',
        'webdriver manager', 'edge webdriver', 'selenium edge driver',
        'microsoft edge', 'msedgedriver', 'edge automation',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
    ]
)
