#!/usr/bin/env python

"""
Created on 2015-09-16T16:14:53
"""

from __future__ import division, print_function
import sys
# import argparse
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from lxml import html
import re
# import time
import timeout_decorator
import signal

__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


class Render(QWebPage):
    def __init__(self, app, url):
        self.app = app
        QWebPage.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        self.mainFrame().load(QUrl(url))
        self.app.exec_()

    def _loadFinished(self, result):
        self.frame = self.mainFrame()
        self.app.quit()
        # self.app.exit()
        # self.deleteLater()

    def update_url(self, url):
        print('updating load Qurl')
        self.mainFrame().load(QUrl(url))
        print('exec_...')
        self.app.exec_()


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


@timeout_decorator.timeout(5, use_signals=False)
def return_results(formatted_result, base_url, page):
    #Next build lxml tree from formatted_result
    tree = html.fromstring(formatted_result)

    print('Tree returned!')
    print(tree.xpath('//div[contains(@id, "emailOnlySignupWrap")]'))

    full_reviews = tree.xpath('//div[contains(@class, "reviewSelector")]')

    page_usernames = []
    page_locations = []
    page_titles = []
    page_ratings = []
    page_dates = []
    page_reviews = []
    page_review_ids = []

    for fullrev in full_reviews:
        # user name:
        member_info = fullrev.xpath('div/div[contains(@class, "col1of2")]/div[contains(@class, "member_info")]')[0]
        usrnm = member_info.xpath('div/div[contains(@class, "username mo")]')
        review = fullrev.xpath('div/div[@class="col2of2"]/div[@class="innerBubble"]')[0]
        title = review.xpath('div/div[contains(@class, "quote")]')[0].text_content().strip()[1:-1]
        rating = review.xpath('div/div[contains(@class, "rating")]/span/img/@alt')[0].split(' ')[0]
        date = review.xpath('div/div[contains(@class, "rating")]/span[contains(@class, "ratingDate")]/@title')
        if len(date) > 0:
            date = date[0]
        else:
            date = review.xpath('div/div[contains(@class, "rating")]/span[contains(@class, "ratingDate")]')[0].text_content()
        rev = review.xpath('div/div[contains(@class, "entry")]')[0].text_content().strip().replace("\n", "")
        if len(usrnm) > 0:
            #location = member_info.xpath('div[1]')[0].text_content()
            print('Username: {}'.format(str(usrnm[0].text_content()).strip()))
            page_usernames.append(str(usrnm[0].text_content()).strip())
        else:
            print('Username: A Trip Advisor Member')
            page_usernames.append('')

        location = member_info.xpath('div[contains(@class, "location")]')
        if len(location) > 0:
            # print('Location: {}'.format(str(location[0].text_content()).strip()))
            page_locations.append(location[0].text_content().strip())
        else:
            # print('Location: ')
            page_locations.append('')

        print('Title: {}'.format(title.encode('utf-8')))
#         print('Rating: {}'.format(rating))
#         print('Date: {}'.format(date))
#         print('Review:')
#         print(rev)
        page_titles.append(title)
        page_ratings.append(rating)
        page_dates.append(date)
        page_reviews.append(rev)
        try:
            rev_id = re.search('review_(\d+)$', fullrev.xpath('@id')[0]).group(1)
        except AttributeError:
            rev_id = ''
        page_review_ids.append(rev_id)

#         print('*'*50)

    if len(tree.xpath('//a[contains(@class, "next")]')) > 0:
        url = base_url+tree.xpath('//a[contains(@class, "next")]/@href')[0]
        more_reviews = True
        page += 1
        print('url and page updated.')
    else:
        more_reviews = False

    ret_dict = {'usrnms': page_usernames,
                'locs': page_locations,
                'ttls': page_titles,
                'rtngs': page_ratings,
                'dts': page_dates,
                'rvws': page_reviews,
                'revids': page_review_ids,
                'url': url,
                'more_reviews': more_reviews,
                'page': page}
    return ret_dict


def scrape_tripadvisor():
    """PURPOSE: To """
    url = "http://www.tripadvisor.com/Hotels-g33851-New_Haven_Connecticut-Hotels.html"

    app = QApplication(sys.argv)

    #Create the render object:
    r = Render(app, url)
    print('create r')

    #result is a QString:
    result = r.frame.toHtml()
    print('create result')

    #QString should be converted to string before processed by lxml
    formatted_result = str(result.toAscii())

    #Next build lxml tree from formatted_result
    tree = html.fromstring(formatted_result)

    #Now using correct Xpath we are fetching URL of archives
    titles_div = tree.xpath('//*[@class="listing_title"]')

    hotel_names = []
    links = []

    for title in titles_div:
        print(title.text_content())
        hotel_names.append(title.text_content())
        print(title.xpath('a/@href')[0])
        links.append(title.xpath('a/@href')[0])
        print('*'*50)

    usernames = []
    locations = []
    titles = []
    ratings = []
    dates = []
    reviews = []
    review_ids = []

    base_url = 'http://www.tripadvisor.com'
    url = base_url+links[0]
    url
    more_reviews = True
    page = 1
    while more_reviews:
        #print('*'*50)
        print('*'*50)
        print('Now on page {}'.format(page))
        #print('*'*50)
        print('*'*50)

        #Create the render object:
        #r = Render(app, url)
        r.update_url(url)
        print('made rendered page')

        #result is a QString:
        result = r.frame.toHtml()
        print('updated result')

        #QString should be converted to string before processed by lxml
        formatted_result = str(result.toAscii())
        print('formatted result')

        try:
            ret_dict = return_results(formatted_result, base_url, page)
            usernames.append(ret_dict['usrnms'])
            locations.append(ret_dict['locs'])
            titles.append(ret_dict['ttls'])
            ratings.append(ret_dict['rtngs'])
            dates.append(ret_dict['dts'])
            reviews.append(ret_dict['rvws'])
            review_ids.append(ret_dict['revids'])
            url = ret_dict['url']
            more_reviews = ret_dict['more_reviews']
            page = ret_dict['page']
        except:
            print('Timed out! Trying that page again...')

        #r.app.exit()


if __name__ == '__main__':
    scrape_tripadvisor()
