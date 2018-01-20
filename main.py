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
from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.themes import Theme

from flask import Flask, request, render_template
from stravalib.client import Client

app = Flask(__name__)

client = Client()

@app.route('/')
@app.route('/<club_name>')
def hello(club_name='Bweeng Trail Blazers'):
    authorize_url = client.authorization_url(client_id=22031, redirect_uri=request.base_url)

    code = request.args.get('code')
    if code:
        access_token = client.exchange_code_for_token(client_id=22031, client_secret='', code=code)

        clubs = client.get_athlete_clubs()
        if len(clubs) <1:
            return 'You are not a member of any Strava clubs'
        try:
            myclub = next(club for club in clubs if club.name == club_name)
        except StopIteration:
            return '<ul>' + ''.join('<li><a href="/' + c.name + '?code=' + code +
                                    '">' + c.name + '</a></li>' for c in clubs) + '</ul>'

        plot = figure(x_axis_label='Distance (metres)', y_axis_label='Average Speed (m/s)',
                      background_fill_color="rgb(255,87,34)", sizing_mode="scale_width",
                      outline_line_color="white")
        for activity in myclub.activities:
            if activity.type == 'Run':
                if activity.workout_type != '1':
                    plot.circle(activity.distance.num, activity.average_speed.num, color="white", alpha=0.5,
                                radius=300)
        for activity in myclub.activities:
            if activity.type == 'Run':
                if activity.workout_type == '1':
                    plot.circle(activity.distance.num, activity.average_speed.num, color='red', legend='Race',
                                alpha=0.5, radius=300)

        theme = Theme(filename="./theme.yaml")
        doc = Document(theme=theme)
        doc.add_root(plot)

        script, div = components(doc)
        return render_template("chart.html", script=script, plot=div, club=myclub, clubs=clubs, code=code, client=client)
    else:
        return "This app requires access to Strava. <p><a href='" + authorize_url + "'><img src=\"static/btn_strava_connectwith_orange.png\"></img> </a>"


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
    app.run(host='127.0.0.1', port=8081, debug=True)
# [END app]
