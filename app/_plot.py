#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
File for temperatures plotting using Plotly
"""
# Get this figure: fig = py.get_figure("https://plot.ly/~zevross/15/")
# Get this figure's data: data = py.get_figure("https://plot.ly/~zevross/15/").get_data()
# Add data to this figure: py.plot(Data([Scatter(x=[1, 2], y=[2, 3])]), filename ="from api (7)", fileopt="extend")
# Get y data of first trace: y1 = py.get_figure("https://plot.ly/~zevross/15/").get_data()[0]["y"]

# Get figure documentation: https://plot.ly/python/get-requests/
# Add data documentation: https://plot.ly/python/file-options/

# If you're using unicode in your file, you may need to specify the encoding.
# You can reproduce this figure in Python with the following code!

# Learn about API authentication here: https://plot.ly/python/getting-started
# Find your api_key here: https://plot.ly/settings/api


# from plotly.offline import plot as pl
# from plotly.graph_objs import graph_objs as go
from google.appengine.ext import ndb
import datetime


# from models.historicals import Historicals

def plot(thermostat):
    # history = Historicals()
    # history.temperature = 15.4
    # history.mode = 'Heat'
    # thermostat.history.append(history)
    # thermostat.put()
    last_month = datetime.date.today() - datetime.timedelta(days=30)
    last_month = datetime.datetime.combine(last_month, datetime.datetime.min.time())

    # test = datetime.datetime(2017, 1, 10, 18, 31, 51, 995369)
    # print test
    # get all data from thermostat
    thermostat = ndb.gql(
        "SELECT * FROM Thermostats where __key__ = :1", thermostat.key)
    heat_plot = {
        'data_to_plot': [],
        'temperature_to_plot': [],
    }
    cold_plot = {
        'data_to_plot': [],
        'temperature_to_plot': [],
    }
    none_plot = {
        'data_to_plot': [],
        'temperature_to_plot': [],
    }

    for data in thermostat:
        for sample in data.history:
            if sample.timestamp > last_month:
                if sample.mode == 'Heat':
                    l_data = heat_plot.get('data_to_plot')
                    l_data.append(sample.timestamp)
                    l_temp = heat_plot.get('temperature_to_plot')
                    l_temp.append(sample.temperature)
                    heat_plot['data_to_plot'] = l_data
                    heat_plot['temperature_to_plot'] = l_temp
                elif sample.mode == 'Cold':
                    l_data = cold_plot.get('data_to_plot')
                    l_data.append(sample.timestamp)
                    l_temp = cold_plot.get('temperature_to_plot')
                    l_temp.append(sample.temperature)
                    cold_plot['data_to_plot'] = l_data
                    cold_plot['temperature_to_plot'] = l_temp
                elif sample.mode == 'None':
                    l_data = none_plot.get('data_to_plot')
                    l_data.append(sample.timestamp)
                    l_temp = none_plot.get('temperature_to_plot')
                    l_temp.append(sample.temperature)
                    none_plot['data_to_plot'] = l_data
                    none_plot['temperature_to_plot'] = l_temp

                # data_to_plot.append(sample.timestamp)
                # temperature_to_plot.append(sample.temperature)
                # mode_to_plot.append(sample.mode)
    # print data_to_plot
    # print temperature_to_plot
    # print mode_to_plot
    trace1 = {
        "x": heat_plot['data_to_plot'],
        "y": heat_plot['temperature_to_plot'],
        "marker": {
            "color": "rgb(255,0,0)",
            "opacity": 1,
            "size": 10,
            "sizemode": "area",
            "sizeref": 1,
            "symbol": "circle"
        },
        "mode": "markers",
        "name": "Heat",
        "type": "scatter",
        "xaxis": "x1",
        "yaxis": "y1"
    }
    trace2 = {
        "x": cold_plot['data_to_plot'],
        "y": cold_plot['temperature_to_plot'],
        "marker": {
            "color": "rgb(0,0,255)",
            "opacity": 1,
            "size": 10,
            "sizemode": "area",
            "sizeref": 1,
            "symbol": "circle"
        },
        "mode": "markers",
        "name": "Cold",
        "type": "scatter",
        "xaxis": "x1",
        "yaxis": "y1"
    }
    trace3 = {
        "x": none_plot['data_to_plot'],
        "y": none_plot['temperature_to_plot'],
        "marker": {
            "color": "rgb(0,0,0)",
            "opacity": 1,
            "size": 10,
            "sizemode": "area",
            "sizeref": 1,
            "symbol": "circle"
        },
        "mode": "markers",
        "name": "None",
        "type": "scatter",
        "xaxis": "x1",
        "yaxis": "y1"
    }

    # data = go.Data([trace1, trace2, trace3])
    layout = {
        "legend": {
            "x": 100,
            "y": 0.5,
            "bordercolor": "transparent"
        },
        "margin": {"r": 10},
        "plot_bgcolor": "rgb(229,229,229)",
        "showlegend": True,
        "xaxis": {
            "gridcolor": "rgb(255,255,255)",
            "showline": False,
            "showticklabels": True,
            "tickcolor": "rgb(127,127,127)",
            "title": "Date",
            "type": "date"
        },
        "yaxis": {
            "gridcolor": "rgb(255,255,255)",
            "showline": False,
            "showticklabels": True,
            "tickcolor": "rgb(127,127,127)",
            "title": "Temperature",
            "type": "linear"
        }
    }
    # fig = go.Figure(data=data, layout=layout)
    # plot_url = plotly.plotly.plot(fig)
    # print plot_url

    # return a div with the chart ready to be included in a html file
    # chart = pl({
    #     "data": data,
    #     "layout": layout,
    # }, output_type='div', show_link=False)
    #
    # return chart
