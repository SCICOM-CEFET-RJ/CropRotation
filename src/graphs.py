import plotly.express as px

def plot_one_scatter(dt, x, y, labels = None):
    fig = px.scatter(dt, 
                x = x, 
                y = y, 
                #title='Função Objetivo (g) versus λ',
                #title='Objective Function (z<sub>2y</sub>) versus λ',
                #color='alpha_type',
                labels=labels)
                        
    fig.update_traces(marker=dict(color='rgb(115, 115, 115)',
                                size=3
                                )
                        )

    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=False,
            showline=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        autosize=False,
        margin=dict(
            autoexpand=True,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=True,
        plot_bgcolor='white'
    )
    #fig['data'][0]['line']['color']='rgb(115, 115, 115)'
    #fig['data'][0]['line']['width']=3

    return fig