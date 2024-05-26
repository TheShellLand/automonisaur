import json
from flask import Flask

app = Flask(__name__)


@app.route("/")
def default():
    return 'Hello.'
