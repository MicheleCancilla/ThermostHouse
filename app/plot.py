#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import StringIO

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot(thermostat):
    # from models.historicals import Historicals
    # history = Historicals()
    # history.temperature = 12.4
    # history.mode = 'Heat'
    # thermostat.history.append(history)
    # thermostat.put()
    # return
    last_month = datetime.date.today() - datetime.timedelta(days=30)
    last_month = datetime.datetime.combine(last_month, datetime.datetime.min.time())

    tmin = 100
    tmax = -100
    toffset = 10
    data_to_plot = []
    temperature_to_plot = []
    if thermostat.history:
        for sample in thermostat.history:
            if sample.timestamp > last_month:
                data_to_plot.append(sample.timestamp)
                temperature_to_plot.append(sample.temperature)
                if sample.temperature < tmin:
                    tmin = sample.temperature
                if sample.temperature > tmax:
                    tmax = sample.temperature
    else:
        # no history saved, adjust the scale
        tmin = -90
        tmax = 90
    # print data_to_plot
    fig, ax = plt.subplots()
    ax.plot(data_to_plot, temperature_to_plot, 'o-')
    ax.set_xlabel('Time', color='r')
    ax.set_ylabel('Temperature', color='0.5')  # grayscale color
    ax.grid(True)

    ax.set_xlim(last_month, datetime.date.today())
    ax.set_ylim(tmin - toffset, tmax + toffset)

    # format the coords message box
    def temp(x):
        return '%f' % x

    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.format_ydata = temp

    fig.autofmt_xdate()
    sio = StringIO.StringIO()
    plt.savefig(sio, format="png")
    img_b64 = sio.getvalue().encode("base64").strip()
    plt.clf()
    sio.close()
    return "<img src='data:image/png;base64,%s'/>" % img_b64
