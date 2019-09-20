# Hack for importing from parent directory
import logging
import os
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current_dir)
sys.path.append(parent_directory)

import synchrolog_flask
from flask import Flask, jsonify

app = Flask(__name__)
app.config['SYNCHROLOG_ACCESS_TOKEN'] = '123456'

logging.getLogger('werkzeug').setLevel(logging.ERROR)

synchrolog_flask.init(app, use_queue=True, level=logging.DEBUG)
logger = app.logger


@app.route('/')
def index():
    logger.info('HELLO')
    logger.error('ALOHA',)
    raise ValueError('EXCEPTION!!!')


@app.route('/hello')
def hello():
    return jsonify({})
