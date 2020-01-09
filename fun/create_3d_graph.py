import pandas as pd
import plotly.graph_objs as go



def create_3d_graph(df, x_col = 'Age', y_col = 'Time_on_Social_Personal',z_col = 'total_optimistic_score',group_by = 'Social_Most_Value_2'):
    """
    Creates a goddamn 3d visualization!
    """

    trace_list = []

    for group_id, group_df in df.groupby('Social_Most_Value_2'):

        trace = go.Scatter3d(
            x=group_df[x_col],
            y=group_df[y_col],
            z= group_df[z_col],
            name=group_id,
            mode='markers',
            marker=dict(
                # color = colors[group_id],
                size = group_df['Age']/3,
                sizemin = 8,
                opacity=0.5,
            ),
            # Use these to acces diff data for your hover!
            text=group_df[z_col],
            # customdata=ggroup_df[z_col],
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
