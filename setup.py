#!/usr/bin/env python

from setuptools import setup
#from distutils.core import setup

VERSION = '0.3'
DESCRIPTION = "Scrapes Google AdSense earnings data with Python using Twill"
LONG_DESCRIPTION = """
adsense_scraper is a simple module that uses Twill and html5lib to scrape
Google AdSense earnings data from your account.

For example, this is useful as a cron job or other sort of periodic task to 
store a copy of your earnings in your own database so that you don't have
to visit the AdSense site every day.

"""

CLASSIFIERS = filter(None, map(str.strip,
"""                 
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines()))


setup(
    name="adsense_scraper",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author="Bob Ippolito",
    author_email="bob@redivi.com",
    url="http://github.com/etrepum/adsense_scraper/tree/master",
    license="MIT License",
    py_modules=['adsense_scraper'],
    platforms=['any'],
    install_requires=['twill', 'html5lib'],
)
