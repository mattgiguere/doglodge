from flask import render_template
from app import app
from flask import request
import retrieve_best_hotels as rbh


@app.route('/')


@app.route('/index')
def index():
    #user = '' # fake user
    #return render_template("index.html",
    #    title = 'Home',
    #    user = user)
    return render_template("index.html")


@app.route('/output')
def call_output():
    # gets the city vairable from the linking page
    destination = request.args.get('ID')
    #the_result = Insight_model_IT1.Classify_Speech(test_str)
    the_result = destination + 'bla'

#    hotel_names = [u'Arizona Biltmore, A Waldorf Astoria Resort',
#                   u'Hotel Palomar Phoenix, a Kimpton Hotel',
#                   u'The Westin Phoenix Downtown', u'Crowne Plaza Phoenix Airport',
#                   u'Sheraton Phoenix Downtown Hotel',
#                   u'Pointe Hilton Tapatio Cliffs Resort',
#                   u'Embassy Suites Phoenix - Biltmore',
#                   u'Pointe Hilton Squaw Peak Resort',
#                   u'BEST WESTERN Innsuites Phoenix Hotel & Suites',
#                   u'Hilton Phoenix Airport']
#
#    hotel_ratings = ['5.0', '4.8', '4.7', '4.0', '4.0', '3.6', '3.0', '3.0', '2.5', '2.0']

    hotel_names, hotel_ratings = rbh.retrieve_best_hotels(destination)
    return render_template("output.html", the_result=the_result,
                           destination=destination, map_name='map4.html',
                           ratings=zip(hotel_ratings, hotel_names))
    #       title = 'Home',
    #       user = user)


