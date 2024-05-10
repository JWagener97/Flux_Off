import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html,callback_context
import random
from collections import deque
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash_daq as daq
import serial.tools.list_ports
import serial
import time
import re 


T = deque(maxlen=100)
W = deque(maxlen=100)
V = deque(maxlen=100)
I = deque(maxlen=100)
P = deque(maxlen=100)
Y = deque(maxlen=100)
F = deque(maxlen=100)


T.append(0)
W.append(0)
V.append(0)
I.append(0)
P.append(0)
Y.append(0)
F.append(0)


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions=True



# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("CBI-MTB", className="display-4"),
        daq.PowerButton(
        id='MTB_Power_Switch',
        on=False,
        label='MTB Power Switch',
        labelPosition='top',
        size=100,
        color='green'
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Control", href="/", active="exact"),
                dbc.NavLink("Plots", href="/page-1", active="exact"),
                dbc.NavLink("Load Profile", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        dcc.Interval(
            id='graph-update',
            interval=2000,
            n_intervals = 0
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback([Input('MTB_Power_Switch', 'on')])
def update_output(on):
    if on:
        send_command_response_mtb(ser_MTB,"S1")
        send_command_response_mtb(ser_MTB,"V5.0")
        send_command_response_mtb(ser_MTB,"I1.0")
    else:
        send_command_response_mtb(ser_MTB,"S0")


@app.callback([Input('graph-update', 'n_intervals'),Input('MTB_Power_Switch', 'on')])
def update_output(n_intervals,on):


    if on:
        w_updated = v_updated = i_updated = p_updated = y_updated = f_updated = False

        while not all([w_updated, v_updated, i_updated, p_updated, y_updated, f_updated]):
            temp = ret_float(send_command_response_mtb(ser_MTB, "w"))
            if temp is not None:
                W.append(temp)
                w_updated = True

            temp = ret_float(send_command_response_mtb(ser_MTB, "v"))
            if temp is not None:
                V.append(temp)
                v_updated = True

            temp = ret_float(send_command_response_mtb(ser_MTB, "i"))
            if temp is not None:
                I.append(temp)
                i_updated = True

            temp = ret_float(send_command_response_mtb(ser_MTB, "p"))
            if temp is not None:
                P.append(temp)
                p_updated = True

            temp = ret_float(send_command_response_mtb(ser_MTB, "y"))
            if temp is not None:
                Y.append(temp)
                y_updated = True

            temp = ret_float(send_command_response_mtb(ser_MTB, "f"))
            if temp is not None:
                F.append(temp)
                f_updated = True

            if all([w_updated, v_updated, i_updated, p_updated, y_updated, f_updated]):
                T.append(T[-1] + 2)  # Increment the second counter


@app.callback(Output('live-power', 'figure'),
        [Input('graph-update', 'n_intervals'),])
def update_graph_scatter(n):
    data1 = go.Scatter(
            x=list(T),
            y=list(W),
            name='Scatter',
            mode= 'lines+markers'
            )
    data2 = go.Scatter(
        x=list(T),  # Assuming T and W are your data arrays
        y=list(Y),  # Assuming W2 is the data for the second trace
        name='Trace 2',
        mode='lines+markers'
    )

    return {'data': [data1,data2],'layout' : go.Layout(xaxis=dict(range=[min(T),max(T)]),
                                                yaxis=dict(range=[min(W),max(W)]),
                                                title="Power",title_x=0.5,
                                                xaxis_title="Time (s)",
                                                yaxis_title="Amplitude (W)",
                                                legend_title="Legend Title",
                                                font=dict(family="Courier New, monospace",size=18,color="RebeccaPurple"))
                                                
            }

@app.callback(Output('live-voltage', 'figure'),
        [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    data = go.Scatter(
            x=list(T),
            y=list(V),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(T),max(T)]),
                                                yaxis=dict(range=[min(V),max(V)]),
                                                title="Voltage",title_x=0.5,
                                                xaxis_title="Time (s)",
                                                yaxis_title="Amplitude (V)",
                                                legend_title="Legend Title",
                                                font=dict(family="Courier New, monospace",size=18,color="RebeccaPurple"))
                                                
            }

@app.callback(Output('live-current', 'figure'),
        [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    data = go.Scatter(
            x=list(T),
            y=list(I),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(T),max(T)]),
                                                yaxis=dict(range=[min(I),max(I)]),
                                                title="Current",title_x=0.5,
                                                xaxis_title="Time (s)",
                                                yaxis_title="Amplitude (A)",
                                                legend_title="Legend Title",
                                                font=dict(family="Courier New, monospace",size=18,color="RebeccaPurple"))
                                                
            }

@app.callback(Output('live-freq', 'figure'),
        [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    data = go.Scatter(
            x=list(T),
            y=list(F),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(T),max(T)]),
                                                yaxis=dict(range=[min(F),max(F)]),
                                                title="Freqency",title_x=0.5,
                                                xaxis_title="Time (s)",
                                                yaxis_title="Frequency (Hz)",
                                                legend_title="Legend Title",
                                                font=dict(family="Courier New, monospace",size=18,color="RebeccaPurple"))
                                                
            }

