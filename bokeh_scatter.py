import os
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, LinearColorMapper, ColorBar, CategoricalColorMapper, Legend, LegendItem, CustomJS
from bokeh.plotting import figure
from bokeh.transform import jitter
from bokeh.palettes import Reds9, Turbo256, d3
from bokeh.models.widgets import CheckboxButtonGroup, DataTable, TableColumn

df = pd.read_csv('beer_data.csv')
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

desc = Div(text=open("description.html").read(), sizing_mode="stretch_width")

# Create Input controls
pack_size_options = list(df['short_pack_size'].unique())
pack_size_options.append("All")
container_options = list(df['container_type'].unique())
hierarchy_options = list(df['hierarchy_type'].unique())
hierarchy_options.append("All")
sub_hierarchy_options = list(df['hierarchy_subtype'].unique())
sub_hierarchy_options.append("All")

# Create Widget Filters
min_abv = Slider(title="ABV", start=0, end=20, value=1, step=1)
jitter_amt = Slider(title="Jitter", start=0, end=1.0, value=0.1, step=0.1)
container_check = CheckboxButtonGroup(labels=container_options, active=[0, 2])
brand = TextInput(title="Brand of Beer")
pack_size = Select(title="Pack Size", value="All", options=pack_size_options)
hierarchy = Select(title='Category', value="All", options=hierarchy_options)
sub_hierarchy = Select(title='Sub-Category', value="All", options=sub_hierarchy_options)
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Oz of Alcohol per $")
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="ABV")
circle_color = Select(title="Circle Color", options=sorted(color_axis_map.keys()), value="Price")

# Create Column Data Sources that will be used by the plot and table
source = ColumnDataSource(data=dict(df))
table_source = ColumnDataSource(data=dict(df))

#Create the tooltips
tooltips=[
    ("Name", "@name"),
    ("Brand", "@brand"),
    ("Price $", "@price"),
    ("ABV", "@alcohol_pct"),
    ("Category", "@hierarchy_type"),
    ("Category Sub-type", "@hierarchy_subtype")
]

#Create the initial LinearColorScale so it can be updated dynamically later
Reds9.reverse()
cmap = LinearColorMapper(palette=Reds9, 
                             low = min(df[color_axis_map[circle_color.value]]), 
                             high = max(df[color_axis_map[circle_color.value]]))

#Rescale linear colormap
def rescale_color(cmap, df):
    cmap.low = min(df[color_axis_map[circle_color.value]])
    cmap.high = max(df[color_axis_map[circle_color.value]])
    return cmap

#Redraw categorical color maps
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
             toolbar_location='below', tooltips=tooltips,tools="box_select,reset,help")
c = p.circle(x=jitter('x', width=jitter_amt.value, range=p.x_range), y=jitter('y', width=jitter_amt.value, range=p.y_range), source=source, size='price', 
             fill_color={"field":color_axis_map[circle_color.value], "transform":cat_linear_color_toggle()}, 
             line_color=None
             )
bar = ColorBar(background_fill_color='gray', background_fill_alpha=0,
                   color_mapper=cmap#cat_linear_color_toggle()
                   , location=(0,0),visible=True)
p.add_layout(bar, "right")

legend = Legend(items=[LegendItem(label=dict(field="x"), renderers=[c])], 
                location=(10, -30),background_fill_alpha=0, visible=False)
p.add_layout(legend, 'right')

columns = [
    TableColumn(field="name", title='Name'),
    TableColumn(field="type", title='Type'),
    TableColumn(field="container_type", title='Container Type'),
    TableColumn(field="short_pack_size", title='Pack Size'),
    TableColumn(field="short_volume", title='Volume'),
    TableColumn(field="price", title='Price'),
    TableColumn(field="alcohol_pct", title='ABV'),
    TableColumn(field="cost per oz", title='Cost per Oz'),
    TableColumn(field="oz of alcohol per dollar", title='Oz of Alcohol per $'),
    ]

data_table = DataTable(source = table_source, columns = columns, selectable = False)

def select_beers():
    container_check_val = container_check.active
    abv_val = min_abv.value
    brand_val = brand.value
    pack_size_val = pack_size.value
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
    if (pack_size_val != "All"):
        selected = selected[selected.short_pack_size.str.contains(pack_size_val)==True]
    if (hierarchy_val != "All"):
        selected = selected[selected.hierarchy_type.str.contains(hierarchy_val)==True]
    if (sub_hierarchy_val != "All"):
        selected = selected[selected.hierarchy_subtype.str.contains(sub_hierarchy_val)==True]
    return selected

def update():
    df1 = select_beers()
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
        name=df1["name"],
        brand=df1["brand"],
        price=df1["price"],
        container_type = df1["container_type"],
        hierarchy_type=df1["hierarchy_type"],
        hierarchy_subtype=df1["hierarchy_subtype"],
        short_pack_size=df1["short_pack_size"],
        alcohol_pct = df1["alcohol_pct"],
        short_volume = df1["short_volume"],
        supplier_id = df1["supplier_id"],
        type = df1["type"]
    )
    source.data.update(
        {"oz of alcohol per dollar": df1["oz of alcohol per dollar"],
        "cost per oz": df1["cost per oz"]}
        )
    table_source.data = source.data
    
    c.glyph.x = jitter('x', width=jitter_amt.value, range=p.x_range)
    c.glyph.y = jitter('y', width=jitter_amt.value, range=p.y_range)
        
def show_hide_legend(attr, old, new):
    color_val = color_axis_map[circle_color.value]      
    if df[color_val].dtype in (float, int):
        p.legend.visible = False
        bar.visible = True
    else:
        p.legend.visible = True
        bar.visible = False
    
source.selected.js_on_change('indices', CustomJS(args=dict(source=source, table_source=table_source), code="""
        console.log(source.data)
        var inds = cb_obj.indices;
        var d1 = source.data;
        
        if(inds.length == 0){
            table_source.data = d1
        }
        else{
        d2 = {'name': [], 'type': [], 'container_type': [], 'short_pack_size': [], 'short_volume': [], 
        'price': [], 'alcohol_pct': [], 'cost per oz': [], 'oz of alcohol per dollar': []}
        
        for (var i = 0; i < inds.length; i++) {
            d2['name'].push(d1['name'][inds[i]])
            d2['type'].push(d1['type'][inds[i]])
            d2['container_type'].push(d1['container_type'][inds[i]])
            d2['short_pack_size'].push(d1['short_pack_size'][inds[i]])
            d2['short_volume'].push(d1['short_volume'][inds[i]])
            d2['price'].push(d1['price'][inds[i]])
            d2['alcohol_pct'].push(d1['alcohol_pct'][inds[i]])
            d2['cost per oz'].push(d1['cost per oz'][inds[i]])
            d2['oz of alcohol per dollar'].push(d1['oz of alcohol per dollar'][inds[i]])
        }
        table_source.data = d2
        }
    """)
)

circle_color.on_change('value', show_hide_legend)

controls = [min_abv, jitter_amt, container_check, brand, pack_size, hierarchy, sub_hierarchy, x_axis, y_axis, circle_color]

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