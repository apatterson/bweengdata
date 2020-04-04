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
import os
# [START app]
from bokeh.models import ColumnDataSource, LabelSet, FixedTicker, Grid
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.themes import Theme
from bokeh.io import curdoc

from flask import Flask, request, render_template
from stravalib.client import Client

app = Flask(__name__)

client = Client()
strava_client_secret = os.environ['STRAVA_CLIENT_SECRET']

@app.route('/')
@app.route('/<club_name>')
def hello(club_name='Bweeng Trail Blazers'):
    authorize_url = client.authorization_url(client_id=22031, redirect_uri=request.base_url)

    code = request.args.get('code')
    if code:
        access_token = client.exchange_code_for_token(client_id=22031, client_secret=strava_client_secret, code=code)

        clubs = client.get_athlete_clubs()
        me = client.get_athlete()
        if len(clubs) <1:
            return 'You are not a member of any Strava clubs'
        try:
            myclub = next(club for club in clubs if club.name == club_name)
        except StopIteration:
            return '<ul>' + ''.join('<li><a href="/' + c.name + '?code=' + code +
                                    '">' + c.name + '</a></li>' for c in clubs) + '</ul>'
        source = ColumnDataSource(data=dict(speed=[4, 4, 4, 4, 4, 4, 3.333, 2.777, 3.83],
                                            distance=[5000, 10000, 8000, 16000, 21097, 42195, 1000, 1000, 1000],
                                            names=['5K', '10K', '5 Miles', '10 Miles',
                                                       'Half', 'Marathon', '5 mins/K', '6 mins/K', '7 mins/Mile']))
        labels = LabelSet(x='distance', y='speed', text='names', level='glyph',
                            source=source, render_mode='canvas')
        plot = figure()

        for activity in myclub.activities:
            radius = 300
            if activity.athlete.id == me.id:
                radius = 500
            if activity.type == 'Run':
                if activity.workout_type != '1' and activity.distance.num > 1000:
                    plot.circle(activity.distance.num, activity.average_speed.num, color="white", alpha=0.5,
                                size=30)
        for activity in myclub.activities:
            if activity.type == 'Run':
                if activity.workout_type == '1' and activity.distance.num > 1000:
                    plot.circle(activity.distance.num, activity.average_speed.num, color='red', legend='Race',
                                alpha=0.5, size=30)
        for activity in myclub.activities:
            if activity.type == 'Run':
                if activity.distance.num > 1000:
                    if activity.athlete.id == me.id:
                        plot.triangle(activity.distance.num, activity.average_speed.num, legend='Me',
                                   size=15, color='grey', line_width=3)

        plot.xgrid[0].ticker = FixedTicker(ticks=[5000, 8000, 10000, 16000, 21097, 42195])
        plot.ygrid[0].ticker = FixedTicker(ticks=[2.777, 3.3333, 3.83])
        plot.xgrid.band_fill_color = 'rgb(255,87,34)'
        plot.xgrid.band_fill_alpha = 0.3
        plot.ygrid.band_fill_color = 'rgb(255,87,34)'
        plot.ygrid.band_fill_alpha = 0.3

        plot.add_layout(labels)

        theme = Theme(filename="./theme.yaml")
        curdoc().theme = theme

        script, div = components(plot)
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
