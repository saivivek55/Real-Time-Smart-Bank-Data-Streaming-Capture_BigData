#code to visualize and move data from mobile sensor data. 
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from flask import Flask, request
import json
from datetime import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from confluent_kafka import Producer
from collections import deque
import pandas as pd

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Kafka configuration
def create_kafka_producer():
    config = {
            'bootstrap.servers': '####',  
            'client.id': 'transaction_data',
            'security.protocol': 'SASL_SSL',  
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': '####',  #API key
            'sasl.password': '####' #API Secret Key
    }
    return Producer(config)


producer = create_kafka_producer()
kafka_topic = 'abc'
excel_file_path = 'location_data.xlsx'

MAX_DATA_POINTS = 1000
UPDATE_FREQ_MS = 1000  


time = deque(maxlen=MAX_DATA_POINTS)
speed = deque(maxlen=MAX_DATA_POINTS)
altitude = deque(maxlen=MAX_DATA_POINTS)
longitude = deque(maxlen=MAX_DATA_POINTS)
latitude = deque(maxlen=MAX_DATA_POINTS)

app.layout = html.Div(
    [
        html.H1("Live Location Data Streamed from Sensor Logger"),
        dcc.Graph(id="live_graph"),
        dcc.Interval(id="counter", interval=UPDATE_FREQ_MS),
    ]
)

@app.callback(Output("live_graph", "figure"), [Input("counter", "n_intervals")])
def update_graph(_counter):
    if not time:
        raise PreventUpdate
    avg_lat = sum(latitude) / len(latitude) if latitude else None
    avg_lon = sum(longitude) / len(longitude) if longitude else None
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "scattergeo"}, {"type": "xy"}]],
        subplot_titles=('Map', 'Speed and Altitude'),
        column_widths=[0.5, 0.5]
    )
    fig.add_trace(
        go.Scattergeo(
            lon=list(longitude), 
            lat=list(latitude), 
            mode='lines+markers',
            name='Path',
            marker=dict(size=8, color='blue')
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=list(time), 
            y=list(speed), 
            name='Speed',
            mode='lines+markers',
            line=dict(color='red')
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=list(time), 
            y=list(altitude), 
            name='Altitude',
            mode='lines+markers',
            line=dict(color='green'),
            yaxis='y2'
        ),
        row=1, col=2
    )
    fig.update_layout(
        title_text='Live Location Tracking',
        showlegend=True,
        geo=dict(
            domain=dict(x=[0, 0.45], y=[0, 1]),
            center=dict(lat=avg_lat, lon=avg_lon) if avg_lat and avg_lon else dict(lat=0, lon=0),
            projection_type='equirectangular',
        ),
        xaxis=dict(domain=[0.55, 1], title='Time'),
        yaxis=dict(title='Speed (m/s)'),
        yaxis2=dict(
            title='Altitude (m)',
            overlaying='y',
            side='right',
            position=0.55
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    fig['layout']['yaxis2']['title'] = 'Altitude (m)'
    return fig

@server.route("/location", methods=["POST"])
def receive_data():
    print("Message delivered!")  
    if request.method == "POST":
        data = request.data
        print(f"Raw data: {data}")  
        try:
            json_data = json.loads(data)
            print(f"JSON data: {json_data}")  
        except json.JSONDecodeError:
            return "Bad JSON", 400
        
        data_records = []
        for d in json_data['payload']:
            ts = datetime.fromtimestamp(d["time"] / 1e9)
            values = d['values']
            
            # Append time-series data to deques
            time.append(ts)
            speed.append(values["speed"])
            altitude.append(values["altitude"])
            longitude.append(values["longitude"])
            latitude.append(values["latitude"])
            
            record = {
                "Time": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "Speed": values["speed"],
                "Altitude": values["altitude"],
                "Longitude": values["longitude"],
                "Latitude": values["latitude"],
                "DeviceId": json_data.get("deviceId", "Unknown"),
                "MessageId": json_data.get("messageId"),
                "SessionId": json_data.get("sessionId"),
                "BearingAccuracy": values.get("bearingAccuracy"),
                "SpeedAccuracy": values.get("speedAccuracy"),
                "VerticalAccuracy": values.get("verticalAccuracy"),
                "HorizontalAccuracy": values.get("horizontalAccuracy"),
                "Bearing": values.get("bearing")
            }
            data_records.append(record)
            
            producer.produce(kafka_topic, json.dumps(record).encode('utf-8'))
            producer.poll(0)

        if len(data_records) > 50: 
            df = pd.DataFrame(data_records)
            with pd.ExcelWriter(excel_file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, index=False)
        
        return "success", 200
    return "Method Not Allowed", 405

if __name__ == '__main__':
    app.run_server(debug=True, port=8000, host='0.0.0.0')