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

filelink=['https://www.dropbox.com/s/fz4ujac2k9s3gbw/NewRipp%231_Flux_CSIFormat_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/0o2pjzwfs8kaajv/NewRipp%232_Flux_CSIFormat_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/cbmhnwjfsmasbop/NewRipp%233_Flux_CSIFormat_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/jeb9ymj2kjqb4vo/NewRipp%234_Flux_CSIFormat_2019.xlsx?dl=1']

filesoil=['https://www.dropbox.com/s/s7hc7e0l51ukql7/RippSoils_1_VWC_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/vg4vwd36ulw0zzz/RippSoils_2_VWC_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/pfzhkqy6zurpupb/RippSoils_3_VWC_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/s2hv6kowh1mrkj8/RippSoils_4_VWC_2019.xlsx?dl=1']

filesoil_2 = ['https://www.dropbox.com/s/us71o3gea0hq9ne/RippSoils_1A_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/fbhy7ovycpdxegc/RippSoils_1B_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/9xurpd0apxuyxcb/RippSoils_1C_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/x7doez7600lzlus/RippSoils_2A_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/7rlhsi7xkcbmd89/RippSoils_2B_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/d9qfbo7s4yl9d4c/RippSoils_2C_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/a0gd3zc09hqzphq/RippSoils_3A_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/tz7kvuisdyldmsa/RippSoils_3B_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/eu1tmxdon9bpkol/RippSoils_3C_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/rpbqhkw72sskvjz/RippSoils_4A_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/turyxl114sb6kkw/RippSoils_4B_VWCTemp_2019.xlsx?dl=1',
          'https://www.dropbox.com/s/dxu353ys7xj3urw/RippSoils_4C_VWCTemp_2019.xlsx?dl=1']

file_CIMIS = 'ftp://ftpcimis.water.ca.gov/pub2/dailyMetric/DayYrETo007.csv'
data_CIMIS = pd.read_csv(file_CIMIS,header=None)
data_CIMIS = data_CIMIS.iloc[:,[1,3]]
data_CIMIS.columns=['DATE','ETr']
data_CIMIS['DATE']=pd.to_datetime(data_CIMIS['DATE'],format='%m/%d/%Y')
data_CIMIS['DATE']=data_CIMIS['DATE'].dt.date

nd=40
for x in range(0,4):
        df=pd.read_excel(filelink[x],skiprows=7,header=None,index_col=False)
        df=df.iloc[:,[0,2,7,13,26,32,35,36,95,96,97,98,99]]
        df.columns=['TIMESTAMP','SITE','LE','Net Radiation','Bowen_ratio','TA','e','esat','SW1','SW2','SW3','SW4','SW5']
        df.TIMESTAMP=pd.to_datetime(df['TIMESTAMP'], format= '%Y-%m-%d %H:%M:%S')
        df['DATE']=df['TIMESTAMP'].dt.date
        df['TIME']=df['TIMESTAMP'].dt.time
        df['Bowen_ratio'] = np.where(df['Bowen_ratio'] > 5, -999, df['Bowen_ratio'])
        df['Bowen_ratio'] = np.where(df['Bowen_ratio'] < -1, 'NaN', df['Bowen_ratio'])
        SW=np.array([df['SW1'],df['SW2'],df['SW3'],df['SW4'],df['SW5']])
        df['SoilWater']=np.mean(SW,axis=0)
        df_day=df[df['Net Radiation']>0]
        df_day=df.groupby(['DATE','SITE'],as_index=False).agg({'LE':'sum','Net Radiation':'mean',
                                                               'SoilWater':'mean'})
        df_day=df_day[df_day['LE']>0]
        df_day['ET']= df_day['LE']*(30*60/2500000)
        df_day['ETcum'] = np.cumsum(df_day['ET'])
        end=len(df_day)
        df_day=df_day[end-nd:end]
        
        globals()['trace%s' % x] = go.Bar(
            x=df_day['DATE'],
            y=df_day['ET'],
            name=x+1)
        globals()['trace_ETcum%s' % x] = go.Scatter(
            x=df_day['DATE'],
            y=df_day['ETcum'],
            name=x+1)
        globals()['trace_SW%s' % x] = go.Scatter(
            x=df['TIMESTAMP'],
            y=df['SoilWater'],
            name=x+1)
        globals()['trace_Bo%s' % x] = go.Scatter(
            x=df['TIMESTAMP'],
            y=df['Bowen_ratio'],
            name=x+1)
        globals()['trace_NetRad%s' % x] = go.Scatter(
            x=df['TIMESTAMP'],
            y=df['Net Radiation'],
            name=x+1)
        
        #### Eta/Eto
        
        dETa = df_day.iloc[:,[0,5]]
        dET = pd.merge(data_CIMIS,dETa,left_on='DATE',right_on='DATE')
        dET['ratio']= dET['ET']/dET['ETr']
        
        globals()['ETratio%s' % x] = go.Scatter(
            x=dET['DATE'],
            y=dET['ratio'],
            name=x+1)
        
        globals()['df%s' % x] = df
                                                    
data=[trace0, trace1, trace2, trace3]
data_ETcum=[trace_ETcum0,trace_ETcum1,trace_ETcum2,trace_ETcum3]
data_SW=[trace_SW0, trace_SW1, trace_SW2, trace_SW3]
trace_ET=[ETratio0, ETratio1, ETratio2, ETratio3]
trace_Bo = [trace_Bo0,trace_Bo1,trace_Bo2,trace_Bo3]
trace_NetRad = [trace_NetRad0,trace_NetRad1,trace_NetRad2,trace_NetRad3]

df_all=df0.append([df1,df2,df3])
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

