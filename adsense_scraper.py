#!/usr/bin/env python
"""Scrapes Google AdSense data with Python using Twill

Current canonical location of this module is here:
http://github.com/etrepum/adsense_scraper/tree/master


Usage::

    from adsense_scraper import get_adsense, get_time_period
    b = get_adsense('YOUR_ADSENSE_LOGIN', 'YOUR_ADSENSE_PASSWORD')
    rows = get_time_period(b, 'yesterday')
    # The summary data is always the first row with channel == ''
    print 'I earned this much yesterday: $%(earnings)s' % rows[0]

"""
# requires html5lib, twill
import sys
import pprint
import decimal
from cStringIO import StringIO
from xml.etree import cElementTree

try:
    from html5lib import HTMLParser
    import twill.commands
except ImportError:
    print >>sys.stderr, """\
adsense_scraper has dependencies::

    Twill 0.9 http://twill.idyll.org/
    html5lib 0.11 http://code.google.com/p/html5lib/

Try this::

    $ easy_install twill html5lib
"""
    raise SystemExit()

__version__ = '0.5'

SERVICE_LOGIN_BOX_URL = "https://www.google.com/accounts/ServiceLogin?service=adsense&rm=hide&fpui=3&nui=15&alwf=true&ltmpl=adsense&passive=true&continue=https%3A%2F%2Fwww.google.com%2Fadsense%2Fgaiaauth2&followup=https%3A%2F%2Fwww.google.com%2Fadsense%2Fgaiaauth2&hl=en_US"
OVERVIEW_URL = "https://www.google.com/adsense/report/overview?timePeriod="

TIME_PERIODS = [
    'today',
    'yesterday',
    'thismonth',
    'lastmonth',
    'sincelastpayment',
]


def parse_decimal(s):
    """Return an int or decimal.Decimal given a human-readable number

    """
    stripped = s.replace(',', '').rstrip('%').lstrip('$')
    try:
        return int(stripped)
    except ValueError:
        return decimal.Decimal(stripped)


def parse_summary_table(doc):
    """
    Parse the etree doc for summarytable, returns::

        [{'channel': unicode,
          'impressions': int,
          'clicks': int,
          'ctr': decimal.Decimal,
          'ecpm': decimal.Decimal,
          'earnings': decimal.Decimal}]

    """
    for t in doc.findall('.//table'):
        if t.attrib.get('id') == 'summarytable':
            break
    else:
        raise ValueError("summary table not found")

    res = []
    FIELDS = ['channel', 'requests', 'responses', 'impressions',
              'clicks', 'ctr', 'ecpm', 'earnings']
    for row in t.findall('.//tr'):
        celltext = []
        for c in row.findall('td'):
            tail = ''
            # adsense inserts an empty span if a row has a period in it, so
            # get the children and find the tail element to append to the text
            if c.find('a') and c.find('a').getchildren():
                tail = c.find('a').getchildren()[0].tail or ''
            celltext.append('%s%s' % ((c.text or c.findtext('a') or '').strip(), tail.strip()))

        if len(celltext) != 8:
            continue
        try:
            value_cols = map(parse_decimal, celltext[1:])
        except decimal.InvalidOperation:
            continue
        res.append(dict(zip(FIELDS, [celltext[0]] + value_cols)))

    return res


def get_adsense(login, password):
    """Returns a twill browser instance after having logged in to AdSense
    with *login* and *password*.

    The returned browser will have all of the appropriate cookies set but may
    not be at the exact page that you want data from.

    """
    b = twill.commands.get_browser()
    b.go(SERVICE_LOGIN_BOX_URL)
    for form in b.get_all_forms():
        try:
            form['Email'] = login
            form['Passwd'] = password
        except ValueError:
            continue
        else:
            break
    else:
        raise ValueError("Could not find login form on page")
    b._browser.select_form(predicate=lambda f: f is form)
    b.submit()
    return b


def get_time_period(b, period):
    """Returns the parsed summarytable for the time period *period* given
    *b* which should be the result of a get_adsense call. *period* must be
    a time period that AdSense supports:
    ``'today'``, ``'yesterday'``, ``'thismonth'``,
    ``'lastmonth'``, ``'sincelastpayment'``.

    """
    b.go(OVERVIEW_URL + period)
    # The cElementTree treebuilder doesn't work reliably enough
    # to use directly, so we parse and then dump into cElementTree.
    doc = cElementTree.fromstring(HTMLParser().parse(b.get_html()).toxml())
    return parse_summary_table(doc)


def main():
    try:
        login, password = sys.argv[1:]
    except ValueError:
        raise SystemExit("usage: %s LOGIN PASSWORD" % (sys.argv[0],))
    twill.set_output(StringIO())
    twill.commands.reset_browser()
    b = get_adsense(login, password)
    data = {}
    for period in TIME_PERIODS:
        data[period] = get_time_period(b, period)
    pprint.pprint(data)
    twill.set_output(None)
    return data

if __name__ == '__main__':
    data = main()
