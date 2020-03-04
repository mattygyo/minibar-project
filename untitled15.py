#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 15:12:32 2020

@author: matthewgrierson
"""


from datetime import date
from random import randint
import os

from bokeh.io import output_file, show, curdoc
from bokeh.plotting import figure
from bokeh.layouts import widgetbox, row
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn,Button

output_file("data_table.html")

data = dict(
        dates=[date(2014, 3, i+1) for i in range(10)],
        downloads=[randint(0, 100) for i in range(10)],
    )

def update():
    #set inds to be selected
    inds = [1,2,3,4]
    source.selected = {'0d': {'glyph': None, 'indices': []},
                                '1d': {'indices': inds}, '2d': {}}
    # set plot data
    plot_dates = [data['dates'][i] for i in inds]
    plot_downloads = [data['downloads'][i] for i in inds]
    plot_source.data['dates'] = plot_dates
    plot_source.data['downloads'] = plot_downloads


source = ColumnDataSource(data)
plot_source = ColumnDataSource({'dates':[],'downloads':[]})


table_button = Button(label="Press to set", button_type="success")
table_button.on_click(update)
columns = [
        TableColumn(field="dates", title="Date", formatter=DateFormatter()),
        TableColumn(field="downloads", title="Downloads"),
    ]
data_table = DataTable(source=source, columns=columns, width=400, height=280)

p = figure(plot_width=400, plot_height=400)

# add a circle renderer with a size, color, and alpha
p.circle('dates','downloads',source=plot_source, size=20, color="navy", alpha=0.5)


curdoc().add_root(row([table_button,data_table,p]))

os.system("bokeh serve --show untitled15.py")