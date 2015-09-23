#!/usr/bin/env python

"""
Created on 2015-09-22T16:24:28
"""

from __future__ import division, print_function
import sys
import argparse

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

import pandas as pd
from splinter.browser import Browser
import connect_aws_db as cadb

__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def splinter_scrape_bf(city, state):
    """PURPOSE: To """
    city = city.lower()
    state = state.lower()
    br = Browser()
    citystate_string = city+'_'+state+'_us/'
    url = 'http://www.bringfido.com/lodging/city/'+citystate_string
    br.visit(url)

    page = 1
    npages = len(br.find_by_xpath('//*[@id="results_paging_controls_bottom"]/span')) - 1

    columns = ['hotel_id',
               'hotel_url',
               'hotel_name',
               'hotel_address',
               'hotel_city',
               'hotel_state',
               'hotel_rating',
               'hotel_latitude',
               'hotel_longitude',
               'review_count',
               'hotel_address',
               'business_id',
               'review_id',
               'user_id',
               'username',
               'review_title',
               'review_text',
               'review_rating',
               'review_date']

    bigdf = pd.DataFrame(columns=columns)

    while page <= npages:
        print('*'*70)
        print('Now on page {}'.format(page))
        archive_links = br.find_by_xpath('//*[@id="results_list"]/div')

        hotel_names = []
        text_summaries = []
        links = []

        for lnk in archive_links:
            hotel_names.append(lnk.find_by_xpath('div[2]/h1/a').value)
            text_summaries.append(lnk.text)
            this_link = lnk.find_by_xpath('div/h1/a')['href']
            links.append(this_link)

        for hotel_id, link in enumerate(links):
            print('*'*50)
            print('Now on {}'.format(link))
            print('*'*50)
            br.visit(link)

            df = pd.DataFrame(columns=columns)

            # hotel_description = br.find_by_xpath('//*[@class="body"]').text

            # scrape the address details section of the page
            details = br.find_by_xpath('//*[@class="address"]').text.split('\n')

            # now get just the address:
            address = details[0]

            # and just the city, state, country, and zip code:
            csczip = details[1]

            # and just the phone number
            # phone = details[2]

            # now separate the city, state, and zip:
            city, state, zipcode = csczip.strip().split(',')
            zipcode = zipcode[3:]

            #Now using correct Xpath we are fetching URL of archives
            reviews = br.find_by_xpath('//*[@class="review_container"]')

            texts = []
            titles = []
            authors = []
            ratings = []

            print(reviews)
            print('')
            for rev in reviews:
                titles.append(rev.find_by_xpath('div/div[1]').text)
                authors.append(rev.find_by_xpath('div/div[2]').text)
                texts.append(rev.find_by_xpath('div/div[3]').text)
                ratings.append(rev.find_by_xpath('div[2]/img')['src'].split('/')[-1][0:1])
                print(rev.find_by_xpath('div[2]/img')['src'].split('/')[-1][0:1])

            df['review_title'] = titles
            df['username'] = authors
            df['review_text'] = texts
            df['review_rating'] = ratings
            df['hotel_id'] = hotel_id
            df['hotel_name'] = hotel_names[hotel_id]
            df['hotel_url'] = link
            df['hotel_address'] = address
            df['hotel_city'] = city
            df['hotel_state'] = state
            df['hotel_rating'] = np.mean([int(rat) for rat in ratings])
            df['hotel_latitude'] = ''
            df['hotel_longitude'] = ''
            df['review_count'] = len(texts)
            df['review_id'] = 0
            df['user_id'] = 0

        bigdf = bigdf.append(df)
        page += 1
        if page <= npages:
            br.visit(url)
            print('Now scraping page {} of {}'.format(page, npages))
            button = br.find_by_id('page_'+str(page))
            print(button)
            button.click()

    bigdf_reviews = bigdf[['hotel_id', 'review_id', 'business_id', 'user_id',
                          'username', 'review_title', 'review_text', 'review_rating']].copy()

    engine = cadb.connect_aws_db(write_unicode=True)
    bigdf_reviews.to_sql('bf_reviews', engine, if_exists='append', index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'city',
        help='The name of the city to scrape.')
    parser.add_argument(
        'state',
        help='This name of the state to scrape.',
             nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python splinter_scrape_bf.py city state')
        print('For example:')
        print('python splinter_scrape_bf.py new_haven ct')
        sys.exit(2)

    args = parser.parse_args()

    splinter_scrape_bf(args.city, args.state)
