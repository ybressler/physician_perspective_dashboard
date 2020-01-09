import pandas as pd
import plotly.graph_objs as go

from fun.math import clean_nulls
from sklearn.preprocessing import minmax_scale


def update_figure_3d(
    df,
    x_col = 'Age',
    y_col = 'Time_on_Social_Personal',
    z_col = 'total_optimistic_score',
    group_by = 'Social_Most_Value_2',
    sizeby = '~Age'
    ):
    """
    Creates a 3d scatterplot from given parameters.
    :param df: dataframe of data being plotted
    :param x_col: plot on X axis
    :param y_col: plot on Y axis
    :param z_col: plot on Z axis
    :param group_by: a categorical variable which to groupby and plot by layers
    :param sizeby: a numerical variable which to scale and plot by. (Add the string `~` to inverse the sizing order)
    """

    trace_list = []

    if group_by not in ['Social_Most_Value_2']:
        # do some transformation.
        None


    if '~' in sizeby:
        sizeby = sizeby.replace('~', '')
        sz = clean_nulls(df[sizeby],inverse=True, fill='max')
    else:
        sz = clean_nulls(df[sizeby],inverse=False, fill='min')

    z = 5
    sz = minmax_scale(sz,(z*2,z*8))


    for group_id, group_df in df.groupby():

        trace = go.Scatter3d(
            x=group_df[x_col],
            y=group_df[y_col],
            z= group_df[z_col],
            name=group_id,
            mode='markers',
            marker=dict(
                size = group_df['Age']/3,
                sizemin = 8,
                opacity=0.75,
            ),
            text=group_df[z_col],
            # customdata=group_df[sizeby],
            hovertemplate=
                f"<b>{group_id}</b><br><br>" +
                f"{x_col}: " + "%{x:,.0f}<br>" +
                f"{y_col}: " + "%{y:,.0f}<br>" +
                f"{z_col}: " + "%{z:,.0f}<br>" +
                "<extra></extra>",
        )

        trace_list.append(trace)


    # Now the layout
    layout = go.Layout(

        clickmode='event+select',
        dragmode = 'select',

        # Create your axis
        scene=dict(
            xaxis = dict(
                title = x_col,
                color='white',
                ),
            yaxis = dict(
                title = y_col,
                color='white',
            ),
            zaxis = dict(
                title = z_col,
                color='white',
                ),
            aspectmode='cube', #this string can be 'data', 'cube', 'auto', 'manual'
            aspectratio=dict(x=1, y=1, z=0.95)
        ),
        plot_bgcolor = 'rgb(255, 255, 255, 0.0)',
        paper_bgcolor = 'rgb(255, 255, 255, 0.0)',
        # autosize=True,
        legend = dict(x = 1.0,y=1.0, bgcolor='rgb(26, 28, 35, 0.0)'),
    )

    figure = {'data':trace_list, 'layout':layout}

    return figure
