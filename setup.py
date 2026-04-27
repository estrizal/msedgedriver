from setuptools import setup, find_packages
import setuptools
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.txt"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.3'
DESCRIPTION = 'ms edge selenium driver downloader'
LONG_DESCRIPTION = 'It automatically downloads ms edge selenium driver that is compatible with ms edge browser installed on your system. Just use install() command and it will download msedgedriver file in that directory'

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
    install_requires=[''],
    keywords=['python', 'selenium', 'edge driver', 'ms edge driver installer', 'automatically download ms edge driver for selenium', 'selenium edge driver', 'selenium ms edge driver'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License"
    ]
)
