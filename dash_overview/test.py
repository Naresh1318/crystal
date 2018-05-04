import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime


df = pd.read_csv("../test.csv")
time_now = datetime.datetime.now()


def get_next(df, idx):
    return np.array(df.iloc[idx].data)[1:]


app = dash.Dash(__name__)

app.head = [
html.Link(
href='https://codepen.io/chriddyp/pen/bWLwgP.css',
rel='stylesheet'
)
]

app.footer = [
    html.Script(type='text/javascript', children='alert("hello world")')
]

app.layout = html.Div([
    html.H4('Live data feed'),
    html.Div(id='live-update-text'),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    )
])


@app.callback(dash.dependencies.Output('live-update-text', 'children'),
              [dash.dependencies.Input('interval-component', 'n_intervals')])
def update_metrics(n):
    x, y = get_next(df, n)
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('x: {}'.format(x), style=style),
        html.Span('y: {}'.format(y), style=style)
    ]


@app.callback(dash.dependencies.Output('live-update-graph', 'figure'),
              [dash.dependencies.Input('interval-component', 'n_intervals')])
def update_live_graph(n):

    time = []
    time.append(datetime.datetime.now().isoformat(' '))

    fig = {
        'data': [{'x': df['x'][:n], 'y': df['y'][:n], 'type': 'line', 'name': 'Live plot', 'line': {'shape': 'spline', 'smoothing': 1.3, 'color': 'rgb(244,66,104)'}}],
    }

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)



