import dash
import dash_core_components as dcc
import dash_html_components as html


app = dash.Dash()

app.layout = html.Div([
    dcc.RadioItems(
        id='dropdown-a',
        options=[{'label': i, 'value': i} for i in ['Canada', 'USA', 'Mexico']],
        value='Canada'
    ),
    html.Div(id='Output-a')

])


