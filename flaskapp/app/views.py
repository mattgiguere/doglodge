from flask import render_template
from app import app
from flask import request
# import retrieve_best_hotels2 as rbh
import retrieve_best_hotels3 as rbh

available_cities = [
    'new york city',
    'los angeles',
    'new haven',
    'phoenix',
    'chicago',
    'houston',
    'philadelphia',
    'san antonio',
    'san diego',
    'dallas',
    'san jose',
    'austin',
    'jacksonville',
    'san francisco',
    'palo alto',
    'mountain view',
    'sunnyvale',
    'santa clara',
    ]

@app.route('/')


@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/output')
def call_output():
    # gets the city variable from the linking page
    destination = request.args.get('ID')

    # transform the destination to a more suitable format
    # (i.e. remove state and make all lower case):
    tdest = str(destination).split(',')[0].strip().lower()

    if tdest in available_cities:
        hotel_names, hotel_ratings, hotel_imgs, hotel_urls, hotel_prices = rbh.retrieve_best_hotels3(destination)
        return render_template("output.html",
                               destination=destination, map_name='map4.html', unavailable=False,
                               ratings=zip(hotel_ratings, hotel_names, hotel_imgs, hotel_urls, hotel_prices))
    else:
        return render_template("output.html",
                               destination=destination,
                               unavailable=True,
                               available_cities=available_cities)

    #       title = 'Home',
    #       user = user)


