#!/usr/bin/env python

"""
Created on 2015-09-27T16:51:39
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


# change default encoding to handle utf characters
reload(sys)
sys.setdefaultencoding('utf8')


def get_hotel_urls(city, state, engine):
    """Retrieve the hotels for the given city and state"""

    # manipulate the city string into the proper form
    citystr = (' ').join(city.lower().split('_'))
    cmd = "SELECT hotel_id, business_id, hotel_url FROM ta_hotels WHERE "
    cmd += "hotel_city='"+citystr+"' AND "
    cmd += "hotel_state='"+state.lower()+"'"
    result = engine.execute(cmd)
    return [(row['hotel_id'], row['business_id'], row['hotel_url']) for row in result]


def return_results(url, page, br):
    br.visit(url)
    sleep_amount = np.random.uniform(8, 20)
    print('sleeping for {} seconds before continuing.'.format(sleep_amount))
    time.sleep(sleep_amount)
    full_reviews = br.find_by_xpath('//div[contains(@class, "reviewSelector")]')

    page_usernames = []
    page_memberids = []
    page_locations = []
    page_titles = []
    page_ratings = []
    page_dates = []
    page_reviews = []
    page_review_ids = []

    for fullrev in full_reviews:
        # user name:
        try:
            member_info = fullrev.find_by_xpath('div/div[contains(@class, "col1of2")]/div[contains(@class, "member_info")]')
            member_str = member_info.find_by_xpath('div[contains(@class, "memberOverlayLink")]')['id']
            member_id = re.findall('UID_(.*)-', member_str)[0]
            usrnm = member_info.find_by_xpath('div/div[contains(@class, "username mo")]')
        except:
            print('member_info does not exist')
            member_id = ''
            usrnm = ''
        review = fullrev.find_by_xpath('div/div[@class="col2of2"]/div[@class="innerBubble"]')[0]
        title = review.find_by_xpath('div/div[contains(@class, "quote")]').text.strip()[1:-1]
        rating = review.find_by_xpath('div/div[contains(@class, "rating")]/span/img')['alt'].split(' ')[0]
        date = review.find_by_xpath('div/div[contains(@class, "rating")]/span[contains(@class, "ratingDate")]')['title']
        rev = review.find_by_xpath('div/div[contains(@class, "entry")]').text.strip().replace("\n", "")
        if len(usrnm) > 0:
            susrnm = usrnm[0].text
            username = susrnm.decode('utf-8', 'ignore').strip()
            print('Username: {}'.format(username))
        else:
            username = ''
            print('Username: A Trip Advisor Member')

        locationel = member_info.find_by_xpath('div[contains(@class, "location")]')
        if len(locationel) > 0:
            location = str(locationel[0].text).strip()
            print('Location: {}'.format(location))
        else:
            location = ''
            print('Location: ')

        #print('full review_id: {}'.format(fullrev['id']))
        try:
            rev_id = re.search('review_(\d+)$', fullrev['id']).group(1)
        except AttributeError:
            rev_id = ''

#         print('review_id: {}'.format(rev_id))
#         print('Title: {}'.format(title))
#         print('Rating: {}'.format(rating))
#         print('Date: {}'.format(date))
#         print('Review:')
#        print(rev)
#        print('*'*50)

        # remove 4-byte unicode text:
        try:
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            # UCS-2 build
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        username = highpoints.sub(u'', username)
        title = highpoints.sub(u'', title)
        rev = highpoints.sub(u'', rev)

        page_usernames.append(username)
        page_memberids.append(member_id)
        page_locations.append(location)
        page_titles.append(title)
        page_ratings.append(rating)
        page_dates.append(date)
        page_reviews.append(rev)
        page_review_ids.append(rev_id)

    if len(br.find_by_xpath('//a[contains(@class, "next")]')) > 0:
        url = br.find_by_xpath('//a[contains(@class, "next")]')['href']
        more_reviews = True
        page += 1
#        print('url and page updated.')
    else:
        more_reviews = False

    ret_dict = {'usrnms': page_usernames,
                'mmbrids': page_memberids,
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


def get_done_business_ids(city, engine):
    cmd = 'select distinct r.business_id from '
    cmd += 'ta_reviews r inner join ta_hotels h on r.business_id = '
    cmd += 'h.business_id where h.hotel_city = "'
    cmd += (' ').join(city.split('_'))+'" '
    donebids = [int(bid[0]) for bid in pd.read_sql_query(cmd, engine).values]
    return donebids


def get_biz_review_ids(city, engine):
    cmd = 'select biz_review_id from ta_reviews r inner join '
    cmd += 'ta_hotels h on r.business_id=h.business_id '
    cmd += 'where h.hotel_city = '
    cmd += '"'+(' ').join(city.split('_'))+'"'
    try:
        xstng_revs = [int(rev_id[0]) for rev_id in pd.read_sql_query(cmd, engine).values]
    except:
        engine = cadb.connect_aws_db(write_unicode=True)
        xstng_revs = [int(rev_id[0]) for rev_id in pd.read_sql_query(cmd, engine).values]
    return xstng_revs


def remove_duplicates(bigdf, city, engine):
    xstng_revs = get_biz_review_ids(city, engine)
    if len(xstng_revs) > 0:
        bigdf = bigdf[~bigdf['biz_review_id'].isin(xstng_revs)].copy()
    return bigdf


def scrape_hotel(url, br, engine):
    columns = ['review_id',
               'hotel_id',
               'business_id',
               'biz_review_id',
               'biz_member_id',
               'username',
               'review_title',
               'review_rating',
               'review_text',
               'review_date']

    bigdf = pd.DataFrame(columns=columns)

    more_reviews = True
    page = 1
    while more_reviews:
        print('*'*50)
        print('Now on page {}'.format(page))
        #print('*'*50)

        df = pd.DataFrame(columns=columns)

        ret_dict = return_results(url, page, br)
        #print(ret_dict['locs'])
        #print(ret_dict['ttls'])
        df['biz_review_id'] = ret_dict['revids']
        df['biz_member_id'] = ret_dict['mmbrids']
        df['username'] = ret_dict['usrnms']
        df['review_title'] = ret_dict['ttls']
        df['review_rating'] = ret_dict['rtngs']
        df['review_date'] = ret_dict['dts']
        df['review_text'] = ret_dict['rvws']
        url = ret_dict['url']
        more_reviews = ret_dict['more_reviews']
        page = ret_dict['page']
        print('successfully completed page {}'.format(page))
        bigdf = bigdf.append(df)
        # more_reviews = False
    return bigdf


def splinter_scrape_ta_reviews(city='', state='', write_to_db=False, start_num=0, end_num=-1):
    """PURPOSE: To """
    engine = cadb.connect_aws_db(write_unicode=True)
    blinks = get_hotel_urls(city, state, engine)

    # only do the specified hotel range
    if start_num != 0:
        blinks = blinks[start_num:]
    if end_num != -1:
        if len(blinks) < end_num:
            print('end_num exceeded number of hotels. resetting to max.')
            end_num = len(blinks)
        blinks = blinks[:end_num]

    br = Browser()

    donebids = get_done_business_ids(city, engine)

    for hotel_id, biz_id, link in blinks:
        # check to see if there are already reviews for that hotel
        if int(biz_id) not in donebids:
            bigdf = scrape_hotel(link, br, engine)
            bigdf['hotel_id'] = hotel_id
            bigdf['business_id'] = biz_id
            bigdf = remove_duplicates(bigdf, city, engine)
            if write_to_db:
                try:
                    bigdf.to_sql('ta_reviews', engine, if_exists='append', index=False)
                except:
                    print('WRITING TO DB FAILED!!!')
        else:
            print('business_id {} already scraped.'.format(biz_id))


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
        '--start_num',
        help='The starting number within the list of hotels for a city ' +
        'to start with. For example, if there are ten hotels for the city, ' +
        'and you only want to add reviews for hotels 5 through 10, set ' +
        'start_num to 5.',
             nargs='?', default=0)
    parser.add_argument(
        '--end_num',
        help='The ending number within the list of hotels for a city. ' +
        'For example, if there are ten hotels for the city, ' +
        'and you only want to add reviews for hotels 0 through 4, set ' +
        'end_num to 5.',
             nargs='?', default=-1)
    parser.add_argument(
        '-w', '--write_to_db',
        help='Set if you want to write the results to the DB.',
             default=False, action='store_true')
    if len(sys.argv) > 11:
        print('use the command')
        print('python splinter_scrape_bf.py city state')
        print('For example:')
        print('python splinter_scrape_ta_reviews.py -c new_haven -s ct')
        sys.exit(2)

    args = parser.parse_args()

    splinter_scrape_ta_reviews(city=args.city,
                               state=args.state,
                               write_to_db=args.write_to_db,
                               start_num=int(args.start_num),
                               end_num=int(args.end_num))
