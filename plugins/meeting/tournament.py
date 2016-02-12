import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import os
import datetime
import time

# Setup plotly
USERNAME = os.getenv('PLOTLY_USERNAME')
API_KEY = os.getenv('PLOTLY_API_KEY')
plotly.tools.set_credentials_file(username=USERNAME, api_key=API_KEY)

# Color palette: http://www.colourlovers.com/palette/459707/brightly_to_nightly
COLORS = ['008EE6', '0084D6', '0070B5', '00619E', '004F80'] * 5

# Don't change this or your graph ID will also change
FILENAME = 'scores'
COUNTER_FILENAME = 'counter'

def compute_champions(data):
    """ Gets a list of dicts with each stack data, sum scores and return a list
    with all names achieving this maximum.
    """
    scores = {}
    for layer in data:
        try:
            for name, value in zip(layer['x'], layer['y']):
                try:
                    scores[name] += value
                except KeyError:
                    scores[name] = 0.0
        except KeyError:
            # Just continue if some layer doesn't have a x or y
            continue
    return [name for name, score in scores.items() if score ==  max(scores.values())]

def add_stack(names, scores, day, title, fileopt='append'):
    """ Adds lists of names and scores to a new stack in our bar plot, unless we set
    fileopt='overwrite', in which case a new plot is created.
    """
    data = [go.Bar(x=names,
                   y=scores,
                   name="Day %d" % day,
                   marker= go.Marker(color=COLORS[day-1]))]
    layout = go.Layout(title=title, barmode='stack')
    fig = go.Figure(data=data, layout=layout)
    link = py.plot(fig, filename=FILENAME, sharing='public', fileopt=fileopt, auto_open=False)
    return link

def add_data(names, scores):
    """ Updates our plot with lists of names and scores and returns a pair: a link
    to a PNG image with the scores plot and a list with tournament champions, if
    any.
    """
    # Add element to our counter
    link = py.plot([{'x': 1, 'name': 'counter'}], filename=COUNTER_FILENAME,
                   fileopt='append', auto_open=False)

    # Get in which day of the tournament we are
    day = len(py.get_figure(link).get_data())

    # Compute special days: Monday and Friday of the second week
    title = 'Scores'
    fileopt = 'append'
    weekday = datetime.datetime.now().isoweekday()

    # Compute special outputs:
    # If second Friday since tournament started, close tournament
    # If Monday after tournament ended, reset everything
    if day > 6 and weekday == 1: # If Monday, overwrite previous plot and reset counter
        fileopt = 'overwrite'
        py.plot([{'x': 1, 'name': 'counter'}], filename=COUNTER_FILENAME,
                fileopt='overwrite', auto_open=False)
        day = 1
    if day > 5 and weekday == 5: # If Friday, finish this competition
        title = 'Final scores!'

    # Update scores plot and get it's link
    link = add_stack(names, scores, day, title, fileopt)

    # Wait for plot to get updated
    time.sleep(1)

    # Compute champion it it's last day of tournament
    champions = []
    if title == 'Final scores!':
        data = py.get_figure(link).get_data()
        champions = compute_champions(data)

    return '%s.png' % link, champions
