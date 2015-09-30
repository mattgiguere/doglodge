from flask import Flask
from flask import render_template
from flask import request
import retrieve_best_hotels2 as rbh
import sys
import os
import connect_aws_db as cadb

app = Flask(__name__)

@app.route('/')
#def hello_world():
#  return 'Hello again, from Dog Lodge! '#+sys.version+' *** '+(' ').join(sys.path)

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/output')
def call_output():
    # gets the city variable from the linking page
    destination = request.args.get('ID')

    hotel_names, hotel_ratings = rbh.retrieve_best_hotels2(destination)
    return render_template("output.html",
                           destination=destination, map_name='map4.html',
                           ratings=zip(hotel_ratings, hotel_names))

@app.route('/countme/<input_str>')
def count_me(input_str):
    return input_str

@app.route('/creds/')
def creds():
    outpt = 'username: {}\n'.format('Robert')
    outpt += 'db: {}\n'.format('Scotland')
    return 'howdy\n'+outpt

@app.route('/version/')
def return_python_version():
    return 'Python Version: {}\n'.format(sys.version)

@app.route('/rbh/')
def return_best_hotels():
    hotel_names, hotel_ratings = rbh.retrieve_best_hotels2('Phoenix')
    return 'howdy\n'+('-').join(hotel_names)

if __name__ == '__main__':
  app.run()
