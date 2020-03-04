#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 18:14:24 2020

@author: matthewgrierson
"""


from random import random
from bokeh.models import CustomJS, ColumnDataSource, Row
from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import Button

x = [random() for x in range(500)]
y = [random() for y in range(500)]

s1 = ColumnDataSource(data = dict(x = x, y = y))
p1 = figure(plot_width = 400, plot_height = 400, tools = "lasso_select", title = "Select Here")
p1.circle('x', 'y', source = s1, alpha = 0.6)

s2 = ColumnDataSource(data = dict(x = [], y = []))
p2 = figure(plot_width = 400, plot_height = 400, x_range = (0, 1), y_range = (0, 1), tools = "", title = "Watch Here")
p2.circle('x', 'y', source = s2, alpha = 0.6)

s1.selected.js_on_change('indices', CustomJS(args = dict(s1 = s1, s2 = s2), code = """
        var inds = cb_obj.indices;
        var d1 = s1.data;
        d2 = {'x': [], 'y': []}
        for (var i = 0; i < inds.length; i++) {
            d2['x'].push(d1['x'][inds[i]])
            d2['y'].push(d1['y'][inds[i]])
        }
        s2.data = d2  """))

def get_values():
    print(s2.data)

button = Button(label = "Get selected set")
button.on_click(get_values)

curdoc().add_root(Row(p1, p2, button))

import os
os.system("bokeh serve --show untitled17.py")