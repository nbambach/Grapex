import pandas as pd
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html

server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_css,server=server)
app.config.suppress_callback_exceptions = True

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
"https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
"https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]