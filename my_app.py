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
from fun.create_3d_graph import create_3d_graph


# --------------------------------------------------------------------------------
#                 I N S T A N T I A T E    T H E    A P P
# --------------------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Get the project details
with open('assets/project_details.json') as f:
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
        # Some titles
        html.H1(proj_deets['project_title'],  style={'marginLeft':'5%'}),
        html.P(proj_deets['project_description'],  style={'marginLeft':'5%'}),
        # collapsable
        html.H2(
            id='collapsable-header',
            children = 'If you want to join in on the fun, stick to this side of the room',
            n_clicks=0,
            style={'marginLeft':'5%', 'color':'orange','size':'3rem',  'cursor': 'pointer'}
        ),
        html.Div(
            id='collapsable-content',
            children = [
                html.Div(children = 'This is a setence about this thing. You love it!'),
                html.Hr()
            ],
            style={'marginLeft':'10%', 'marginRight':'5%'}
        ),

        # Store the data
        html.Div(id="data-load-permission", children='-',style={"display":"none"}),
        dcc.Store(id='data-1'),
        dcc.Store(id='data-2', storage_type='memory'),
        dcc.Dropdown(id='x-axis-dropdown', className="dropdown",  multi=False),
        html.Div(
            id='data-viz-1',
            className='row',
            children =[
                dcc.Graph(
                    id='data-viz-1-graph',
                    className="graph-3d",
                    config={
                        "modeBarButtonsToRemove": ['toImage', 'zoomIn', 'zoomOut','toggleSpikelines','hoverCompareCartesian', 'hoverClosestCartesian'],
                        "displaylogo":False,
                        },
                    style={'height': '90vh','max-height': '81vh', 'horizontalAlign':'center','verticalAlign':'middle'}
                )
            ]
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
    Output('data-1', 'data'),
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

    return data


@app.callback(
    Output('x-axis-dropdown', 'options'),
    [Input('data-1', 'data')]
    )
def update_dropdown(data):
    """
    Updates the children of this dropdown menu
    :params data: the data of this thing!
    """
    if not data:
        raise PreventUpdate
    df = pd.DataFrame.from_records(data)
    options = [{'label':x, 'value':x} for x in df.columns]
    return options

#
# Create your data visualization
@app.callback(
    Output('data-viz-1-graph', 'figure'),
    [Input('data-1', 'data'),
    Input('x-axis-dropdown', 'value')]
    )
def load_data(data, x_axis):
    """
    Load the data and stores it (if you have permission)
    :params permission: permission to load the data?
    """
    if not data:
        raise PreventUpdate
    logger.info(f'Creating the data visualization for the id data-viz-1')

    df = pd.DataFrame.from_records(data)

    # If this isn't here, you get errors
    if not x_axis:
        x_axis = 'Age'

    figure = create_3d_graph(df=df, x_col=x_axis)
    # ------------------------------------------------

    return figure

# --------------------------------------------------------------------------------
#                 F I N I S H E D


port = 5000
url = f"http://127.0.0.1:{port}"


if __name__ == '__main__':
    # Run the actual app
    app.run_server(debug=True, dev_tools_ui=True, port=port)
    # app.run_server()
