from flask import render_template
from app import app
from flask import request
import retrieve_best_hotels2 as rbh


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
    # gets the city variable from the linking page
    destination = request.args.get('ID')

    hotel_names, hotel_ratings = rbh.retrieve_best_hotels2(destination)
    return render_template("output.html",
                           destination=destination, map_name='map4.html',
                           ratings=zip(hotel_ratings, hotel_names))
    #       title = 'Home',
    #       user = user)


