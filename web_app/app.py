import dash
import dash_bootstrap_components as dbc
from dash import html as html
from dash import dcc as dcc
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
import json
import numpy as np
import colour
import RGB

import plotly.graph_objects as go
from plotly.subplots import make_subplots

################################ DATA IMPORTING ####################################
################################ IMPORT CSV FOR LIGHTING AND CREATE PANDAS DATAFRAME
df = pd.read_csv("Bedroom291121.csv")
df = df[df["field1"]<6500]
df['created_at'] = df['created_at'].str.replace('T','')
df['created_at'] = df['created_at'].str.replace(':','')
df["created_at"] = pd.to_datetime(df["created_at"], format="%Y-%m-%d%H%M%S%z")
df = df.drop(['latitude','longitude','elevation','status'],axis=1)
df = df.rename(columns={"created_at": "Time","field1": "Bedroom Colour Temperature (K)","field2":"Calculated Outdoor Colour Temperature (K)","field3": "Indoor Light Level (lux)", "field4": "Indoor Temperature (°C)","field5":"Indoor Humidity (%)"})


################################ IMPORT CSV FOR FITBIT AND CREATE PANDAS DATAFRAME
df2 = pd.read_csv("Fitbit291121.csv")
df2['created_at'] = df2['created_at'].str.replace('T','')
df2['created_at'] = df2['created_at'].str.replace(':','')
df2["created_at"] = pd.to_datetime(df2["created_at"], format="%Y-%m-%d%H%M%S%z")
df2 = df2.drop(['latitude','longitude','elevation','status'],axis=1)
df2 = df2.rename(columns={"created_at": "Time","field1": "Sleep State"})
df2=df2.sort_values(by="Time")

################################ COMBINE FITBIT AND BEDROOM DATAFRAMES
# Merge_asof method combines nearest Time values from each dataframe to create single dataframe.
# This is suitable as the exact timing of sleep state change is not required (i.e. can change by 30 seconds)
# A unified dataset is more important for using later on in the scatterplot matrix where datasets should match
df_combined=pd.merge_asof(df, df2, left_on="Time", right_on="Time")
# Any empty fields for sleep state should be filled with 3 to indicate awake (as Fitbit will not constantly collect if you are awake during the day).
df_combined["Sleep State"] = df_combined["Sleep State"].fillna(3)

#df_combined=pd.merge(df, df2, on="Time")
#df_combined=pd.merge_ordered(df, df2, left_on="Time", right_on="Time")

#pd.set_option("display.max_rows", None, "display.max_columns", None,'display.width', 120)
#print(df_combined)
#df_combined.to_csv('test2.csv')

################################ IMPORT CSV FOR EMOTION WORK SESSION AND CREATE PANDAS DATAFRAME
df_emotion = pd.read_csv("2021-12-18_16-52-32emotion.csv")
df_emotion['TIME'] = pd.to_datetime(df_emotion['TIME'], format="%Y-%m-%d %H:%M:%S.%f%z")
#df_emotion = df_emotion.rename(columns={"TIME": "Time"})
df_emotion=df_emotion.sort_values(by="TIME")
#df_emotion['Angry'] = df_emotion['Angry'].rolling(7).sum()
#print(df_emotion)

################################ DASH APP SETUP ####################################
################################ CREATE DASH APP INSTANCE
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], 
                meta_tags=[{'name':'viewport','content':'width-device-width, initial-scale=1.0'}],
                suppress_callback_exceptions=True)

server = app.server

# Webpage overall name                
app.title = "Bedroom Lighting of the Future"
# Overall content styling
CONTENT_STYLE = {
    'margin-top':"2rem",
}

