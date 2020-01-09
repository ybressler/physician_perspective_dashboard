# Publish on Heroku with a flask server
from flask import Flask
import flask


# Import logging module
import logging


# Standard packages
import re
import os
import json
import pandas as pd
import datetime

# Set the pandas options for printing...
pd.options.display.max_columns = 60
pd.set_option('max_colwidth', 200)

import pathlib


# dash packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq

from dash.dependencies import Input, Output, State
# import dash_table
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate


# Load private stuff
from fun.visualize import update_figure_3d


# --------------------------------------------------------------------------------
#                 I N S T A N T I A T E    T H E    A P P
# --------------------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Get the project details
with open(pathlib.Path('assets/project_details.json')) as f:
    proj_deets = json.load(f)

# Instantiate meta tags
meta_tags = {
    "viewport":"width=device-width",
    "title": proj_deets["meta_title"],
    "description": proj_deets["meta_description"],
    "og: description": proj_deets["meta_og_description"],
    }


# Set up the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} | {levelname} | {name} | {message}", style="{"
)
logger = logging.getLogger(__name__)

# Instantiate the flask server
server = Flask(__name__)


app = dash.Dash(__name__, server=server, meta_tags=[{"name":k, "content":v} for k,v in meta_tags.items()])
app.title = meta_tags.get('title')
app.config.suppress_callback_exceptions = True


# --------------------------------------------------------------------------------
#                 L O A D   D A T A
# --------------------------------------------------------------------------------
# Get the paths
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()


# --------------------------------------------------------------------------------
#                 G E N E R A T E    T H E   A C T U A L   A P P
# --------------------------------------------------------------------------------
app.layout = html.Div(
    children = [
        # Save stuff
        html.Div(id="data-load-permission", children='-',style={"display":"none"}),
        dcc.Store(id='data-1'),
        dcc.Store(id='axis-options', storage_type='memory'),
        dcc.Store(id='axis-values', storage_type='memory'),

        # Some titles
        html.H1(proj_deets['project_title'],  style={'marginLeft':'5%'}),
        html.P(proj_deets['project_description'],  style={'marginLeft':'5%'}),

        # collapsable
        html.Hr(),
        html.Div(className='left-column',
            children = [
                html.H2(
                    id='collapsable-header',
                    children = 'Toggle User Selections',
                    n_clicks=0,
                    style={'marginLeft':'5%', 'color':'orange','size':'3rem',  'cursor': 'pointer'}
                ),
                html.Div(
                    id='collapsable-content',
                    children = [

                        html.Div(className="row", children=[
                            html.Div(className='dropdown-label', children ='X Axis'),
                            html.Div(className='dropdown-container', children = dcc.Dropdown(id='x-axis-dropdown', className="dropdown",  multi=False, clearable=False, persistence=True,searchable=False, placeholder="Select your X axis...")),
                        ]),

                        html.Div(className="row", children=[
                            html.Div(className='dropdown-label', children ='Y Axis'),
                            html.Div(className='dropdown-container', children = dcc.Dropdown(id='y-axis-dropdown', className="dropdown",  multi=False, clearable=False, persistence=True, searchable=False, placeholder="Select your Y axis...")),
                        ]),

                        html.Div(className="row", children=[
                            html.Div(className='dropdown-label', children ='Z Axis'),
                            html.Div(className='dropdown-container', children = dcc.Dropdown(id='z-axis-dropdown', className="dropdown",  multi=False, clearable=False, persistence=True, searchable=False, placeholder="Select your Z axis...")),
                        ]),

                        html.Div(className="row", children=[
                            html.Div(className='dropdown-label', children ='Groupby'),
                            html.Div(className='dropdown-container', children = dcc.Dropdown(id='groupby-dropdown', className="dropdown",  multi=False, clearable=False, persistence=True, searchable=False, placeholder="Select your Groupby...")),
                        ]),

                        html.Div(className="row", children=[
                            html.Div(className='dropdown-label', children ='Sizeby'),
                            html.Div(className='dropdown-container', children = dcc.Dropdown(id='sizeby-dropdown', className="dropdown",  multi=False, clearable=False, persistence=True, searchable=False, placeholder="Select your Sizeby...")),
                        ]),

                        html.Hr()
                        ],
                        style={'marginLeft':'10%', 'marginRight':'5%'}
                    ),
                ]
        ),
        html.Div(
            className='right-column',
            children=[
                html.Div(
                    id='data-viz-1',
                    className='graph-row',
                    children =[
                        dcc.Graph(
                            id='data-viz-1-graph',
                            className="graph-3d",
                            config={
                                "modeBarButtonsToRemove": ['toImage', 'zoomIn', 'zoomOut','toggleSpikelines','hoverCompareCartesian', 'hoverClosestCartesian'],
                                "displaylogo":False,
                                "autosizable":True,
                                "responsive":True,
                            },
                            style={
                                'vertical-align':'top', 'overflowY':'overflow'
                            }
                        )
                    ]
                )
            ],
        )
    ]
)


# --------------------------------------------------------------------------------

