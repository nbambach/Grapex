import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from sites import rip720
from sites import rip760

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
"https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
"https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]
app = dash.Dash(__name__, external_stylesheets=external_css)
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    html.Div([
        html.H1("GrAPPex Tools",
                style={'display': 'inline',
                        'float': 'left',
                       'font-size': '2.65 em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0',
                       }),
        html.Img(src="https://www.ars.usda.gov/ARSUserFiles/80420510/GRAPEX/grapex_logo_web.png",
            style={
                'height': '100px',
                'float': 'right'}),
    ], className='banner'),
    html.Div([
        html.Div([
            html.H3("")
        ],style={'padding': '10px 10px 70px 10px'},
            className='Title'),
        html.Div([
            dcc.Tabs(id="tabs_site", value='RIPPERDAN', children=[
                dcc.Tab(label='RIP720', value='rip720'),
                dcc.Tab(label='RIP760', value='rip760'),
                dcc.Tab(label='BAR', value='bar'),
                dcc.Tab(label='SLM', value='slm'),
                dcc.Tab(label='FLUX', value='flux')
            ]),
            html.Div(id='tool_type')
        ])
])
])

@app.callback(Output('tool_type', 'children'),
              [Input('tabs_site', 'value')])

def render_content(tab):
    if tab == 'rip720':
        return rip720.rip720_layout
    elif tab == 'rip760':
        return rip760.rip760_layout
 
 if __name__ == "__main__":
    app.run_server(debug=True)