for x in range(0,4):
        for y in range (0,3):
            dff2=pd.read_excel(filesoil_2[y],skiprows=7,header=None,index_col=False)
            dff2=dff2.iloc[:,[0,2,5,6,7,8]]
            dff2.columns=['TIMESTAMP','SITE','VWC_1','VWC_2','VWC_3','VWC_4']
            dff2.TIMESTAMP=pd.to_datetime(dff2['TIMESTAMP'], format= '%Y-%m-%d %H:%M:%S')
            globals()['data%s' % y] = dff2
        
        dff2s = [data.set_index(['TIMESTAMP']) for data in [data0, data1, data2]]
        dt = pd.concat(dff2s, axis=1).reset_index()
        dt=dt.iloc[:,[0,1,2,3,4,5,7,8,9,10,12,13,14,15]]
        dt.columns=['TIMESTAMP','SITE','SWC60A','SWC90A','SWC61A','SWC91A','SWC60B','SWC90B','SWC61B','SWC91B','SWC60C','SWC90C','SWC61C','SWC91C']

        SWCC_60= np.array([dt['SWC60A'],dt['SWC61A'],dt['SWC60B'],dt['SWC61B'],dt['SWC60C'],dt['SWC61C']])
        SWCC_90= np.array([dt['SWC90A'],dt['SWC91A'],dt['SWC90B'],dt['SWC91B'],dt['SWC90C'],dt['SWC91C']])                 
      
        dt['SWCC_60']=np.nanmean(SWCC_60,axis=0)
        dt['SWCC_90']=np.nanmean(SWCC_90,axis=0)
        dt=dt.iloc[:,[0,14,15]]
    
### NOTE ON SOIL ARRAY
# 60cm - 1/3
# 90cm - 2/4 
    
        dff=pd.read_excel(filesoil[x],skiprows=7,header=None,index_col=False)
        dff=dff.iloc[:,[0,2,5,6,7,8,9,10,11,12,13,14,15,16]]
        dff.columns=['TIMESTAMP','SITE','VWC_1','VWC_2','VWC_3','VWC_4','VWC_5','VWC_6','VWC_7','VWC_8','VWC_9','VWC_10','VWC_11','VWC_12']
        dff.TIMESTAMP=pd.to_datetime(dff['TIMESTAMP'], format= '%Y-%m-%d %H:%M:%S')
        dff['DATE']=dff['TIMESTAMP'].dt.date
        dff['TIME']=dff['TIMESTAMP'].dt.time 
        
        ### NOTE ON SOIL ARRAY
# 30 cm - 4/7
# 60cm - 1/2/5/8/10/12
# 90cm - 3/6/9/11

        SW_30=np.array([dff['VWC_4'],dff['VWC_7']])
        SW_60=np.array([dff['VWC_1'],dff['VWC_2'],dff['VWC_5'],dff['VWC_8'],dff['VWC_10'],dff['VWC_12']])
        SW_90=np.array([dff['VWC_3'],dff['VWC_6'],dff['VWC_9'],dff['VWC_11']])

        dff['VWC_30']=np.nanmean(SW_30*100,axis=0)
        dff['VWC_60']=np.nanmean(SW_60*100,axis=0)
        dff['VWC_90']=np.nanmean(SW_90*100,axis=0)      
        dff=dff.iloc[:,[0,1,14,15,16,17,18]]
    
        dfinal = pd.concat([dff,dt],sort=False)
        SW_60=np.array([dfinal['VWC_60'],dfinal['SWCC_60']])
        SW_90=np.array([dfinal['VWC_90'],dfinal['SWCC_90']])
        dfinal['VWC_60']= np.nanmean(SW_60,axis=0)
        dfinal['VWC_90']= np.nanmean(SW_90,axis=0)
        dfinal =dfinal.iloc[:,0:7]
        
        globals()['VWC_30%s' % x] = go.Scatter(
            x=dfinal['TIMESTAMP'],
            y=dfinal['VWC_30'],
            name=x+1)

        globals()['VWC_60%s' % x] = go.Scatter(
            x=dfinal['DATE'],
            y=dfinal['VWC_60'],
            name=x+1)

        globals()['VWC_90%s' % x] = go.Scatter(
            x=dfinal['DATE'],
            y=dfinal['VWC_90'],
            name=x+1)

data_all_SW30 = [VWC_300,VWC_301,VWC_302,VWC_303]
data_all_SW60 = [VWC_600,VWC_601,VWC_602,VWC_603]
data_all_SW90 = [VWC_900,VWC_901,VWC_902,VWC_903]

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

rip720_layout = html.Div([
    html.Div([
        html.H2("Ripperdan 720 | ET Tool",
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
                    'data': data_SW,
                    'layout':layout}),
        ]),
        
        
         html.Div([
             html.H3("Soil Water Content | 30 cm Depth ")
         ],
             className='Title'),
         html.Div([
             dcc.Graph(
                 id='SWC 30 all',
                 figure={
                     'data': data_all_SW30,
                     'layout':layout}),
         ]),
        
        html.Div([
            html.H3("Soil Water Content | 60 cm Depth ")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='SWC 60',
                figure={
                    'data': data_all_SW60,
                    'layout':layout}),
        ]),
        
        html.Div([
            html.H3("Soil Water Content | 90 cm Depth ")
        ],
            className='Title'),
        html.Div([
            dcc.Graph(
                id='SWC 90',
                figure={
                    'data': data_all_SW90,
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
        
        html.Div([
            html.H3("ET Alexi")
        ],
            className='Title'),
        html.Img(src="https://www.ars.usda.gov/ARSUserFiles/80420510/GRAPEX/imagery_multiscale.png?width=700&height=307"),
    ]),            
], style={'padding': '10px 10px 25px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "900px",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'}
)