################################ NAVIGATION AND MENUBAR LAYOUT COMMON ACROSS ALL PAGES
menubar = html.Div(
    [
        html.H1("BEDROOM LIGHTING OF THE FUTURE", className="header-title"),
        html.Hr(),
        html.P(
        "Welcome to my Sensing and IoT Project! It explores bedroom lighting of the future, consisting of health-based lighting and emotional lighting. Health-based lighting is related to circadian rhythms, looking at how the natural colour temperature of the Sun compares to that of my bedroom, and how that impacts my sleep. Emotional-based lighting tracks my facial expressions with a webcam and changes the colour of the lighting in my room to reflect this, (i.e. If I'm sad, the lights go blue). You are currently on the Web App element of my project, built with Dash in Python, which focuses on data analysis and novel interaction. All physical actuations are detailed in the SIoT report.",
        className="header-description"
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("CIRCADIAN RHYTHM", href="/", active="exact"), #active makes it look highlighted, Nav bar from bootstrap
                dbc.NavLink("BEDROOM SENSORS", href="/page-1", active="exact"),
                dbc.NavLink("EMOTIONAL LIGHTING", href="/page-2", active="exact"),
                dbc.NavLink("LIVE DATA", href="/page-3", active="exact"),
            ],
            #vertical=True,
            pills=True,
            fill=True,
            justified=True,
        ),
        html.Hr()
    ],
)
################################ CONTENT OF MAIN PAGE SETUP FOR CALLBACK USING ID (FOR NAVIGATION)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE) # just creating, nothing in it yet

################################ OVERALL APP WITH MENUBAR AND PAGE CONTENT BASED ON URL
app.layout = html.Div([
    dcc.Location(id="url"),
    menubar,
    content
])

################################ GRAPHS SETUP ####################################
################################ GRAPH 1 SETUP FOR BEDROOM AND OUTDOOR COLOUR TEMPERATURE
fig1=px.line(df, x='Time', y=['Bedroom Colour Temperature (K)','Calculated Outdoor Colour Temperature (K)'])
fig1.update_traces(mode="markers+lines", hovertemplate=None)
fig1.update_layout(
    # title={
    #     'text': "Room Light Colour Temperature versus Time",
    #     'y':1,
    #     'x':0.5,
    #     'xanchor': 'center',
    #     'yanchor': 'top'},
    xaxis_title="Time",
    yaxis_title="Colour Temperature (K)",
    legend_title="Toggle Visibility",
    font=dict(
        family="Courier New, monospace",
        size=15,
        color="White"
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=2,
        xanchor="right",
        x=1
    ),
    hovermode="x unified",
    xaxis=dict(
        rangeslider=dict(
            visible=True,
        ),
        #type="date",
    )
)
fig1.layout.template = 'plotly_dark'
################################ FITBIT GRAPH TO COMBINE FOR CIRCADIAN RHYTHM PAGE
fig_sleep = px.line(df2, x='Time', y=['Sleep State'])
fig_sleep.update_traces(mode="markers+lines", line_shape="hv",yaxis="y2")
fig_sleep.layout.template = 'plotly_dark'
################################ COMBINED FINAL SUBPLOT OF FITBIT + INDOOR/OUTDOOR LIGHTING
subfig = make_subplots(specs=[[{"secondary_y": True}]])
subfig.add_traces(fig1.data + fig_sleep.data)
subfig.layout.xaxis.title="Time"
subfig.layout.yaxis.title="Colour Temperature (K)"
subfig.layout.yaxis2.title="Sleep State"

subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

subfig.update_traces(mode="lines", hovertemplate=None)
subfig.update_layout(
    legend_title="Toggle Visibility",
    font=dict(
        family="Courier New, monospace",
        size=15,
        color="White"
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=2,
        xanchor="right",
        x=1
    ),
    hovermode="x unified",
    xaxis=dict(
        rangeslider=dict(
            visible=True)
        ),
    yaxis2=dict(
        ticktext=["Awake", "REM Sleep", "Light Sleep", "Deep Sleep"],
        tickvals=[3, 2, 1, 0],
        tickmode="array",
    )
    )
