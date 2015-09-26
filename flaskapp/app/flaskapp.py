from flask import Flask
app = Flask(__name__)

@app.route('/')


@app.route('/index')
def index():
    #user = '' # fake user
    #return render_template("index.html",
    #    title = 'Home',
    #    user = user)
    return render_template("index.html")


if __name__ == '__main__':
  app.run()
