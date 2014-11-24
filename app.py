#!/usr/bin/env python
import argparse
import os

from flask import Flask, make_response, render_template

app = Flask(__name__)

DEBUG = True
if os.environ.get('DEPLOYMENT_TARGET', 'development') in ['staging', 'production']:
    DEBUG = False

@app.route('/')
def index(methods=['GET']):
    context = {}

    return make_response(render_template('session_list.html', **context))


@app.route('/user/<str:user_id>')
def user_detail(user_id=None, methods=['GET']):
    context = {}

    return make_response(render_template('user_detail.html', **context))

@app.route('/session/<str:session_id>')
def session_detail(session_id=None, methods=['GET']):
    context = {}

    return make_response(render_template('session_detail.html', **context))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8000

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=DEBUG)