import dash
import requests
import dash_core_components as dcc
import dash_html_components as html
import colorlover as cl
import datetime as dt
import numpy as np
import flask
import os
import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
import time
from IPython import display

filelink=['https://www.dropbox.com/s/01hb6av413b9qz0/BAR_007_Flux_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/cwodpmojs6ttyrr/Barrelli_Flux_2019.xlsx?dl=1']

filesoil=['https://www.dropbox.com/s/vu7y7hmo83rme7c/BAR_007_Soils_2019.xlsx?dl=1',
         'https://www.dropbox.com/s/bs6qgg5ni4lxe7h/Barrelli_Soils_2019.xlsx?dl=1']

filerad=['https://www.dropbox.com/s/t9s1pm6qj3b6le8/BAR_007_Soils_Net_2019.xlsx?dl=1',
        'https://www.dropbox.com/s/8h2nvrm6ks5c4af/Barrelli_Soils_Net_2019.xlsx?dl=1']

filesoil_2 = ['https://www.dropbox.com/s/z5dm4h8a8k3xw3d/BARRProfile%231_All_2019.xlsx?dl=1',
             'https://www.dropbox.com/s/b2be45102b7ypx4/BARRProfile%232_All_2019.xlsx?dl=1']

file_CIMIS = 'ftp://ftpcimis.water.ca.gov/pub2/dailyMetric/DayYrETo103.csv'
data_CIMIS = pd.read_csv(file_CIMIS,header=None)
data_CIMIS = data_CIMIS.iloc[:,[1,3]]
data_CIMIS.columns=['DATE','ETr']
data_CIMIS['DATE']=pd.to_datetime(data_CIMIS['DATE'],format='%m/%d/%Y')
data_CIMIS['DATE']=data_CIMIS['DATE'].dt.date

block = ['BAR_A07','BAR_A12']
nd=40
for x in range(0,2):
        df=pd.read_excel(filelink[x],skiprows=5,header=None,index_col=False)
        df=df.iloc[:,[0,2,29,30,58,60,61]]
        df.columns=['TIMESTAMP','SITE','LE','H','TA','e','esat']
        df.TIMESTAMP=pd.to_datetime(df['TIMESTAMP'], format= '%Y-%m-%d %H:%M:%S')
        df['DATE']=df['TIMESTAMP'].dt.date
        df['TIME']=df['TIMESTAMP'].dt.time
        df['Bowen_ratio'] = df['H']/df['LE']
        df['Bowen_ratio'] = np.where(df['Bowen_ratio'] > 5, -999, df['Bowen_ratio'])
        df['Bowen_ratio'] = np.where(df['Bowen_ratio'] < -1, 'NaN', df['Bowen_ratio'])

        df_day=df.groupby(['DATE','SITE'],as_index=False).agg({'LE':'sum'})
        df_day=df_day[df_day['LE']>0]
        df_day['ET']= df_day['LE']*(30*60/2500000)
        df_day['ETcum'] = np.cumsum(df_day['ET'])
        end=len(df_day)
        df_day=df_day[end-nd:end]
        
        globals()['trace%s' % x] = go.Bar(
            x=df_day['DATE'],
            y=df_day['ET'],
            name=block[x])
        globals()['trace_ETcum%s' % x] = go.Scatter(
            x=df_day['DATE'],
            y=df_day['ETcum'],
            name=block[x])

        globals()['trace_Bo%s' % x] = go.Scatter(
            x=df['TIMESTAMP'],
            y=df['Bowen_ratio'],
            name=block[x])
 
        
        #### Eta/Eto
        
        dETa = df_day.iloc[:,[0,3]]
        dET = pd.merge(data_CIMIS,dETa,left_on='DATE',right_on='DATE')
        dET['ratio']= dET['ET']/dET['ETr']
        
        globals()['ETratio%s' % x] = go.Scatter(
            x=dET['DATE'],
            y=dET['ratio'],
            name=block[x])
        
        globals()['df%s' % x] = df
                                                    
data=[trace0, trace1]
data_ETcum=[trace_ETcum0,trace_ETcum1]
trace_ET=[ETratio0, ETratio1]
trace_Bo = [trace_Bo0,trace_Bo1]

df_all=df0.append([df1])
df_all['VPD']=df_all['esat']-df_all['e']

df_all = df_all.groupby([df_all['TIMESTAMP']]).mean()

data_met1= go.Scatter(
  x = df_all.index,
  y = df_all['TA'],
  name = 'Tair'
  )

data_met2= go.Scatter(
  x = df_all.index,
  y = df_all['VPD'],
  name = 'VPD',
  yaxis='y2'
)

data_met = [data_met1,data_met2]

df_rad07=pd.read_excel(filerad[0],skiprows=5,header=None,index_col=False)
df_rad07=df_rad07.iloc[:,[0,2,3,4,5,6]]
df_rad07.columns=['TIMESTAMP','SITE','SWin','SWout','LWin','LWout']
df_rad07['Rnet']= df_rad07['SWin']+df_rad07['LWin']-df_rad07['SWout']-df_rad07['LWout']

