#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 16:11:50 2020

@author: matthewgrierson
"""

import os
import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, LinearColorMapper, ColorBar, CategoricalColorMapper, Legend, LegendItem
from bokeh.plotting import figure
from bokeh.transform import jitter
from bokeh.palettes import Reds9, Turbo256, d3
from bokeh.models.widgets import CheckboxButtonGroup, DataTable, TableColumn

df = pd.read_csv('beer_data.csv')

df["color"] = np.where(df["alcohol_pct"] > 5, "orange", "grey")
df["alpha"] = np.where(df["alcohol_pct"] > 0, 0.9, 0.25)
df['brand'] = df['brand'].str.lower().str.strip()
df['hierarchy_type'] = ['uncat' if str(x)=='nan' else x for x in df['hierarchy_type']]
df['hierarchy_subtype'] = ['uncat' if str(x)=='nan' else x for x in df['hierarchy_subtype']]

axis_map = {
    "Oz of Alcohol per $": "oz of alcohol per dollar",
    "Cost per Oz": "cost per oz",
    "ABV": "alcohol_pct",
    "Pack Size": "short_pack_size_num",
    "Volume (Oz)": "standard vol",
    "Price": "price"
}

color_axis_map = {
    "ABV": "alcohol_pct",
    "Brand": "brand",
    "Container Type": "container_type",
    "Category": "hierarchy_type",
    "Sub-Category": "hierarchy_subtype",
    "Price": "price",
    "Pack Size": "short_pack_size",
    "Volume": "short_volume",
    "Supplier": "supplier_id",
    "Type": "type",
    "Oz of Alcohol per $": "oz of alcohol per dollar",
    "Cost per Oz": "cost per oz"
}


desc = Div(sizing_mode="stretch_width")

# Create Input controls
container_options = list(df['container_type'].unique())
hierarchy_options = list(df['hierarchy_type'].unique())
hierarchy_options.append("All")
sub_hierarchy_options = list(df['hierarchy_subtype'].unique())
sub_hierarchy_options.append("All")
#---------------------------------------------------------------------------
min_abv = Slider(title="ABV", start=0, end=20, value=1, step=1)
container_check = CheckboxButtonGroup(labels=container_options, active=[0, 2])
brand = TextInput(title="Brand of Beer")
hierarchy = Select(title='Category', value="All", options=hierarchy_options)
sub_hierarchy = Select(title='Sub-Category', value="All", options=sub_hierarchy_options)
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Oz of Alcohol per $")
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Pack Size")
circle_color = Select(title="Circle Color", options=sorted(color_axis_map.keys()), value="Price")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(df))

TOOLTIPS=[
    ("Name", "@name"),
    ("Brand", "@brand"),
    ("Price $", "@price"),
    ("ABV", "@alcohol_pct"),
    ("Category", "@hierarchy_type"),
    ("Category Sub-type", "@hierarchy_subtype")
]

Reds9.reverse()
cmap = LinearColorMapper(palette=Reds9, 
                             low = min(df[color_axis_map[circle_color.value]]), 
                             high = max(df[color_axis_map[circle_color.value]]))

def rescale_color(cmap, df):
    cmap.low = min(df[color_axis_map[circle_color.value]])
    cmap.high = max(df[color_axis_map[circle_color.value]])
    return cmap

def cat_linear_color_toggle():
    color_val = color_axis_map[circle_color.value]
    if df[color_val].dtype == 'float64' or df[color_val].dtype == 'int64':
        color_mapper = rescale_color(cmap, df)
    else:
        cat_list=list(df[color_val].astype(str).unique())
        if len(cat_list) < 30:
            colors = d3['Category20'][20]+d3['Category20b'][10]
            color_mapper = CategoricalColorMapper(factors=cat_list, palette=colors)
        else:     
            color_mapper = CategoricalColorMapper(factors=cat_list, palette=Turbo256)
    return color_mapper

p = figure(background_fill_color='black', background_fill_alpha=0.5,
             border_fill_color='gray', border_fill_alpha=0.25,
             plot_height=250, plot_width=500, title="", 
             toolbar_location='below', tooltips=TOOLTIPS)
c = p.circle(x='x', y='y', source=source, size='price', 
             fill_color={"field":color_axis_map[circle_color.value], "transform":cat_linear_color_toggle()}, 
             line_color=None, fill_alpha="alpha"#, legend_field=color_axis_map[circle_color.value]
             )
bar = ColorBar(background_fill_color='gray', background_fill_alpha=0,
                   color_mapper=cmap#cat_linear_color_toggle()
                   , location=(0,0),visible=True)
p.add_layout(bar, "right")

legend = Legend(items=[LegendItem(label=dict(field="x"), renderers=[c])], 
                location=(10, -30),background_fill_alpha=0)
p.add_layout(legend, 'right')
legend.visible = False

columns = [
    TableColumn(field="name", title='Name'),
    TableColumn(field="container_type", title='Container Type'),
    TableColumn(field="short_pack_size", title='Pack Size'),
    TableColumn(field="short_volume", title='Volume'),
    TableColumn(field="price", title='Price'),
    TableColumn(field="type", title='Type'),
    TableColumn(field="cost per oz", title='Cost/Oz.'),
    TableColumn(field="oz of alcohol per dollar", title='Oz. of Alcohol per $'),
    ]

data_table = DataTable(source = source, columns = columns)

def select_movies():
    container_check_val = container_check.active
    abv_val = min_abv.value
    brand_val = brand.value
    brand_val = brand_val.lower().strip()
    hierarchy_val = hierarchy.value
    sub_hierarchy_val = sub_hierarchy.value
    selected = df[df['alcohol_pct'] > abv_val]
    if (container_check_val != 4):
        container_name_list = []
        for i in container_check_val:
            container_name_list.append(container_check.labels[i])
        if len(container_name_list) == 0:
            container_name_list = container_options
        selected = selected[selected.container_type.isin(container_name_list)==True]
    if (brand_val != ""):
        selected = selected[selected.brand.str.contains(brand_val)==True]
    if (hierarchy_val != "All"):
        selected = selected[selected.hierarchy_type.str.contains(hierarchy_val)==True]
    if (sub_hierarchy_val != "All"):
        selected = selected[selected.hierarchy_subtype.str.contains(sub_hierarchy_val)==True]
    return selected

def update():
    df1 = select_movies()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]
    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d beers selected" % len(df1)
    color_select = color_axis_map[circle_color.value]

    c.glyph.fill_color = {"field":color_axis_map[circle_color.value], "transform":cat_linear_color_toggle()}
    p.legend.items[0].label= {'field': color_axis_map[circle_color.value]}
    if df1[color_select].dtype in (float, int):
        bar.color_mapper = rescale_color(cmap, df1)
    source.data = dict(
        x=df1[x_name],
        y=df1[y_name],
        color=df1["color"],
        name=df1["name"],
        brand=df1["brand"],
        price=df1["price"],
        container_type = df1["container_type"],
        hierarchy_type=df1["hierarchy_type"],
        hierarchy_subtype=df1["hierarchy_subtype"],
        short_pack_size=df1["short_pack_size"],
        alpha=df1["alpha"],
        alcohol_pct = df1["alcohol_pct"],
        short_volume = df1["short_volume"],
        supplier_id = df1["supplier_id"],
        type = df1["type"]
    )
    source.data.update(
        {"oz of alcohol per dollar": df1["oz of alcohol per dollar"],
        "cost per oz": df1["cost per oz"]}
        )
        
def show_hide_legend(attr, old, new):
    color_val = color_axis_map[circle_color.value]      
    if df[color_val].dtype in (float, int):
        p.legend.visible = False
        bar.visible = True
        #bar.color_mapper = {cat_linear_color_toggle()}
    else:
        p.legend.visible = True
        bar.visible = False
    

circle_color.on_change('value',show_hide_legend)

controls = [min_abv, container_check, brand, hierarchy, sub_hierarchy, x_axis, y_axis, circle_color]

for control in controls:
    if (control==container_check):
        container_check.on_change('active',lambda attr, old, new: update())
    else:
        control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=320, height=500)
inputs.sizing_mode = "fixed"
l = layout([
    [desc],
    [inputs, p],
    [data_table]
], sizing_mode="scale_both")

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Beer"

os.system("bokeh serve --show bokeh_scatter.py")