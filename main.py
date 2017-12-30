# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
# [START app]
import random

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

from flask import Flask, request, render_template
from stravalib.client import Client

app = Flask(__name__)

client = Client()

@app.route('/')
def hello():
    authorize_url = client.authorization_url(client_id=22031, redirect_uri='http://localhost:8080/authorized')

    return "<a href='" + authorize_url + "'>Click here</a>"

@app.route('/authorized')
def authorized():
    code = request.args.get('code')
    access_token = client.exchange_code_for_token(client_id=22031, client_secret='', code=code)

    curr_athlete = client.get_athlete().firstname
    plot = figure()
    plot.circle([1,2], [3,4])
    html = file_html(plot, CDN, "my plot")
    return html

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
