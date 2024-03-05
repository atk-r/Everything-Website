from flask import Flask
from routing import getWebpage

app = Flask(__name__)


@app.route('/')
def index():
  return getWebpage('/')


@app.route('/<path:route>')
def page(route):
  return getWebpage(route)

if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0")