df_rad12=pd.read_excel(filelink[1],skiprows=5,header=None,index_col=False)
df_rad12=df_rad12.iloc[:,[0,2,70]]
df_rad12.columns=['TIMESTAMP','SITE','Rnet']

df_rad = [df_rad07,df_rad12]

for x in range(0,2):
        df_netrad=df_rad[x]
        
        globals()['trace_NetRad%s' % x] = go.Scatter(
            x=df_netrad['TIMESTAMP'],
            y=df_netrad['Rnet'],
            name=block[x])

trace_NetRad = [trace_NetRad0,trace_NetRad1]  

for x in range(0,2):
        df_soil=pd.read_excel(filesoil[x],skiprows=5,header=None,index_col=False)
        df_soil=df_soil.iloc[:,[0,2,19,21,23,25,27]]
        df_soil.columns=['TIMESTAMP','SITE','SW1','SW2','SW3','SW4','SW5']
        SWC= np.array([df_soil['SW1'],df_soil['SW2'],df_soil['SW3'],df_soil['SW4'],df_soil['SW5']])
        df_soil['SWC']=np.nanmean(SWC,axis=0)

        globals()['trace_SWC%s' % x] = go.Scatter(
            x=df_soil['TIMESTAMP'],
            y=df_soil['SWC'],
            name=block[x])

trace_SWC = [trace_SWC0,trace_SWC1]  

layout0 = go.Layout(
    xaxis=dict(
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        ),
        rangeselector=dict(
            buttons=list([
                dict(count=7,
                     label='  1 week  ',
                     step='day',
                     stepmode='backward'),
                dict(count=10,
                     label='  10 days  ',
                     step='day',
                     stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(
            visible = True
        ),
        type='date'
    ),
    yaxis=dict(
        titlefont=dict(
            size=16,
            color='rgb(107, 107, 107)'
        ),
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        )
    ),
    legend=dict(
        x=0.4,
        y=-0.25,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)',
        orientation="h"
    ),
    barmode='group',
    bargap=0.15,
    bargroupgap=0.1,
)

layout = go.Layout(
    xaxis=dict(
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        ),
        rangeselector=dict(
            buttons=list([
                dict(count=7,
                     label='  1 week  ',
                     step='day',
                     stepmode='backward'),
                dict(count=10,
                     label='  10 days  ',
                     step='day',
                     stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(
            visible = True
        ),
        type='date'
    ),
    yaxis=dict(
        title='Soil Water Content (%)',
        titlefont=dict(
            size=16,
            color='rgb(107, 107, 107)'
        ),
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        )
    ),
    legend=dict(
        x=0.4,
        y=-0.25,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)',
        orientation="h"
    )
)

layout2 = go.Layout(
   xaxis=dict(
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        ),
        rangeselector=dict(
            buttons=list([
                dict(count=7,
                     label='  1 week  ',
                     step='day',
                     stepmode='backward'),
                dict(count=10,
                     label='  10 days  ',
                     step='day',
                     stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(
            visible = True
        ),
        type='date'
    ),
    yaxis=dict(
        title='Celsius',
        titlefont=dict(
            size=16,
            color='rgb(107, 107, 107)'
        ),
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        )
    ),
    yaxis2=dict(
        title='kPa',
        titlefont=dict(
            size=16,
            color='rgb(107, 107, 107)'
        ),
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        ),
        overlaying='y',
        side='right'
    ),
    legend=dict(
        x=0.4,
        y=-0.25,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)',
        orientation="h"
    )
)

bar_layout = html.Div([
    html.Div([
        html.H2("Barrelli | ET Tool",
                style={'display': 'inline',
                        'float': 'left',
                       'font-size': '2.0 em',
                       'margin-left': '8px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0',
                       }),
            ], className='banner'),
    html.Div([
        html.Div([
            html.H3("")
        ],style={'padding': '10px 10px 70px 10px'},
            className='Title'),
        html.Div([
            html.H3("Evapotranspiration (mm/day)")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='ET',
                figure={
                    'data': data,
                    'layout':layout0}),
        ]),
        

          html.Div([
             html.H3("Cumulative Evapotranspiration (mm)")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='ETcum',
                figure={
                    'data': data_ETcum,
                    'layout':layout0}),
        ]),
        
         html.Div([
            html.H3("ETa/ETr")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='ETratio',
                figure={
                    'data': trace_ET,
                    'layout':layout0}),
        ]),
        
        html.Div([
            html.H3("Bowen Ratio")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='Boratio',
                figure={
                    'data': trace_Bo,
                    'layout':layout0}),
        ]),
            
         html.Div([
            html.H3("Soil Water Content | Near Surface")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='SWC',
                figure={
                    'data': trace_SWC,
                    'layout':layout}),
        ]),
        
        
        html.Div([
            html.H3("Air Temperature and Vapor Pressure Deficit")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='Tmet',
                figure={
                    'data': data_met,
                    'layout':layout2}),
        ]),
        
         html.Div([
            html.H3("Net Radiation")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='NetRad',
                figure={
                    'data': trace_NetRad,
                    'layout':layout0}),
        ]),
               
]),            
], style={'padding': '10px 10px 25px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "900px",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'}
)