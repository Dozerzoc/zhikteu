import os

from flask import Flask, request
from flask_cors import CORS
from models import get_result
from werkzeug.serving import make_ssl_devcert
import json

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/query', methods=['GET'])
def index():
    text = request.args.get('text')
    data = None
    if text:
        data = get_result(text)
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


if __name__ == "__main__":
    ssl = make_ssl_devcert(os.curdir + '/selfsigned')
    app.run(ssl_context=(ssl[0], ssl[1]), host='0.0.0.0', port=5000, debug=False)