subfig.layout.template = 'plotly_dark'
################################ OUTDOOR COLOUR TEMPERATURE GRAPH ONLY
fig_outdoor_col_temp=px.line(df, x='Time', y=['Calculated Outdoor Colour Temperature (K)'])
fig_outdoor_col_temp.update_traces(mode="lines", hovertemplate=None, line_color = "#f65f5f")
fig_outdoor_col_temp.update_layout(
    xaxis_title="Time",
    yaxis_title="Calculated Outdoor<br>Colour Temperature (K)",
    showlegend = False,
    font=dict(
        family="Courier New, monospace",
        size=15,
        color="White"
    ),
    hovermode="x unified",
)
fig_outdoor_col_temp.layout.template = 'plotly_dark'
################################ INDOOR TEMPERATURE IN DEGREES GRAPH ONLY
fig_indoor_temp=px.line(df, x='Time', y=['Indoor Temperature (°C)'])
fig_indoor_temp.update_traces(mode="lines", hovertemplate=None,  line_color = "#ffab0c")
fig_indoor_temp.update_layout(
    xaxis_title="Time",
    yaxis_title="Indoor Temperature (°C)",
    showlegend = False,
    font=dict(
        family="Courier New, monospace",
        size=15,
        color="White"
    ),
    hovermode="x unified",
)
fig_indoor_temp.layout.template = 'plotly_dark'
################################ INDOOR HUMIDITY GRAPH ONLY
fig_humidity=px.line(df, x='Time', y=['Indoor Humidity (%)'])
fig_humidity.update_traces(mode="lines", hovertemplate=None, line_color = "#f9da58")
fig_humidity.update_layout(
    xaxis_title="Time",
    yaxis_title="Indoor Humidity (%)",
    showlegend = False,
    font=dict(
        family="Courier New, monospace",
        size=15,
        color="White"
    ),
    hovermode="x unified",
)
fig_humidity.layout.template = 'plotly_dark'
################################ INDOOR COLOUR TEMPERATURE GRAPH ONLY
fig_indoor_col_temp=px.line(df, x='Time', y=['Bedroom Colour Temperature (K)'])
fig_indoor_col_temp.update_traces(mode="lines", hovertemplate=None, line_color = "#d4d4d4")
fig_indoor_col_temp.update_layout(
    xaxis_title="Time",
    yaxis_title="Bedroom Colour Temperature (K)",
    showlegend = False,
    font=dict(
        family="Courier New, monospace",
        size=15,
        color="White"
    ),
    hovermode="x unified",
)
fig_indoor_col_temp.layout.template = 'plotly_dark'
################################ OUTDOOR LIGHT LEVEL GRAPH ONLY
fig_lux=px.line(df, x='Time', y=['Indoor Light Level (lux)'])
fig_lux.update_traces(mode="lines", hovertemplate=None, line_color = "#056eff")
fig_lux.update_layout(
    xaxis_title="Time",
    yaxis_title="Indoor Light Level (lux)",
    showlegend = False,
    font=dict(
        family="Courier New, monospace",
        size=15,
        color="White"
    ),
    hovermode="x unified",
)
fig_lux.layout.template = 'plotly_dark'
################################ FITBIT SLEEP STATE GRAPH ONLY
fig_sleep_2=px.line(df2, x='Time', y=['Sleep State'])
fig_sleep_2.update_traces(mode="markers + lines", line_shape="hv", hovertemplate=None, line_color = "#56d0ae")
fig_sleep_2.update_layout(
    xaxis_title="Time",
    yaxis_title="Sleep State",
    showlegend = False,
    font=dict(
        family="Courier New, monospace",
        size=15,
        color="White",
    ),
    hovermode="x unified",
)
fig_sleep_2.update_yaxes(ticktext=["Awake", "REM Sleep", "Light Sleep", "Deep Sleep"],
        tickvals=[3, 2, 1, 0],
        tickmode="array")
fig_sleep_2.layout.template = 'plotly_dark'

################################ SCATTERPLOT MATRIX GRAPH USING COMBINED UNIFIED DATASET
df_combined = df_combined.rename(columns={"Bedroom Colour Temperature (K)" : "Bedroom Colour<br>Temperature (K)","Calculated Outdoor Colour Temperature (K)" : "Calculated Outdoor<br>Colour Temperature (K)" ,"Indoor Light Level (lux)": "Indoor Light<br>Level (lux)","Indoor Temperature (°C)" : "Indoor<br>Temperature (°C)", "Indoor Humidity (%)" : "Indoor<br>Humidity (%)","Sleep State" : "Sleep<br>State"})
fig_scatter = px.scatter_matrix(df_combined,
                                dimensions=["Bedroom Colour<br>Temperature (K)", "Calculated Outdoor<br>Colour Temperature (K)", "Indoor Light<br>Level (lux)", "Indoor<br>Temperature (°C)", "Indoor<br>Humidity (%)","Sleep<br>State"],
                                opacity = 0.2,
                                color = 'Sleep<br>State',
                                width = 1100,
                                height = 1100,
                                # color_continuous_scale=[(0.00, "red"),   (0.25, "red"),
                                #                         (0.25, "green"), (0.5, "green"),
                                #                         (0.5, "blue"),  (0.75, "blue"),
                                #                         (0.75,"purple"), (1.00,"purple")]
                                )
