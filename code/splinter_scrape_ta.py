#!/usr/bin/env python

"""
Created on 2015-09-26T12:13:49
"""

from __future__ import division, print_function
import sys
import argparse
import re
import time
# try:
#     import numpy as np
# except ImportError:
#     print('You need numpy installed')
#     sys.exit(1)
import pandas as pd
from splinter.browser import Browser
import connect_aws_db as cadb


__author__ = "Matt Giguere (github: @mattgiguere)"
__license__ = "MIT"
__version__ = '0.0.1'
__maintainer__ = "Matt Giguere"
__email__ = "matthew.giguere@yale.edu"
__status__ = " Development NOT(Prototype or Production)"


def splinter_scrape_ta(city_url):
    """PURPOSE: To """
    # this only needs to be done at the very beginning
    br = Browser()

    # number of pages of hotel results to scrape
    max_pages = 7

    url = "http://www.tripadvisor.com/Hotels-g31310-Phoenix_Arizona-Hotels.html"

    #####################################################
    # do not edit below this line
    #####################################################
    # more_pages is used to keep track if there is more
    # than one page of hotel results for the given city
    more_pages = True

    # scraping will start on page 1 of the hotel results
    page = 1

    # open the URL in a browser object:
    br.visit(url)

    # find the div to enter the date range. This is needed to get pricing info:
    date_bar = br.find_by_xpath('//*[contains(@class, "meta_date_wrapper")]')

    # find the check in calendar span:
    cin_btn = date_bar.find_by_xpath('span[contains(@class, "meta_date_field   check_in")]/span')[0]

    # now click the check_in span to activate it
    cin_btn.click()

    # select the right calendar div (next month)
    rightcal = br.find_by_xpath('//div[contains(@class, "month")]')[1]

    # now select the third Friday of next month as the check in date
    fri_btn = rightcal.find_by_xpath('table/tbody/tr[3]/td[6]/div')

    # and click it
    fri_btn.click()

    # now choose the next day (saturday) as the check out date
    cout_btn = date_bar.find_by_xpath('span[contains(@class, "meta_date_field   check_out")]/span')[0]
    cout_btn.click()
    leftcal = br.find_by_xpath('//div[contains(@class, "month")]')[0]
    sat_btn = leftcal.find_by_xpath('table/tbody/tr[3]/td[7]/div')
    sat_btn.click()
    print('Dates selected.')

    # wait a few seconds for ta to retrieve prices
    time.sleep(5)

    # create a pandas dataframe that will be used for writing
    # the results to the DB:

    columns = ['hotel_id',
               'hotel_url',
               'hotel_img_url',
               'hotel_name',
               'hotel_address',
               'hotel_city',
               'hotel_state',
               'hotel_rating',
               'hotel_latitude',
               'hotel_longitude',
               'hotel_price',
               'business_id',
               'review_count',
               'dog_review_count',
               ]

    bigdf = pd.DataFrame(columns=columns)

    # create some lists to fill w. the results from each page
    hotel_names = []
    links = []
    img_url = []
    hotel_price = []
    business_id = []
    print('starting scraper loop.')
    while more_pages and page <= max_pages:
        print('*'*75)
        print('Now scraping page {} of {} of the hotel results'.format(page, max_pages))
        print('*'*75)
        # get all the review divs
        time.sleep(5)
        listing_div = br.find_by_xpath('//*[contains(@class, "hotels_lf_condensed")]')
        xsts1 = br.is_element_present_by_xpath('//*[contains(@class, "photo_booking")]', wait_time=1)
        xsts2 = br.is_element_present_by_xpath('//*[contains(@class, "property_details")]', wait_time=1)
        xsts3 = br.is_element_present_by_xpath('//*[contains(@class, "prw_rup")]/div/div/div/div[@class="headerContents"]/div[contains(@class, "price")]', wait_time=1)
        while len(listing_div) < 3 or not xsts1 or not xsts2 or not xsts3:
            print('now waiting for DOIs to return')
            time.sleep(5)
            listing_div = br.find_by_xpath('//*[contains(@class, "hotels_lf_condensed")]')
            xsts1 = br.is_element_present_by_xpath('//*[contains(@class, "photo_booking")]', wait_time=1)
            xsts2 = br.is_element_present_by_xpath('//*[contains(@class, "property_details")]', wait_time=1)
            xsts3 = br.is_element_present_by_xpath('//*[contains(@class, "prw_rup")]/div/div/div/div[@class="headerContents"]/div[contains(@class, "price")]', wait_time=1)
            print('# of listings: {}'.format(len(listing_div)))
            print('photo_booking exists: {}'.format(xsts1))
            print('property_details exists: {}'.format(xsts2))
            print('prw_up exists: {}'.format(xsts3))

        print('Number of hotel listings on this page: {}'.format(len(listing_div)))

        df = pd.DataFrame(columns=columns)

        for listing in listing_div:
            try:
                biz_id = re.findall('hotel_(\d+)', listing['id'])
                if len(biz_id) > 0:
                    biz_id = biz_id[0]
                else:
                    biz_id = None
                prop = listing.find_by_xpath('div/div/div/div[contains(@class, "property_details")]')
                title = prop.find_by_xpath('div/div[@class="listing_title"]')
                hotel_link = title.find_by_xpath('a')['href']
                hotel_img = prop.find_by_xpath('div[@class="photo_booking"]/div/div/a/img')['src']
                price_text = prop.find_by_xpath('div[contains(@class, "prw_rup")]/div/div/div/div[@class="headerContents"]/div[contains(@class, "price")]').text
                price = re.findall('(\d+)', price_text)[0]

                print('business_id: {}'.format(biz_id))
                print(title.text)
                print(hotel_link)
                print('Hotel img URL: {}'.format(hotel_img))
                print('Price: ${}'.format(price))

                business_id.append(biz_id)
                hotel_names.append(title.text)
                links.append(hotel_link)
                img_url.append(hotel_img)
                hotel_price.append(price)
            except:
                print('!'*80)
                print('ONE OF THE NEEDED DIVS DOES NOT EXIST!')
                print('!'*80)
            print('*'*50)

        if len(hotel_names) > 0:
            df['hotel_name'] = hotel_names
            df['hotel_price'] = hotel_price
            df['hotel_img_url'] = img_url
            df['hotel_url'] = links
            df['business_id'] = business_id
            bigdf = bigdf.append(df)

        # update the page number
        page += 1

        # if more pages are desired, look for a "next" button
        if page <= max_pages:
            nxt_btn = br.find_by_xpath('//div[contains(@class, "deckTools")]/div[contains(@class, "unified")]/a[contains(@class, "next")]')
            # if there is a next button, click it
            # else exit the while loop
            if len(nxt_btn) > 0:
                nxt_btn.click()
            else:
                more_pages = False

    engine = cadb.connect_aws_db(write_unicode=True)
    bigdf.to_sql('ta_hotels', engine, if_exists='append', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        'city_url',
        help='The url of the city to scrape.')
    parser.add_argument(
        'state',
        help='This name of the state to scrape.',
             nargs='?')
    if len(sys.argv) > 3:
        print('use the command')
        print('python splinter_scrape_bf.py city state')
        print('For example:')
        print('python splinter_scrape_bf.py http://www.tripadvisor.com/Hotels-g31310-Phoenix_Arizona-Hotels.html')
        sys.exit(2)

    args = parser.parse_args()

    splinter_scrape_ta(args.city_url)