@app.callback(Output('live-pf', 'figure'),
        [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    data = go.Scatter(
            x=list(T),
            y=list(P),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(T),max(T)]),
                                                yaxis=dict(range=[min(P),max(P)]),
                                                title="Power - Factor",title_x=0.5,
                                                xaxis_title="Time (s)",
                                                yaxis_title="Power Factor[λ]",
                                                legend_title="Legend Title",
                                                font=dict(family="Courier New, monospace",size=18,color="RebeccaPurple"))
                                                
            }



@app.callback(Output('guage_cluster', 'figure'),
        [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):


    figure = make_subplots(
        rows=2,
        cols=3,                   
        specs=[[{'type': 'indicator'}, {'type': 'indicator'},{'type': 'indicator'}],
            [{'type': 'indicator'}, {'type': 'indicator'},{'type': 'indicator'}]],
            vertical_spacing = 0.2
        )
    
    figure.add_trace(go.Indicator(
    name = "Power",
    value=W[-1],
    mode="gauge+number",
    title={'text': "Power[W]"},
    number = {'valueformat':'.2f'},
    gauge={'axis': {'range': [None, 8000]},
           'bar': {'color': "black"},

           'steps': [
               {'range': [0, 4000], 'color': "green"},
               {'range': [4000, 6000], 'color': "orange"},
               {'range': [6000, 8000], 'color': "red"}],}),
           row=1,
           col=1,)

    figure.add_trace(go.Indicator(
    name = "Voltage",
        value=V[-1],
        mode="gauge+number",
        title={'text': 'Volts[rms]'},
        number = {'valueformat':'.2f'},
        gauge={'axis': {'range': [0, 270]},
               'bar': {'color': "black"},
               'steps': [
                   {'range': [0, 230], 'color': "green"},
                   {'range': [230, 250], 'color': "orange"},
                   {'range': [250, 270], 'color': "red"}],}),
           row=1,
           col=2,)
    
    figure.add_trace(go.Indicator(
        name = "Current",
        value=I[-1],
        mode="gauge+number",
        title={'text': 'Amps[rms]',},
        number = {'valueformat':'.2f'},
        gauge={'axis': {'range': [None, 105]},
               'bar': {'color': "black"},
               'steps': [
                   {'range': [0, 10], 'color': "green"},
                   {'range': [10, 70], 'color': "orange"},
                   {'range': [70, 105], 'color': "red"}],}),
               row=1,
               col=3,)
    
    figure.add_trace(go.Indicator(
        name = "VA",
        value=Y[-1],
        mode="gauge+number",
        title={'text': 'Volt-ampere[VA]'},
        number = {'valueformat':'.2f'},
        gauge={'axis': {'range': [None, 8000]},
           'bar': {'color': "black"},
           'steps': [
               {'range': [0, 4000], 'color': "green"},
               {'range': [4000, 6000], 'color': "orange"},
               {'range': [6000, 8000], 'color': "red"}],}),
               row=2,
               col=1,)
    
    figure.add_trace(go.Indicator(
        name = "Power_Factor",
        value=P[-1],
        mode="gauge+number",
        title={'text': "Power Factor[λ]"},
        number = {'valueformat':'.2f'},
        gauge={'axis': {'range': [-1.0, 1.0]},
               'bar': {'color': "black"},
               'steps': [
                   {'range': [-1, -0.5], 'color': "green"},
                   {'range': [-0.5, 0.5], 'color': "orange"},
                   {'range': [0.5, 1.0], 'color': "green"}],}),
               row=2,
               col=2,)
    
    figure.add_trace(go.Indicator(
        name = "Frequency",
        value=F[-1],
        mode="gauge+number",
        title={'text': 'Frequency[Hz]',},
        number = {'valueformat':'.2f'},
        gauge={'axis': {'range': [40, 66]},
               'bar': {'color': "black"},
               'steps': [
                   {'range': [40, 48], 'color': "orange"},
                   {'range': [48, 62], 'color': "green"},
                   {'range': [62, 66], 'color': "orange"}],}),
               row=2,
               col=3,)

    
    return figure


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.Div([
            html.Div([
            html.H5('Select Current Range'),
            html.Div([
            html.Div([dcc.Slider(id = "current-range-slider",min = 0, max = 2,step=None,marks={0: "0.1A", 1: "5A", 2: "80A"},value=0,),],style={'width': '90%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Input(id = "current-range-input",type="number", min=0, max=2, step=1),],style={'width': '7%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Button("Set",id="voltage-set", color="primary", className="me-1"),],style={'width': '3%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            ]),
            html.Hr(),
            ]),


            html.Div([
            html.H5('Set Current'),
            html.Div([
            html.Div([dcc.Slider(0, 105,0.01,value=0.00,marks=None,tooltip={"always_visible": True,"template": "{value} A"},),],style={'width': '90%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Input(type="number", min=0, max=10, step=1),],style={'width': '7%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Button("Set", color="primary", className="me-1"),],style={'width': '3%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            ]),
            html.Hr(),
            ]),


            html.Div([
            html.H5('Set Voltage'),
            html.Div([
            html.Div([dcc.Slider(id="voltage-slider",min=0,max=270,step=0.01,value=0.00,marks=None,tooltip={"always_visible": True,"template": "{value} V"},),],style={'width': '90%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Input(id="voltage-input",type="number", min=0, max=270, step=0.01),],style={'width': '7%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Button("Set",id="voltage-set", color="primary", className="me-1"),],style={'width': '3%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            ]),
            html.Hr(),
            ]),


            html.Div([
            html.H5('Set Power Factor'),
            html.Div([
            html.Div([dcc.Slider(-1, 1,0.1,value=1.0,marks=None,tooltip={"always_visible": True,"template": "{value} "},),],style={'width': '90%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Input(type="number", min=0, max=10, step=1),],style={'width': '7%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Button("Set", color="primary", className="me-1"),],style={'width': '3%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            ]),
            html.Hr(),
            ]),

            html.Div([
            html.H5('Set Frequency'),
            html.Div([
            html.Div([dcc.Slider(40, 66,0.1,value=50.0,marks=None,tooltip={"always_visible": True,"template": "{value} Hz"},),],style={'width': '90%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Input(type="number", min=0, max=10, step=1),],style={'width': '7%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            html.Div([dbc.Button("Set", color="primary", className="me-1"),],style={'width': '3%', 'display': 'inline-block','vertical-align': 'top','padding': '2px'}),
            ]),
            html.Hr()
            ]),

            dcc.Graph(id='guage_cluster'),

        ])
    elif pathname == "/page-1":
        return html.Div([
            html.H3('Live Plot of Parameters from the MTB'),
            dcc.Graph(id='live-power', animate=True),
            dcc.Graph(id='live-voltage', animate=True),
            dcc.Graph(id='live-current', animate=True),
            dcc.Graph(id='live-freq', animate=True),
            dcc.Graph(id='live-pf', animate=True),
        ])
    elif pathname == "/page-2":
        return html.Div([
            
        ])
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

@app.callback(
    Output("voltage-input", "value"),
    Output("voltage-slider", "value"),
    Input("voltage-input", "value"),
    Input("voltage-slider", "value"),
    Input("voltage-set", "n_clicks"),
)
def update_current(input_value, slider_value, n_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return [0.00, 0.00]
        print("")

    prop_id = ctx.triggered[0]["prop_id"]
    if prop_id == "voltage-input.value":
        return input_value, input_value
    elif prop_id == "voltage-slider.value":
        return slider_value, slider_value
    else:
        return [0.00, 0.00]

def send_command_response_mtb(ser_MTB,comm):
    ser_MTB.write((comm + "\r").encode())  # Ensure each command ends with CR
    time.sleep(0.2)
    response = b""
    if ser_MTB.in_waiting > 0:  # Check if there is data available to read
        while True:
            char = ser_MTB.read()
            if char == b'\r':
                break
            response += char
        dec_response = response.decode().strip()
        if dec_response == "":
            return None
        return dec_response
    else:
        return None  # No data written, so no need to read
    
def ret_float(temp):
    if temp != None:
        return float(re.sub("[^0-9^.-]", "", temp))
    else:
        return None

if __name__ == "__main__":
    # Define serial port settings
    port_MTB = "COM21"  # Change this to your serial port
    baud_rate_MTB = 2400
    bytesize_MTB = serial.EIGHTBITS
    parity_MTB = serial.PARITY_NONE
    stopbits_MTB = serial.STOPBITS_TWO  # Set to two stop bits
    try:
        #ser_MTB = serial.Serial(port_MTB, baud_rate_MTB, bytesize=bytesize_MTB, parity=parity_MTB, stopbits=stopbits_MTB, timeout=1)
        #app.run_server(debug = True,port = 90, use_reloader=False)
        app.run_server(host='0.0.0.0',port = 8050)
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    
    