# fig_scatter.update_traces(diagonal_visible=False)
fig_scatter.update_layout(
    legend_title="Toggle Visibility",
    font=dict(
        family="Courier New, monospace",
        size=9.5,
        color="White"
    ),
    yaxis6=dict(
        ticktext=["Awake", "REM Sleep", "Light Sleep", "Deep Sleep"],
        tickvals=[3, 2, 1, 0],
        tickmode="array",
    ),
    xaxis6=dict(
        ticktext=["Awake", "REM Sleep", "Light Sleep", "Deep Sleep"],
        tickvals=[3, 2, 1, 0],
        tickmode="array",
    ),
    coloraxis_colorbar=dict(
        #title="Sleep State",
        title={'side': "right"},
        ticktext=["Awake", "REM Sleep", "Light Sleep", "Deep Sleep"],
        tickvals=[3, 2, 1, 0],
        tickmode="array",
    ))
fig_scatter.layout.template = 'plotly_dark'

################################ PEARSON COEEFFICENT PLOT
df_combined_correlated = df_combined
df_combined_correlated = df_combined_correlated.drop(['entry_id_x','entry_id_y'],axis=1)
df_combined_correlated_output = df_combined_correlated.corr(method="pearson")
#print(df_combined_correlated_output)
fig_corr = px.imshow(df_combined_correlated_output, 
                    color_continuous_scale=px.colors.sequential.RdBu, 
                    zmin=-1,
                    width = 1100,
                    height = 1100)
fig_corr.update_layout(
    legend_title="Toggle Visibility",
    font=dict(
        family="Courier New, monospace",
        size=12,
        color="White"
    ),
    coloraxis_colorbar=dict(
        title="Correlation<br>Coefficent", 
        titleside = "right"
    )
)
fig_corr.layout.template = 'plotly_dark'

################################ CALLBACK FUNCTIONS FOR MAKING GRAPHS INTERACTIVE ####################################
################################ COLOUR TEMPERATURE VISUAL SQUARE ON HOVER CALLBACK
@app.callback(
    Output('hover-data','children'),
    [Input('graph1','hoverData')]
)
def disp_hover_data(hover_data):
    if json.dumps(hover_data) == 'null':
        indoor_colour=0
        outdoor_colour=0
        #sleep_state=0
    else:
        max_items = len(hover_data["points"])
        if max_items <= 2:
            indoor_colour = json.dumps(hover_data['points'][1]["y"], indent=2)
            outdoor_colour = json.dumps(hover_data['points'][0]["y"], indent=2)
        else:
            indoor_colour = json.dumps(hover_data['points'][1]["y"], indent=2)
            outdoor_colour = json.dumps(hover_data['points'][0]["y"], indent=2)
    
    indoor_colour=float(indoor_colour)
    rgb_indoor=RGB.convert_K_to_RGB(indoor_colour)
    R_indoor=rgb_indoor[0]
    G_indoor=rgb_indoor[1]
    B_indoor=rgb_indoor[2]

    outdoor_colour=float(outdoor_colour)
    rgb_outdoor=RGB.convert_K_to_RGB(outdoor_colour)
    R_outdoor=rgb_outdoor[0]
    G_outdoor=rgb_outdoor[1]
    B_outdoor=rgb_outdoor[2]

    img_rgb = np.array([[[R_indoor, G_indoor, B_indoor]],
                [[R_outdoor, G_outdoor, B_outdoor]]
                ], dtype=np.uint8)

    fig_colour=px.imshow(img_rgb,
                        labels=dict(x="Colour Temperature (K)", y="OUTDOOR      |     INDOOR")
                        )
    fig_colour.update_layout(
        hovermode=False
)
    fig_colour.update_xaxes(showticklabels=False)
    fig_colour.update_yaxes(showticklabels=False)
    fig_colour.layout.template = 'plotly_dark'

    return [
            dcc.Graph(id="graph_colour",figure=fig_colour)
    ]

