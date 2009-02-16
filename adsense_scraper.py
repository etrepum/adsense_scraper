#!/usr/bin/env python

# requires html5lib, twill
import sys
import pprint
from cStringIO import StringIO
from xml.etree import cElementTree

try:
    import html5lib
    from html5lib import treebuilders
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

SERVICE_LOGIN_BOX = "https://www.google.com/accounts/ServiceLoginBox?service=adsense&ltmpl=login&ifr=true&rm=hide&fpui=3&nui=15&alwf=true&passive=true&continue=https%3A%2F%2Fwww.google.com%2Fadsense%2Flogin-box-gaiaauth&followup=https%3A%2F%2Fwww.google.com%2Fadsense%2Flogin-box-gaiaauth&hl=en_US"
OVERVIEW_URL = "https://www.google.com/adsense/report/overview?timePeriod="
TIME_PERIODS = ['today', 'yesterday', 'thismonth', 'lastmonth', 'sincelastpayment']

ETREE_PARSER = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("etree", cElementTree))

def parse_summary_table(doc):
    for t in doc.findall('.//table'):
        if t.attrib.get('id') == 'summarytable':
            break
    else:
        raise ValueError("summary table not found")

    return [
        [c.text or '' for c in row.findall('td')]
        for row in t.findall('.//tr')
    ]

def get_adsense(login, password):
    b = twill.commands.get_browser()
    b.go(SERVICE_LOGIN_BOX)
    form = b.get_all_forms()[0]
    form['Email'] = login
    form['Passwd'] = password
    b.submit()
    b.go(b.find_link('Click here to continue').url)
    return b

def get_time_period(b, period):
    b.go(OVERVIEW_URL + period)
    doc = ETREE_PARSER.parse(b.get_html())
    return parse_summary_table(doc)

def main():
    try:
        login, password = sys.argv[1:]
    except ValueError:
        raise SystemExit("usage: %s LOGIN PASSWORD" % (sys.argv[0],))
    twill.set_output(StringIO())
    b = get_adsense(login, password)
    data = {}
    for period in TIME_PERIODS:
        data[period] = get_time_period(b, period)
    pprint.pprint(data)
    twill.set_output(None)
    return data

if __name__ == '__main__':
    data = main()
