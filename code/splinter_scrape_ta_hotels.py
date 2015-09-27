#!/usr/bin/env python

"""
Created on 2015-09-26T12:13:49
"""

from __future__ import division, print_function
import sys
import argparse
import re
import time
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


def get_city(city):
    city_urls = {'new_york_ny': 'http://www.tripadvisor.com/Hotels-g60763-New_York_City_New_York-Hotels.html',
                 'los_angeles_ca': 'http://www.tripadvisor.com/Hotels-g32655-Los_Angeles_California-Hotels.html',
                 'chicago_il': 'http://www.tripadvisor.com/Hotels-g35805-Chicago_Illinois-Hotels.html',
                 'houston_tx': 'http://www.tripadvisor.com/Hotels-g56003-Houston_Texas-Hotels.html',
                 'philadelphia_pa': 'http://www.tripadvisor.com/Hotels-g60795-Philadelphia_Pennsylvania-Hotels.html',
                 'phoenix_az': 'http://www.tripadvisor.com/Hotels-g31310-Phoenix_Arizona-Hotels.html',
                 'san_antonio_tx': 'http://www.tripadvisor.com/Hotels-g60956-San_Antonio_Texas-Hotels.html',
                 'san_diego_ca': 'http://www.tripadvisor.com/Hotels-g60750-San_Diego_California-Hotels.html',
                 'dallas_tx': 'http://www.tripadvisor.com/Hotels-g55711-Dallas_Texas-Hotels.html',
                 'san_jose_ca': 'http://www.tripadvisor.com/Hotels-g33020-San_Jose_California-Hotels.html',
                 'austin_tx': 'http://www.tripadvisor.com/Hotels-g30196-Austin_Texas-Hotels.html',
                 'jacksonville_fl': 'http://www.tripadvisor.com/Hotels-g60805-Jacksonville_Florida-Hotels.html',
                 'san_francisco_ca': 'http://www.tripadvisor.com/Hotels-g60713-San_Francisco_California-Hotels.html',
                 'indianapolis_in': 'http://www.tripadvisor.com/Hotels-g37209-Indianapolis_Indiana-Hotels.html',
                 'columbus_oh': 'http://www.tripadvisor.com/Hotels-g50226-Columbus_Ohio-Hotels.html',
                 'new_haven_ct': 'http://www.tripadvisor.com/Hotels-g33851-New_Haven_Connecticut-Hotels.html',
                 }
    return city_urls[city]


def splinter_scrape_ta_hotels(city_url='', city='new_haven', state='ct', write_to_db=False, max_pages=20):
    """PURPOSE: To """
    # this only needs to be done at the very beginning
    br = Browser()

    if city_url == '':
        city_url = get_city(city.lower()+'_'+state.lower())

    print('using the following url:')
    print('{}'.format(city_url))
    #city_url = "http://www.tripadvisor.com/Hotels-g31310-Phoenix_Arizona-Hotels.html"

    #####################################################
    # do not edit below this line
    #####################################################
    # more_pages is used to keep track if there is more
    # than one page of hotel results for the given city
    more_pages = True

    # scraping will start on page 1 of the hotel results
    page = 1

    # open the URL in a browser object:
    br.visit(city_url)

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

    # get the city and state info
    loclist = br.find_by_xpath('//*[contains(@id, "BREADCRUMBS")]')
    locstring = loclist.text.split(u'\u203a')
    hotel_city = city = locstring[2].lower()

    hotel_state = re.findall('\w+ \(([A-Z][A-Z])\)',locstring[1])[0].lower()

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
        print('waiting a few seconds before scraping...')
        time.sleep(np.random.uniform(3, 10))
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
                print('business_id: {}'.format(biz_id))
                business_id.append(biz_id)
            except:
                print('!'*80)
                print('biz_id DOES NOT EXIST!')
                print('!'*80)
            try:
                prop = listing.find_by_xpath('div/div/div/div[contains(@class, "property_details")]')
            except:
                print('!'*80)
                print('prop DIV DOES NOT EXIST!')
                print('!'*80)
            try:
                title = prop.find_by_xpath('div/div[@class="listing_title"]')
                print(title.text)
                hotel_names.append(title.text)
            except:
                print('!'*80)
                print('TITLE DIV DOES NOT EXIST!')
                print('!'*80)
                hotel_names.append(None)
            try:
                hotel_link = title.find_by_xpath('a')['href']
                print(hotel_link)
                links.append(hotel_link)
            except:
                print('!'*80)
                print('hotel_link DOES NOT EXIST!')
                print('!'*80)
                links.append(None)
            try:
                hotel_img = prop.find_by_xpath('div[@class="photo_booking"]/div/div/a/img')['src']
                print('Hotel img URL: {}'.format(hotel_img))
                img_url.append(hotel_img)
            except:
                print('!'*80)
                print('hotel_img DIV DOES NOT EXIST!')
                print('!'*80)
                img_url.append(None)
            try:
                price_text = prop.find_by_xpath('div[contains(@class, "prw_rup")]/div/div/div/div[@class="headerContents"]/div[contains(@class, "price")]').text
                price = re.findall('(\d+)', price_text)[0]
                print('Price: ${}'.format(price))
                hotel_price.append(price)
            except:
                print('!'*80)
                print('price DIV DOES NOT EXIST!')
                print('!'*80)
                hotel_price.append(None)
            print('*'*50)

        if len(hotel_names) > 0:
            df['hotel_name'] = hotel_names
            df['hotel_price'] = hotel_price
            df['hotel_img_url'] = img_url
            df['hotel_url'] = links
            df['business_id'] = business_id
            df['hotel_city'] = hotel_city
            df['hotel_state'] = hotel_state
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

    if write_to_db:
        engine = cadb.connect_aws_db(write_unicode=True)
        bigdf.to_sql('ta_hotels', engine, if_exists='append', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='argparse object.')
    parser.add_argument(
        '--city_url',
        help='The url of the city to scrape.',
        nargs='?', default='')
    parser.add_argument(
        '-c', '--city',
        help='The url of the city to scrape.',
        nargs='?', default='')
    parser.add_argument(
        '-s', '--state',
        help='This name of the state to scrape.',
             nargs='?', default='')
    parser.add_argument(
        '-w', '--write_to_db',
        help='Set if you want to write the results to the DB.',
             default=False, action='store_true')
    if len(sys.argv) > 7:
        print('use the command')
        print('python splinter_scrape_bf.py city state')
        print('For example:')
        print('python splinter_scrape_bf.py http://www.tripadvisor.com/Hotels-g31310-Phoenix_Arizona-Hotels.html')
        sys.exit(2)

    args = parser.parse_args()

    splinter_scrape_ta_hotels(city_url=args.city_url, city=args.city, state=args.state, write_to_db=args.write_to_db)