################################ SLEEP STATE TEXT ON HOVER CALLBACK
@app.callback(
    Output('hover-data-sleep','children'),
    [Input('graph1','hoverData')]
)
def disp_hover_data(hover_data):
    if json.dumps(hover_data) == 'null':
        sleep_state = '4'
    else:
        max_items = len(hover_data["points"])
        if max_items <= 2:
            sleep_state = '4'
        else:
            sleep_state = json.dumps(hover_data['points'][2]["y"], indent=2)

    sleep_dict=({'4':'Hover Over a Sleep State Peak','3':'Awake','2':'REM Sleep','1':'Light Sleep','0':'Deep Sleep'})
    #print(sleep_state)
    sleep_state_text = sleep_dict[sleep_state]
    #print(sleep_state_text)

    return [
            (sleep_state_text)
    ]
################################ EMOTION AVERAGING WINDOW SIZE CALLBACK
@app.callback(
    Output('emotion_graph','figure'),
    [Input('emotion_graph_value','value')]
)
def disp_hover_data(window_size):

    fig_emotion=px.scatter(df_emotion, x='TIME', y=['Sad','Angry','Happy','Surprise','Neutral'],trendline = 'rolling',trendline_options=dict(window=window_size))
    fig_emotion.data = [t for t in fig_emotion.data if t.mode == "lines"]
    fig_emotion.update_traces(showlegend=True, hovertemplate=None)

    fig_emotion.update_layout(
        xaxis_title="Time",
        yaxis_title="Emotion Value (0-1)",
        legend_title="Toggle Visibility",
        font=dict(
            family="Courier New, monospace",
            size=15,
            color="White"
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=2,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
        xaxis=dict(
            rangeslider=dict(
                visible=True,
            ),
        )
    )
    fig_emotion.layout.template = 'plotly_dark'

    return fig_emotion

################################ CALLBACK FUNCTIONS FOR URL NAVIGATION AND PAGE SETUP ####################################
################################ URL NAVIGATION CALLBACK FUNCTION AND PAGES
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [
                html.P(
                        "Humans are best tuned to the natural cycle of the sun, but artifical lighting has negatively affected this. A synchronised Circadian Rhythm is important for a healthy life as it directly impacts our physical and mental wellbeing. Let's compare the colour temperature of the lights in your room to the ideal sun colour temperature based on sun elevation (time of day).",
                        className="paragraph"
                        ),
                html.H2('CIRCADIAN RHYTHM ANALYSIS',
                        className="header-subtitle"),
                html.P(
                        "Hover over the graph to see what the colour temperature inside was compared to outside, and what my state of sleep at that point. Use the slider to focus on a specfic time region.",
                        className="paragraph"
                        ),
                dcc.Graph(id='graph1', figure=subfig),
                html.Div(
                            dbc.Row(
                                [
                                    dbc.Col(children = [
                                        html.H2('Colour Temperature Visual', className="header-subtitle"),
                                        html.Div(id='hover-data')
                                    ]),
                                    dbc.Col(children = [
                                        html.H2('Sleep State', className="header-subtitle"),
                                        html.Div(id='hover-data-sleep', className="sleep-text"),
                                    ])
                                ],
                                align="start",
                            ),
                    ),
                html.Hr()
                ]
    elif pathname == "/page-1":
        return [
                html.P(
                        "The following page shows the raw data captured from my 2 bedroom sensors (BH1745 RGB Luminance Sensor and DHT22 Temperature & Humdity Sensor), Outdoor Colour Temperature converted from a solar elevation API and FitBit - each can be individually explored. Scroll down to the bottom of the page to see how they correlate!",
                        className="paragraph"
                        ),
                html.P(
                        "Scroll down to the bottom of the page to see how they correlate!",
                        className="header-description"
                        ),
            html.Div( children = [
                html.H2('Indoor Room Colour Temperature (K)',
                        className="header-subtitle"),
                dcc.Graph(id='graph2', figure=fig_indoor_col_temp),
                html.H2('Calculated Outdoor Colour Temperature (K)',
                        className="header-subtitle"),
                dcc.Graph(id='graph3', figure=fig_outdoor_col_temp),
                html.H2('Indoor Room Light Levels (lux)',
                        className="header-subtitle"),
                dcc.Graph(id='graph4', figure=fig_lux),
                html.H2('Bedroom Temperature (°C)',
                        className="header-subtitle"),
                dcc.Graph(id='graph5', figure=fig_indoor_temp),
                html.H2('Bedroom Humidity (%)',
                        className="header-subtitle"),
                dcc.Graph(id='graph6', figure=fig_humidity),
                html.H2('Fitbit Sleep State',
                        className="header-subtitle"),
                dcc.Graph(id='graph7', figure=fig_sleep_2),
                html.Hr(),
                html.H2('Scatterplot Matrix Analysis',
                        className="header-subtitle"),
                html.P(
                        "A scatterplot matrix was created to compare each of the measured values, and the Sleep State shown as a colour axis to see how it changes across each comparison. The results are quite interesting. The indoor light level and my sleep state clearly show correlation, where when I am awake, my lights are on, whenever I am asleep, they are off - this makes sense. A similar correlation occurs with my Bedroom Colour Tempeture which is also in line with expectations. The same pattern should be identified with the Outdoor Colour Temperature, to show I am sleeping at night and awake during the day, however the data is far more spread out across each Sleep State, therefore indicating a highly poor Circadian Rhythm.",
                        className="paragraph"
                        ),
                html.P(
                        "Further correlations show that the humidity is usually higher when I am asleep, and the temperature is lower. This is likely down to my lights, PC and monitors being off which generate a lot of heat, and also that it's typically the middle of the night (i.e. 4am).",
                        className="paragraph"
                        ),
                dcc.Graph(id='graph_scatter', figure=fig_scatter,
                        style={
                            "height":1100,
                            "width":1100,
                            "display": "block",
                            "margin-left": "auto",
                            "margin-right": "auto",
                            }),
                html.H2('Pearson Correlation Coefficient Plot',
                        className="header-subtitle"),
                html.P(
                        "A feature correlation plot shows the Pearson correlation coefficients using a colour scale. This provides greater insight than the scatter matrix above, but doesn't allow as much exploration of the data. There positive correlation between the Bedroom Colour Temperature and Indoor Light Level, which makes sense as it shows my lights are on when light colour is detected. My sleep state has a negative correlation of -0.3 with the Outdoot Colour Temperature, which is quite bad given that this should be closer to 1, let alone negative. This indicates to me that just getting the right number of hours of sleep is not enough, but actually doing these at the right time is what I should be focusing on. I am potentially impacting my productivity and alertness with an asynchronous sun to sleep cycle.",
                        className="paragraph"
                        ),
                dcc.Graph(id='graph_corr', figure=fig_corr,
                        style={
                            "height":1100,
                            "width":1100,
                            "display": "block",
                            "margin-left": "auto",
                            "margin-right": "auto",
                            }),

            ]
            )
                ]
    elif pathname == "/page-2":
        return [
            html.Div( children = [
                html.H2('EMOTIONS DURING WORK SESSION',
                        className="header-subtitle"),
                html.P(
                        "My emotions were tracked using an OpenCV Python Script and webcam during a work session. Since emotions change quite suddenly, the data was saved to a local CSV and automatically uploaded to Google Sheets with the gspread API (as ThingSpeak has an upload limit of 1 request/15 seconds). The data was captured frame by frame, but when saved to the CSV, I averaged it to the last 30 readings to reduce the file size. The graph below shows the predictions for each emotional state - hover over to see the prediction values. An existing CNN from online was used to train on a pre-prepared Kaggle face dataset of 27,261 images split into training and validation sets (70/30) with an accuracy of 68% - this was quite good but expressions often had to be overemphasized. I then used the same model (tweaking some parameters), but created my own dataset with my face. It had an accuracy of 55%, but only predicted Neutral and Happy reliably as the dataset was limited to 190 images and biased to these emotions - it could however pickup subtleties in my expression much better. The graph below shows the predictions of the existing maching learning model.",
                        className="paragraph"
                        ),
                html.P(
                    "A slider enables you to change the window size to smooth the data - set it to 1 to see the raw data.",
                        className="header-description"
                        ),
                dcc.Graph(id='emotion_graph'),
                html.P(
                        "Set the window size for the rolling average filter.", 
                        className="header-description"
                        ),
                dcc.Slider(
                    id='emotion_graph_value',
                    min=1,
                    max=2000,
                    step=1,
                    value=500,
                    tooltip={"placement": "bottom", "always_visible": True},
                    marks={
                            1: '1',
                            500: '500',
                            1000: '1000',
                            1500: '1500',
                            2000: '2000'},
                ),

            ]
                )
            ]

    elif pathname == "/page-3":
        return [
                html.P(
                        "Below are live feeds from my 6 different data sources, collected through Python scripts running on my Pi 3, then uploaded to Thingspeak for storage.",
                        className="paragraph"
                        ),
                html.H2('Live Room Sensor Data', 
                        className="header-subtitle"
                        ),
                html.P(
                        "There are 2 sensors (BH1745 RGB Luminance Sensor and DHT22 Temperature & Humdity Sensor) attached to my Raspberry Pi 3, collecting 4 distinct metrics relevant to sleep and lighting.",
                        className="paragraph"
                        ),
                html.Div([
                    html.Iframe(src="https://thingspeak.com/channels/1570388/charts/1?bgcolor=%23000000&color=%23ffffff&dynamic=true&max=6000&results=60&title=Room+Colour+Temperature+versus+Time&type=line"
                    ,style={"width":"460px", "height":"230px", "style":"border: 1px solid #cccccc;"} ),
                    html.Iframe(src="https://thingspeak.com/channels/1570388/charts/3?bgcolor=%23000000&color=%23ffffff&dynamic=true&results=60&title=Indoor+Lux+versus+Time&type=line"
                    ,style={"width":"460px", "height":"230px", "style":"border: 1px solid #cccccc;"} ),
                ], style={'textAlign':'center'}),
                html.Div([
                    html.Iframe(src="https://thingspeak.com/channels/1570388/charts/4?bgcolor=%23000000&color=%23ffffff&dynamic=true&results=60&title=Indoor+Temperature+versus+Time&type=line"
                    ,style={"width":"460px", "height":"230px", "style":"border: 1px solid #cccccc;"} ),
                    html.Iframe(src="https://thingspeak.com/channels/1570388/charts/5?bgcolor=%23000000&color=%23ffffff&dynamic=true&results=60&title=Indoor+Humidity+versus+Time&type=line"
                    ,style={"width":"460px", "height":"230px", "style":"border: 1px solid #cccccc;"} ),
                ], style={'textAlign':'center'}),
                
                html.H2('Live Sun Colour Temperature Data', 
                        className="header-subtitle"
                        ),
                html.P(
                        "The outdoor colour temperature is based on the solar elevation and is a sinusoidal type plot. It shifts phase slightly everyday due to the changing sunrise and sunset times, which is why it is useful to track this live and have it dynamically change through the year (rather than alarms or schedulers which are fixed). It is collected through the Astral and PySolar Python APIs, then the model uses the ColourScience Module to convert elevation to an approximated Correlated Colour Temperature (CCT) in Kelvin.",
                        className="paragraph"
                        ),
                html.Div([
                    html.Iframe(src="https://thingspeak.com/channels/1570388/charts/2?bgcolor=%23000000&color=%23ffffff&dynamic=true&results=2000&title=Calculated+Outdoor+Colour+Temperature+versus+Time&type=line"
                    ,style={"width":"460px", "height":"230px", "style":"border: 1px solid #cccccc;"} ),
                ], style={'textAlign':'center'}),
                html.H2('Live Fitbit Data', 
                        className="header-subtitle"
                        ),
                html.P(
                        "The live data of my sleep state is uploaded at the end of each day through the FitBit Web API to ThingSpeak using a Raspberry Pi 3. It shows my different sleep states from 0 - 3, where 0 = Deep Sleep, 1 = Light Sleep, 2 = Rapid Eye Movement (REM) Sleep, 3 = Awake. Suprisingly we have periods of being awake whilst we sleep, but these are often too short to remember.", 
                        className="paragraph"
                        ),
                html.Div([
                    html.Iframe(src="https://thingspeak.com/channels/1573337/charts/1?bgcolor=%23000000&color=%23ffffff&dynamic=true&results=50&type=step"
                    ,style={"width":"460px", "height":"230px", "style":"border: 1px solid #cccccc;"} ),
                ], style={'textAlign':'center'}),
                ]
    
    ################################# 404 MESSAGE FOR INVALID PAGE
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

################################ RUNNING FINAL APP ####################################
if __name__ == "__main__":
    app.run_server()
#######################################################################################