@app.callback(
    Output('collapsable-content', 'style'),
    [Input('collapsable-header', 'n_clicks')],
    [State('collapsable-content', 'style')]
    )
def collapse_stuff(n_clicks, style):
    """
    If the thing is clicked, collapse it
    :param n_clicks: the number of clicks
    :param style: the style of the collapse thing
    """
    # This is not password data... This is the big motherload
    if not style:
        raise PreventUpdate

    if n_clicks%2 == 0:
        style['display'] = 'block'
    else:
        style['display'] = 'none'

    return style


# Load the data

@app.callback(
    [Output('data-1', 'data'),
    Output('axis-options', 'data')],
    [Input('data-load-permission', 'children')]
    )
def load_data(permission):
    """
    Load the data and stores it (if you have permission)
    :params permission: permission to load the data?
    """
    if not permission:
        raise PreventUpdate

    if os.path.isfile(pathlib.Path('Data/Clean_dr_data.csv')):
        data_path = pathlib.Path('Data/Clean_dr_data.csv')
    else:
        data_path = pathlib.Path('Data/Clean_anonymized_dr_data.csv')

    logger.info(f'Loading data from', data_path)
    df = pd.read_csv(data_path)
    data = df.to_dict()

    axis_data = {x:None for x in df.columns}
    return data, axis_data


@app.callback(
    [Output('x-axis-dropdown', 'options'),
    Output('y-axis-dropdown', 'options'),
    Output('z-axis-dropdown', 'options'),
    Output('groupby-dropdown', 'options'),
    Output('sizeby-dropdown', 'options')],
    [Input('axis-options', 'data'),
    Input('axis-values', 'data')]
    )
def update_dropdown(axis_data, axis_data_2):
    """
    Updates the data layer for all dropdown menus
    :params axis_data: the data of this thing!
    """
    if not axis_data:
        raise PreventUpdate

    if not axis_data_2:
        axis_data_2 = {}

    # If the second doesn't exist, Instantiate them
    x_options = [{'label':k, 'value':k} for k in axis_data.keys() if axis_data_2.get(k) not in ['y_axis', 'z_axis', 'groupby', 'sizeby']]
    y_options = [{'label':k, 'value':k} for k in axis_data.keys() if axis_data_2.get(k) not in ['x_axis', 'z_axis', 'groupby','sizeby']]
    z_options = [{'label':k, 'value':k} for k in axis_data.keys() if axis_data_2.get(k) not in ['x_axis', 'y_axis', 'groupby', 'sizeby']]
    grp_options = [{'label':k, 'value':k} for k in axis_data.keys() if axis_data_2.get(k) not in ['x_axis', 'y_axis', 'z_axis','sizeby']]
    sz_options = [{'label':k, 'value':k} for k in axis_data.keys() if axis_data_2.get(k) not in ['x_axis', 'y_axis', 'z_axis','groupby']]

    return x_options, y_options, z_options, grp_options, sz_options

@app.callback(
    Output('axis-values', 'data'),
    [Input('x-axis-dropdown', 'value'),
    Input('y-axis-dropdown', 'value'),
    Input('z-axis-dropdown', 'value'),
    Input('groupby-dropdown', 'value'),
    Input('sizeby-dropdown', 'value')]
    )
def update_dropdown(x_axis, y_axis, z_axis, group_by, size_by):
    """
    Updates the data layer for all dropdown menus
    :params axis_data: the data of this thing!
    """

    data = {}

    for k, v in zip([x_axis, y_axis, z_axis, group_by, size_by], ['x_axis','y_axis','z_axis', 'group_by', 'size_by']):
        if k:
            data[k] = v
    logger.info(f'Updating axis. data: {data}')

    return data


# Create your data visualization
@app.callback(
    Output('data-viz-1-graph', 'figure'),
    [Input('data-1', 'data'),
    Input('axis-values', 'data')]
    )
def create_graph(data, axis_data):
    """
    Create a s 3d graph.
    """
    if not data:
        raise PreventUpdate
    logger.info(f'Creating the data visualization for the id data-viz-1')

    df = pd.DataFrame.from_records(data)

    axis_data_inversed = {v:k for k,v in axis_data.items()} if axis_data else {}
    x_col = axis_data_inversed.get('x_axis')
    y_col = axis_data_inversed.get('y_axis')
    z_col = axis_data_inversed.get('z_axis')
    group_by = axis_data_inversed.get('group_by')
    size_by = axis_data_inversed.get('size_by')

    for z in [x_col,y_col,z_col]:
        if z and 'Social_Most_Value_2' in z:
            raise PreventUpdate

    figure = update_figure_3d(df=df, x_col=x_col, y_col=y_col, z_col=z_col, group_by=group_by, size_by=size_by)
    # ------------------------------------------------

    return figure

# --------------------------------------------------------------------------------
#                 F I N I S H E D


port = 5000
url = f"http://127.0.0.1:{port}"


if __name__ == '__main__':
    # Run the actual app
    # app.run_server(debug=True, dev_tools_ui=True, port=port)
    app.run_server()
