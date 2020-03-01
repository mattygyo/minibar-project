#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 23:27:49 2020

@author: matthewgrierson
"""


import numpy as np
import pandas as pd

from bokeh.layouts import row, widgetbox
from bokeh.models import Select
from bokeh.models import HoverTool, ColorBar, LinearColorMapper, Label
from bokeh.palettes import Spectral5
from bokeh.plotting import curdoc, figure, ColumnDataSource
from bokeh.sampledata.autompg import autompg_clean as df
import os
df = df.copy()

SIZES = list(range(6, 22, 3))
COLORS = Spectral5

# data cleanup
df.cyl = df.cyl.astype(str)
df.yr = df.yr.astype(str)
columns = sorted(df.columns)

discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
quantileable = [x for x in continuous if len(df[x].unique()) > 20]

def create_figure():
    xs = df[x.value].tolist()
    ys = df[y.value].tolist()
    x_title = x.value.title()
    y_title = y.value.title()
    name = df['name'].tolist()

    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(xs))
    if y.value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s vs %s" % (y_title, x_title)
    
    p = figure(plot_height=600, plot_width=800,
               tools='pan,box_zoom,wheel_zoom,lasso_select,reset,save',
                toolbar_location='above', **kw)
    
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title
    
    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4
    
    if size.value != 'None':
        groups = pd.qcut(df[size.value].values, len(SIZES))
        sz = [SIZES[xx] for xx in groups.codes]
    else:
        sz = [9] * len(xs)        
    
    if color.value != 'None':
        coloring = df[color.value].tolist()
        cv_95 = np.percentile(np.asarray(coloring), 95)
        mapper = LinearColorMapper(palette=Spectral5, 
                                   low=cv_min, high=cv_95)
        mapper.low_color = 'blue'
        mapper.high_color = 'red'
        add_color_bar = True
        ninety_degrees = pd.np.pi / 2.
        color_bar = ColorBar(color_mapper=mapper, title='',
                             #title=color.value.title(),
                             title_text_font_style='bold',
                             title_text_font_size='20px',
                             title_text_align='center',
                             orientation='vertical',
                             major_label_text_font_size='16px',
                             major_label_text_font_style='bold',
                             label_standoff=8,
                             major_tick_line_color='black',
                             major_tick_line_width=3,
                             major_tick_in=12,
                             location=(0,0))
    else:
         c = ['#31AADE'] * len(xs)
         add_color_bar = False
    
    if add_color_bar:
          source = ColumnDataSource(data=dict(x=xs, y=ys, 
                                    c=coloring, size=sz, name=name))
    else:
          source = ColumnDataSource(data=dict(x=xs, y=ys, color=c, 
                                    size=sz, name=name))
    
    if add_color_bar:
         p.circle('x', 'y', fill_color={'field': 'c', 
                  'transform': mapper},
                  line_color=None, size='size', source=source)
    else:
         p.circle('x', 'y', color='color', size='size', source=source)
    
         p.add_tools(HoverTool(tooltips=[('x', '@x'), ('y', '@y'), 
                 ('desc', '@name')]))
    
    if add_color_bar:
         color_bar_label = Label(text=color.value.title(),
                                 angle=ninety_degrees,
                                 text_color='black',
                                 text_font_style='bold',
                                 text_font_size='20px',
                                 x=25, y=300, 
                                 x_units='screen', y_units='screen')
         p.add_layout(color_bar, 'right')
         p.add_layout(color_bar_label, 'right')
    
    
    return p


def update(attr, old, new):
    layout.children[1] = create_figure()


x = Select(title='X-Axis', value='mpg', options=columns)
x.on_change('value', update)

y = Select(title='Y-Axis', value='hp', options=columns)
y.on_change('value', update)

size = Select(title='Size', value='None', 
              options=['None'] + quantileable)
size.on_change('value', update)

color = Select(title='Color', value='None', 
               options=['None'] + quantileable)
color.on_change('value', update)

controls = widgetbox([x, y, color, size], width=200)
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "Crossfilter"

os.system("bokeh serve --show untitled10.py")