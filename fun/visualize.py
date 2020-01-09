import pandas as pd
import plotly.graph_objs as go

from fun.math import clean_nulls
from sklearn.preprocessing import minmax_scale


def update_figure_3d(
    df,
    x_col = None,
    y_col = None,
    z_col = None,
    group_by = None,
    size_by = None
    ):
    """
    Creates a 3d scatterplot from given parameters.
    :param df: dataframe of data being plotted
    :param x_col: plot on X axis
    :param y_col: plot on Y axis
    :param z_col: plot on Z axis
    :param group_by: a categorical variable which to groupby and plot by layers
    :param size_by: a numerical variable which to scale and plot by. (Add the string `~` to inverse the sizing order)
    """

    if not x_col:
        x_col = 'Age'
    if not y_col:
        y_col = 'Time_on_Social_Personal'
    if not z_col:
        z_col = 'total_optimistic_score'
    if not group_by:
        group_by = 'Social_Most_Value_2'
    if not size_by:
        size_by = '~Age'

    trace_list = []

    if df[group_by].dtype != object:
        # do some transformation
        slice_1 = df[group_by].quantile(0.25)
        slice_2 = df[group_by].quantile(0.50)
        slice_3 = df[group_by].quantile(0.75)
        bins = [df[group_by].min()-1, slice_1, slice_2, slice_3, df[group_by].max()+1]
        df[group_by+'_mod'] = pd.cut(df[group_by],bins=bins, labels=[f'{i} Quantile' for i in range(1, len(bins))])
    else:
        df[group_by+'_mod'] = df[group_by]

    # So that it can be referenced for hover info
    size_by_in = size_by

    if '~' in size_by:
        size_by = size_by.replace('~', '')
        sz = clean_nulls(df[size_by],inverse=True, fill='max')
    else:
        sz = clean_nulls(df[size_by],inverse=False, fill='min')

    z = 5
    sz = minmax_scale(sz,(z,z**2.1))


    for group_id, group_df in df.groupby(group_by+'_mod'):

        trace = go.Scatter3d(
            x=group_df[x_col],
            y=group_df[y_col],
            z= group_df[z_col],
            name=group_id,
            mode='markers',
            marker=dict(
                size = sz,
                sizemin = 2*z,
                opacity=0.75,
            ),
            text=group_df[group_by],
            customdata=group_df[size_by],
            hovertemplate=
                f"<b>{group_by}</b> " + "(%{text})<br><br>" +
                f"<i>Sized by {size_by_in}: " + "%{customdata:,.0f}</i><br>" +
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
        width=900,
        height=900,

        # Create your axis
        scene=dict(
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=2, y=2, z=0.1)
                ),

            xaxis = dict(
                title = x_col,
                color='white',
                range = [df[x_col].min(), df[x_col].max()] if 'score' not in x_col else [0,100]
                ),
            yaxis = dict(
                title = y_col,
                color='white',
                range = [df[y_col].min(), df[y_col].max()] if 'score' not in y_col else [0,100]
            ),
            zaxis = dict(
                title = z_col,
                color='white',
                range = [df[z_col].min(), df[z_col].max()] if 'score' not in z_col else [0,100]
                ),
            aspectmode='cube', #this string can be 'data', 'cube', 'auto', 'manual'
            aspectratio=dict(x=1, y=1, z=1.0)
        ),
        plot_bgcolor = 'rgb(255, 255, 255, 0.0)',
        paper_bgcolor = 'rgb(255, 255, 255, 0.0)',
        autosize=True,
        legend = dict(x = 0.8,y=0.9, bgcolor='rgb(26, 28, 35, 0.0)'),
    )

    figure = {'data':trace_list, 'layout':layout}

    return figure
