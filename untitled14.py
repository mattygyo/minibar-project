#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 13:49:41 2020

@author: matthewgrierson
"""


from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.models.widgets.tables import DataTable, TableColumn
from bokeh.layouts import row
from bokeh.io import curdoc
import os

source = ColumnDataSource(dict(
    x=[1, 2, 3, 4, 5, 6],
    y=[1, 2, 3, 4, 5, 6],
))

p = figure(
    plot_height=300,
    tools='lasso_select'
)

rc = p.scatter(
    x='x',
    y='y',
    size=20,
    color='red',
    source=source,
    fill_alpha=1.0,
    line_alpha=1.0,
)

columns = [
    TableColumn(field="x", title="Value"),
    TableColumn(field="x", title="Value")
]
#init_cds = ColumnDataSource(data=dict(value=['']))
table = DataTable(
    source=source,
    columns=columns,
    reorderable=False,
)

def update_table(attr, old, new):
    print(new.indices)
    if new.indices != []:
        new_vals_dict = {'value': new.indices}
    else:
        new_vals_dict = {'value': ['']}
    table.source.data = new_vals_dict

source.on_change('selected', update_table)

curdoc().add_root(row(children=[p, table]))

os.system("bokeh serve --show untitled14.py")