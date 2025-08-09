"""DS18B20 Arduino 연계 실시간 Dash 웹 애플리케이션."""
import datetime
import random
import sys
import time
import os

import dash
from dash import html, dcc, Input, Output, State
from typing import Any, cast
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from serial_json_communication import ArduinoJSONSerial
from port_manager import find_arduino_port
try:
    from serial.tools import list_ports
except Exception:
    list_ports = None

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# --- Helper & Initialization ---

def _configure_console_encoding():
    try:
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
    except Exception:
        pass

_configure_console_encoding()

def _get_initial_port_options():
    try:
        options = []
        default_val = None
        if list_ports is not None:
            ports = list(list_ports.comports())
            for p in ports:
                label = f"{p.device} - {p.description}"
                options.append({'label': label, 'value': p.device})
            if ports:
                default_val = ports[0].device
        if not options:
            options = [{'label': f'COM{i}', 'value': f'COM{i}'} for i in range(1, 11)]
            default_val = 'COM4'
        return options, default_val
    except Exception:
        return [], None

INITIAL_PORT_OPTIONS, INITIAL_PORT_VALUE = _get_initial_port_options()
detected_port = find_arduino_port()
selected_port = detected_port
SKIP_CONNECT = False
if detected_port:
    print(f"✅ Arduino 포트 자동 감지: {detected_port}")
else:
    print("⚠️ Arduino 포트 자동 감지 실패: UI에서 선택")
    SKIP_CONNECT = True

arduino = ArduinoJSONSerial(port=selected_port or 'COM4', baudrate=115200)
ARDUINO_CONNECTED = False

COLOR_SEQ = ["#2C7BE5", "#00A3A3", "#E67E22", "#6F42C1", "#FF6B6B", "#20C997", "#795548", "#FFB400"]
TH_DEFAULT = 55.0
TL_DEFAULT = -25.0

def try_arduino_connection(max_attempts=3):
    global ARDUINO_CONNECTED
    for attempt in range(1, max_attempts + 1):
        print(f"🔄 Arduino 연결 시도 {attempt}/{max_attempts}...")
        try:
            if arduino.connect():
                if arduino.start_reading():
                    ARDUINO_CONNECTED = True
                    print("✅ Arduino 연결 및 데이터 읽기 시작 성공!")
                    return True
                else:
                    print("⚠️ 연결은 성공했지만 데이터 읽기 시작 실패")
                    arduino.disconnect()
            else:
                print(f"❌ 연결 시도 {attempt} 실패")
        except (ConnectionError, OSError, PermissionError) as e:
            print(f"❌ 연결 오류 (시도 {attempt}): {e}")
        if attempt < max_attempts:
            print("⏳ 2초 후 재시도...")
            time.sleep(2)
    print("❌ 모든 연결 시도 실패 - 시뮬레이션 모드")
    return False

if not SKIP_CONNECT:
    try_arduino_connection()
else:
    print("연결 시도 건너뜀 (시뮬레이션)")

def _snapshot():
    """Collect current data snapshot from Arduino or simulation."""
    global ARDUINO_CONNECTED
    if ARDUINO_CONNECTED and not arduino.is_healthy():
        ARDUINO_CONNECTED = False
        print("⚠️ Arduino 연결 상태 불량 감지 - 시뮬레이션 모드 전환")
    if ARDUINO_CONNECTED and arduino.is_healthy():
        stats = arduino.get_connection_stats()
        connection_status = f"🟢 Arduino 연결됨 (데이터: {stats['sensor_data_count']}개)"
        connection_style = {'textAlign':'center','margin':'10px','padding':'10px','border':'2px solid green','borderRadius':'5px','color':'green'}
        current_temps = arduino.get_current_temperatures()
        latest_data = arduino.get_latest_sensor_data(count=50)
        system_messages = arduino.get_system_messages(count=10)
        print(f"🔍 실제 데이터 사용: 현재온도={len(current_temps)}개, 최신데이터={len(latest_data)}개")
    else:
        connection_status = "🔴 Arduino 연결 끊김 (시뮬레이션 모드)"
        connection_style = {'textAlign':'center','margin':'10px','padding':'10px','border':'2px solid red','borderRadius':'5px','color':'red'}
        current_temps = {i: {'temperature': round(20 + random.uniform(-5, 15), 1), 'status': 'simulated'} for i in range(1,5)}
        times = [datetime.datetime.now() - datetime.timedelta(seconds=i) for i in range(30,0,-1)]
        latest_data = []
        for t in times:
            for sid in range(1,5):
                latest_data.append({'timestamp': t, 'sensor_id': sid, 'temperature': 20 + random.uniform(-5,15)})
        system_messages = [{'timestamp': datetime.datetime.now(), 'message': 'Simulation mode active', 'level': 'warning'}]
    return connection_status, connection_style, current_temps, latest_data, system_messages

@app.callback(
    [Output('connection-status','children'), Output('connection-status','style')]
    +[Output(f'sensor-{i}-temp','children') for i in range(1,9)]
    +[Output(f'sensor-{i}-status','children') for i in range(1,9)]
    +[Output('system-log','children'), Output('system-log-v2','children')],
    Input('interval-component','n_intervals'), State('ui-version-store','data'), prevent_initial_call=True)
def update_status_and_log(_n, ui_version):
    connection_status, connection_style, current_temps, _latest_data, system_messages = _snapshot()
    sensor_temps, sensor_statuses = [], []
    for i in range(1,9):
        if i in current_temps:
            info = current_temps[i]
            sensor_temps.append(f"{info['temperature']:.1f}°C")
            status = info.get('status','')
            if status == 'ok': sensor_statuses.append('🟢 정상')
            elif status == 'simulated': sensor_statuses.append('🟡 시뮬레이션')
            else: sensor_statuses.append(f"⚠️ {status}")
        else:
            sensor_temps.append('--°C')
            sensor_statuses.append('🔴 연결 없음')
    log_entries = []
    for msg in system_messages:
        ts = msg['timestamp'].strftime('%H:%M:%S')
        level_icons = {"info":"ℹ️","warning":"⚠️","error":"❌"}
        icon = level_icons.get(msg['level'],'📝')
        log_entries.append(html.Div(f"[{ts}] {icon} {msg['message']}"))
    return [connection_status, connection_style] + sensor_temps + sensor_statuses + [log_entries, log_entries]

@app.callback(
    [Output('temp-graph','figure'), Output('detail-sensor-graph','figure')],
    [Input('interval-component','n_intervals'), Input('detail-sensor-dropdown','value')],
    [State('threshold-store','data'), State('ui-version-store','data')], prevent_initial_call=True)
def update_main_graphs(_n, detail_sensor_id, threshold_map, ui_version):
    if detail_sensor_id is None: detail_sensor_id = 1
    _, _, _current_temps, latest_data, _msgs = _snapshot()
    # Temp overview graph
    if latest_data:
        df = pd.DataFrame(latest_data)
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['sensor_id'] = df['sensor_id'].astype(str)
        except Exception: pass
        try:
            fig = px.line(df, x='timestamp', y='temperature', color='sensor_id',
                          title='실시간 온도 모니터링 (최근 50개 데이터)', template='plotly_white')
        except Exception:
            fig = go.Figure()
            for sid, g in df.groupby('sensor_id'):
                fig.add_trace(go.Scatter(x=g['timestamp'], y=g['temperature'], mode='lines', name=sid))
            fig.update_layout(title='실시간 온도 모니터링 (최근 50개 데이터)', template='plotly_white')
    else:
        fig = go.Figure(); fig.update_layout(title='데이터 없음', template='plotly_white')
    # Add global TH/TL lines
    try:
        fig.add_hline(y=TH_DEFAULT, line_dash='dash', line_color='red', annotation_text='TH', annotation_position='top left')
        fig.add_hline(y=TL_DEFAULT, line_dash='dash', line_color='blue', annotation_text='TL', annotation_position='bottom left')
    except Exception:
        pass

    # Detail graph
    if latest_data:
        df_all = pd.DataFrame(latest_data)
        try:
            df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
            df_all['sensor_id'] = df_all['sensor_id'].astype(int)
        except Exception: pass
        one = df_all[df_all['sensor_id']==detail_sensor_id]
        if not one.empty:
            try:
                detail_fig = px.line(one, x='timestamp', y='temperature', title=f'센서 {detail_sensor_id} 상세 그래프', template='plotly_white')
            except Exception:
                detail_fig = go.Figure(); detail_fig.add_trace(go.Scatter(x=one['timestamp'], y=one['temperature'], mode='lines', name=f'센서 {detail_sensor_id}'))
        else:
            detail_fig = go.Figure(); detail_fig.update_layout(title=f'센서 {detail_sensor_id} 데이터 없음', template='plotly_white')
    else:
        detail_fig = go.Figure(); detail_fig.update_layout(title='상세 데이터 없음', template='plotly_white')
    try:
        detail_fig.add_hline(y=TH_DEFAULT, line_dash='dash', line_color='red')
        detail_fig.add_hline(y=TL_DEFAULT, line_dash='dash', line_color='blue')
    except Exception:
        pass
    fig.update_layout(height=440); detail_fig.update_layout(height=440)
    return fig, detail_fig

@app.callback(Output('combined-graph','figure'), [Input('interval-component','n_intervals'), Input('sensor-line-toggle','value')], State('ui-version-store','data'), prevent_initial_call=True)
def update_combined_graph(_n, selected_sensor_lines, ui_version):
    if not isinstance(selected_sensor_lines, list) or not selected_sensor_lines:
        selected_sensor_lines = [i for i in range(1,9)]
    _, _, _current_temps, latest_data, _msgs = _snapshot()
    if latest_data:
        try:
            df = pd.DataFrame(latest_data)
            df['sensor_id'] = df['sensor_id'].astype(int)
            df = df[df['sensor_id'].isin(selected_sensor_lines)]
            fig = go.Figure()
            color_map = {int(sid): COLOR_SEQ[(sid-1)%len(COLOR_SEQ)] for sid in range(1,9)}
            for sid, g in df.groupby('sensor_id'):
                fig.add_trace(go.Scatter(x=g['timestamp'], y=g['temperature'], mode='lines', name=f'센서 {sid}', line=dict(color=color_map.get(int(sid),'#888'), width=2)))
            if ui_version == 'v2':
                fig.update_layout(title='전체 센서 실시간 온도', template='plotly_dark', height=480, showlegend=False, plot_bgcolor='#000', paper_bgcolor='#000')
            else:
                fig.update_layout(title='전체 센서 실시간 온도', template='plotly_white', height=480, showlegend=False)
            try:
                fig.add_hline(y=TH_DEFAULT, line_dash='dash', line_color='red')
                fig.add_hline(y=TL_DEFAULT, line_dash='dash', line_color='blue')
            except Exception:
                pass
        except Exception:
            fig = go.Figure(); fig.update_layout(title='전체 센서 실시간 온도 (오류)', height=480, template='plotly_dark' if ui_version=='v2' else 'plotly_white')
    else:
        fig = go.Figure(); fig.update_layout(title='전체 센서 실시간 온도 (데이터 없음)', height=480, template='plotly_dark' if ui_version=='v2' else 'plotly_white')
    return fig

def create_layout_v2():
    """Night mode (v2) – dark theme; mirror v1 structure & combined graph."""
    sensor_cards = []
    for i in range(1, 9):
        # Placeholder figure (will be replaced by live callback)
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, visible=False),
            height=100,
            showlegend=False
        )
        card = html.Div([
            html.Div([
                html.H4(f"센서 ID {i}", style={'color': 'white', 'marginBottom': '5px'}),
                html.P("--°C", id=f'sensor-{i}-temp', style={'fontSize': '32px', 'fontWeight': 'bold', 'color': 'white', 'margin': '0'})
            ], style={'flex': '0 1 150px', 'padding': '20px'}),
            html.Div([
                html.Div([
                    html.Button('ID 변경', id=f'btn-change-id-v2-{i}', style={'backgroundColor': '#555', 'color': 'white', 'border': 'none', 'padding': '5px 10px', 'margin': '0 5px'}),
                    html.Button('상/하한 온도 임계값 변경', id=f'btn-change-thresholds-v2-{i}', style={'backgroundColor': '#555', 'color': 'white', 'border': 'none', 'padding': '5px 10px', 'margin': '0 5px'}),
                    html.Button('측정주기 변경 (현재 1초)', id=f'btn-change-interval-v2-{i}', style={'backgroundColor': '#555', 'color': 'white', 'border': 'none', 'padding': '5px 10px', 'margin': '0 5px'}),
                ], style={'marginBottom': '10px'}),
                dcc.Graph(id=f'sensor-{i}-mini-graph', figure=fig, style={'height': '100px'}, config={'displayModeBar': False})
            ], style={'flex': '1', 'padding': '10px'}),
            html.Div([html.Span('⚙️', style={'fontSize': '24px', 'cursor': 'pointer'})], style={'padding': '20px', 'display': 'flex', 'alignItems': 'center'})
        ], style={'display': 'flex', 'alignItems': 'center', 'backgroundColor': '#1e1e1e', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid #444'})
        sensor_cards.append(card)

    control_panel_v2 = html.Div([
        html.Div([
            html.H3('포트 연결', style={'margin': '4px 0', 'color': 'white'}),
            dcc.Dropdown(
                id='port-dropdown-v2',
                options=cast(Any, INITIAL_PORT_OPTIONS),
                value=selected_port or INITIAL_PORT_VALUE,
                placeholder='자동 감지 또는 포트 선택',
                style={'width': '100%', 'marginBottom': '10px'}
            ),
            html.Button('선택 포트로 연결', id='connect-port-btn-v2', n_clicks=0, style={'width': '100%', 'marginBottom': '20px'})
        ], style={'padding': '20px', 'backgroundColor': '#1e1e1e', 'borderRadius': '10px', 'marginBottom': '15px'}),
        html.Div([
            html.H3("제어 패널", style={'color': 'white'}),
            html.Button('Arduino 재연결', id='reconnect-btn-v2', n_clicks=0, style={'margin': '5px', 'width': '100%'}),
            html.Button('JSON 모드 토글', id='json-toggle-btn-v2', n_clicks=0, style={'margin': '5px', 'width': '100%'}),
            html.Button('통계 요청', id='stats-btn-v2', n_clicks=0, style={'margin': '5px', 'width': '100%'}),
        ], style={'padding': '20px', 'backgroundColor': '#1e1e1e', 'borderRadius': '10px', 'marginBottom': '15px'}),
        html.Div([
            html.H3("시스템 로그", style={'color': 'white'}),
            html.Div(id='system-log-v2',
                     style={'height': '200px', 'overflow': 'auto', 'border': '1px solid #444', 'padding': '10px',
                            'backgroundColor': '#111', 'fontFamily': 'monospace'})
        ], style={'padding': '20px', 'backgroundColor': '#1e1e1e', 'borderRadius': '10px'}),
    ])

    combined_graph_block = html.Div([
        html.H4("전체 센서 실시간 그래프 (1~8)", style={'margin': '0 0 8px 0', 'textAlign': 'center', 'color': 'white'}),
        html.Div([
            dcc.Graph(id='combined-graph', style={'flex': '1', 'height': '480px'}, config={'displaylogo': False}),
            html.Div([
                html.Strong("표시 센서", style={'color': 'white', 'display': 'block', 'marginBottom': '4px'}),
                # Checklist (selection control)
                dcc.Checklist(
                    id='sensor-line-toggle',
                    options=[{'label': f"센서 {i}", 'value': i} for i in range(1,9)],
                    value=[i for i in range(1,9)],
                    labelStyle={'display': 'block', 'margin': '2px 0', 'color': 'white'}
                ),
                html.Div([
                    html.Div([
                        html.Span(style={
                            'display': 'inline-block', 'width': '10px', 'height': '10px',
                            'backgroundColor': COLOR_SEQ[i-1], 'marginRight': '6px',
                            'borderRadius': '2px'
                        }),
                        html.Span(f"센서 {i}", style={'fontSize': '11px', 'color': 'white'})
                    ], style={'display': 'flex', 'alignItems': 'center', 'margin': '2px 0'})
                    for i in range(1,9)
                ], id='sensor-color-legend', style={'marginTop': '6px', 'marginBottom': '6px'}),
                html.Button('전체 선택', id='btn-select-all', n_clicks=0, style={'marginTop': '6px', 'width': '100%'}),
                html.Button('전체 해제', id='btn-deselect-all', n_clicks=0, style={'marginTop': '4px', 'width': '100%'}),
            ], style={'width': '140px', 'marginLeft': '12px'})
        ], style={'display': 'flex', 'alignItems': 'flex-start'})
    ], style={'padding': '16px', 'backgroundColor': '#1e1e1e', 'borderRadius': '10px', 'border': '1px solid #444', 'marginBottom': '20px'})

    return html.Div(
        style={'backgroundColor': 'black','color': 'white','padding': '20px','height': '100vh','overflowY': 'scroll'},
        children=[
            html.H2("🌙 Sensor Dashboard - Night Mode (v2)", style={'textAlign': 'center', 'marginBottom': '20px'}),
            *sensor_cards,
            # Interval selection modal (hidden overlay)
            html.Div(id='interval-modal', style={'position': 'fixed', 'top': 0, 'left':0, 'right':0, 'bottom':0, 'backgroundColor':'rgba(0,0,0,0.6)', 'display':'none', 'alignItems':'center', 'justifyContent':'center', 'zIndex': 2000}, children=[
                html.Div(style={'backgroundColor':'#222','padding':'20px','borderRadius':'8px','width':'320px','color':'white','boxShadow':'0 0 10px #000'}, children=[
                    html.H4('측정 주기 선택', style={'marginTop':0}),
                    dcc.Dropdown(id='interval-select', options=[
                        {'label':'1초','value':1000}, {'label':'5초','value':5000}, {'label':'10초','value':10000}, {'label':'20초','value':20000}, {'label':'30초','value':30000},
                        {'label':'1분','value':60000}, {'label':'3분','value':180000}, {'label':'5분','value':300000}, {'label':'10분','value':600000}, {'label':'20분','value':1200000},
                        {'label':'40분','value':2400000}, {'label':'1시간','value':3600000}
                    ], placeholder='주기 선택', style={'marginBottom':'10px'}),
                    html.Div(id='interval-selected-preview', style={'marginBottom':'10px','fontSize':'14px','color':'#ddd'}),
                    html.Div([
                        html.Button('적용', id='interval-apply-btn', n_clicks=0, style={'marginRight':'10px'}),
                        html.Button('취소', id='interval-cancel-btn', n_clicks=0, style={'backgroundColor':'#444','color':'white'})
                    ], style={'textAlign':'right'})
                ])
            ]),
            dcc.ConfirmDialog(id='interval-confirm-dialog'),
            combined_graph_block,
            control_panel_v2,
            # Hidden placeholders so shared callback outputs always have valid targets
            html.Div([
                html.Div(id='connection-status'),
                dcc.Graph(id='temp-graph'),
                html.Div(id='system-log'),
                dcc.Dropdown(id='detail-sensor-dropdown', value=1),
                dcc.Graph(id='detail-sensor-graph'),
                *[html.Div(id=f'sensor-{i}-status') for i in range(1,9)]
            ], style={'display': 'none'})
        ]
    )

def create_layout_v1():
    return html.Div([
        html.H1("☀️ DS18B20 센서 데이터 대시보드 (Day Mode)", style={'textAlign':'center','color':'#2c3e50'}),
        html.Div(
            f"UI Build: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            style={'textAlign':'center','color':'#6c757d','fontSize':'12px','marginBottom':'6px'}
        ),
        html.Div([
            html.Div(id='connection-status', style={'textAlign':'center','margin':'10px','padding':'10px','border':'2px solid','borderRadius':'5px'}),
            html.Div([
                html.H3('포트 연결', style={'margin':'4px 0'}),
                html.Span('포트 선택: ', style={'marginRight':'6px'}),
                dcc.Dropdown(id='port-dropdown', options=cast(Any, INITIAL_PORT_OPTIONS), value=selected_port or INITIAL_PORT_VALUE,
                             placeholder='자동 감지 또는 포트 선택', style={'display':'inline-block','width':'260px','marginRight':'8px'}),
                html.Button('선택 포트로 연결', id='connect-port-btn', n_clicks=0, style={'display':'inline-block'})
            ], style={'textAlign':'center','marginTop':'8px'})
        ]),
        html.Hr(),
        html.Div([
            html.Div([
                html.H3("센서 상태", style={'textAlign':'center'}),
                html.Div(id='sensor-cards', children=[
                    html.Div([
                        html.H4(f"센서 {i}", style={'margin':'5px'}),
                        html.Div(id=f'sensor-{i}-temp', children="--°C", style={'fontSize':'24px','fontWeight':'bold'}),
                        html.Div(id=f'sensor-{i}-status', children="연결 대기", style={'fontSize':'12px','color':'#666'})
                    ], style={'display':'inline-block','margin':'10px','padding':'20px','border':'1px solid #ddd','borderRadius':'8px','width':'170px','textAlign':'center','backgroundColor':'#f9f9f9'})
                    for i in range(1,9)
                ]),
                html.Div([
                    html.Div([
                        html.H4("전체 센서 실시간 그래프 (1~8)", style={'margin':'0 0 8px 0','textAlign':'center'}),
                        html.Div([
                            dcc.Graph(id='combined-graph', style={'flex':'1'}, config={'displaylogo': False}),
                            html.Div([
                                html.Strong("표시 센서"),
                                dcc.Checklist(id='sensor-line-toggle', options=[{'label':f"센서 {i}",'value':i} for i in range(1,9)], value=[i for i in range(1,9)], labelStyle={'display':'block','margin':'2px 0'}),
                                html.Button('전체 선택', id='btn-select-all', n_clicks=0, style={'marginTop':'6px','width':'100%'}),
                                html.Button('전체 해제', id='btn-deselect-all', n_clicks=0, style={'marginTop':'4px','width':'100%'}),
                            ], style={'width':'140px','marginLeft':'12px'})
                        ], style={'display':'flex','alignItems':'flex-start'})
                    ], style={'marginTop':'20px','padding':'10px','border':'1px solid #ddd','borderRadius':'8px','backgroundColor':'#fff'})
                ])
            ], style={'flex':'1','minWidth':'340px'}),
            html.Div([
                html.H3("빠른 설정", style={'textAlign':'center'}),
                html.Div([
                    html.Label('포트 선택', style={'fontWeight':'bold'}),
                    dcc.Dropdown(id='port-dropdown-2', options=cast(Any, INITIAL_PORT_OPTIONS), value=selected_port or INITIAL_PORT_VALUE, placeholder='포트 선택', style={'width':'100%','marginBottom':'6px'}),
                    html.Button('선택 포트로 연결', id='connect-port-btn-2', n_clicks=0, style={'width':'100%','marginBottom':'16px'})
                ], style={'marginBottom':'10px'}),
                html.Div([
                    html.Button('ID 변경', id='btn-change-id', n_clicks=0, style={'width':'100%','marginBottom':'10px'}),
                    dcc.Input(id='input-old-id', type='number', placeholder='현재 ID', min=1, max=64, style={'width':'48%','marginRight':'4%'}),
                    dcc.Input(id='input-new-id', type='number', placeholder='새 ID', min=1, max=64, style={'width':'48%'}),
                ], style={'marginBottom':'15px'}),
                html.Div([
                    html.Button('임계값 변경 (TL/TH)', id='btn-change-thresholds', n_clicks=0, style={'width':'100%','marginBottom':'10px'}),
                    dcc.Input(id='input-target-id', type='number', placeholder='센서 ID', min=1, max=64, style={'width':'100%','marginBottom':'6px'}),
                    dcc.Input(id='input-tl', type='number', placeholder='TL 하한(°C)', step=0.5, style={'width':'48%','marginRight':'4%'}),
                    dcc.Input(id='input-th', type='number', placeholder='TH 상한(°C)', step=0.5, style={'width':'48%'}),
                ], style={'marginBottom':'15px'}),
                html.Div([
                    html.Button('측정 주기 변경', id='btn-change-interval', n_clicks=0, style={'width':'100%','marginBottom':'10px'}),
                    dcc.Input(id='input-interval', type='number', placeholder='주기(ms)', min=100, step=100, style={'width':'100%'}),
                ]),
            ], style={'width':'280px','marginLeft':'20px','padding':'10px','border':'1px solid #ddd','borderRadius':'8px','height':'100%'}),
        ], style={'display':'flex','alignItems':'flex-start','flexWrap':'wrap'}),
        html.Hr(),
        html.Div([
            dcc.Graph(id='temp-graph', style={'height':'440px'}, config={'displaylogo': False}),
            html.Div([
                html.Div([
                    html.Label('상세 그래프 센서 선택'),
                    dcc.Dropdown(id='detail-sensor-dropdown', options=[{'label':f'센서 {i}','value':i} for i in range(1,65)], value=1, clearable=False, style={'width':'200px'})
                ], style={'marginBottom':'10px'}),
                dcc.Graph(id='detail-sensor-graph', style={'height':'440px'}, config={'displaylogo': False})
            ], style={'marginTop':'20px'})
        ], style={'margin':'20px'}),
        html.Div([
            html.H3("제어 패널"),
            html.Button('Arduino 재연결', id='reconnect-btn', n_clicks=0, style={'margin':'5px','padding':'10px'}),
            html.Button('JSON 모드 토글', id='json-toggle-btn', n_clicks=0, style={'margin':'5px','padding':'10px'}),
            html.Button('통계 요청', id='stats-btn', n_clicks=0, style={'margin':'5px','padding':'10px'}),
        ], style={'margin':'20px','padding':'15px','backgroundColor':'#f0f0f0','borderRadius':'5px'}),
        html.Div([
            html.H3("시스템 로그"),
            html.Div(id='system-log', style={'height':'200px','overflow':'auto','border':'1px solid #ddd','padding':'10px','backgroundColor':'#f8f8f8','fontFamily':'monospace'})
        ], style={'margin':'20px'}),
        html.Div([
            html.Div(id='system-log-v2'),
            dcc.Dropdown(id='port-dropdown-v2')
        ], style={'display':'none'})
    ])


# --- Main App Layout ---
app.layout = html.Div([
    html.Div([
        html.H1("DS18B20 Dashboard", style={'flex': '1'}),
        html.Div([
            html.Button('☀️ Day (v1)', id='btn-ver-1', n_clicks=0, style={'marginRight': '5px'}),
            html.Button('🌙 Night (v2)', id='btn-ver-2', n_clicks=0),
        ], style={'textAlign': 'right'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'padding': '10px', 'borderBottom': '1px solid #ddd'}),
    html.Div(id='mode-indicator', style={'textAlign':'center','fontWeight':'bold','color':'#007bff','margin':'8px'}),
    html.Div(id='mode-feedback', style={'textAlign':'center','color':'#28a745','marginBottom':'8px'}),
    dcc.Store(id='ui-version-store', data='v1'),
    html.Div(id='main-content', children=create_layout_v1()),
    # Common components that should always be present
    dcc.Interval(
        id='interval-component',
        interval=1000,
        n_intervals=0
    ),
    dcc.Store(id='sensor-data-store'),
    dcc.Store(id='threshold-store', data={}),
    dcc.Store(id='last-command-result'),
    dcc.Store(id='port-options-cache'),
    dcc.Store(id='sensor-intervals-store'),
    dcc.Store(id='interval-modal-target-sensor'),
    dcc.Store(id='pending-interval-selection')
])
# --- Main App Layout ---
@app.callback(
    Output('mode-indicator', 'children'),
    Output('mode-feedback', 'children'),
    Input('ui-version-store', 'data')
)
def show_mode_indicator_and_feedback(ui_version):
    if ui_version == 'v2':
        return "현재 모드: 🌙 Night (v2)", "🌙 Night 모드로 전환됨"
    return "현재 모드: ☀️ Day (v1)", "☀️ Day 모드로 전환됨"

# --- Validation Layout (superset of all component IDs) ---
def build_validation_layout():
    return html.Div([
    # Version switch buttons (ensure inputs exist for callbacks during validation)
    html.Button(id='btn-ver-1'),
    html.Button(id='btn-ver-2'),
        html.Div(id='main-content'),
        dcc.Store(id='ui-version-store'),
        dcc.Interval(id='interval-component'),
        html.Div(id='connection-status'),
        dcc.Graph(id='temp-graph'),
        html.Div(id='system-log'),
        dcc.Dropdown(id='detail-sensor-dropdown'),
        dcc.Graph(id='detail-sensor-graph'),
        dcc.Graph(id='combined-graph'),
        html.Div(id='system-log-v2'),
        dcc.Dropdown(id='port-dropdown'),
        dcc.Dropdown(id='port-dropdown-2'),
        dcc.Dropdown(id='port-dropdown-v2'),
        dcc.Checklist(id='sensor-line-toggle'),
        html.Button(id='btn-select-all'),
        html.Button(id='btn-deselect-all'),
        html.Button(id='reconnect-btn'),
        html.Button(id='reconnect-btn-v2'),
        html.Button(id='json-toggle-btn'),
        html.Button(id='json-toggle-btn-v2'),
        html.Button(id='stats-btn'),
        html.Button(id='stats-btn-v2'),
        html.Button(id='connect-port-btn'),
        html.Button(id='connect-port-btn-2'),
        html.Button(id='connect-port-btn-v2'),
        html.Button(id='btn-change-id'),
        html.Button(id='btn-change-thresholds'),
        html.Button(id='btn-change-interval'),
        dcc.Input(id='input-old-id'),
        dcc.Input(id='input-new-id'),
        dcc.Input(id='input-target-id'),
        dcc.Input(id='input-tl'),
        dcc.Input(id='input-th'),
        dcc.Input(id='input-interval'),
        dcc.Store(id='threshold-store'),
        dcc.Store(id='last-command-result'),
        dcc.Store(id='sensor-intervals-store'),
        dcc.Store(id='interval-modal-target-sensor'),
        dcc.Store(id='pending-interval-selection'),
        *[html.Div(id=f'sensor-{i}-temp') for i in range(1,9)],
        *[html.Div(id=f'sensor-{i}-status') for i in range(1,9)],
    # v2 mini sensor graphs (validation placeholders)
    *[dcc.Graph(id=f'sensor-{i}-mini-graph') for i in range(1,9)],
    # interval modal & related components
    html.Div(id='interval-modal'),
    dcc.Dropdown(id='interval-select'),
    html.Button(id='interval-apply-btn'),
    html.Button(id='interval-cancel-btn'),
    dcc.ConfirmDialog(id='interval-confirm-dialog'),
    *[html.Button(id=f'btn-change-interval-v2-{i}') for i in range(1,9)],
    ])

app.validation_layout = build_validation_layout()

# --- Callbacks ---

@app.callback(
    Output('main-content', 'children'),
    Output('ui-version-store', 'data'),
    Input('btn-ver-1', 'n_clicks'),
    Input('btn-ver-2', 'n_clicks'),
    State('ui-version-store', 'data')
)
def update_main_layout(n1, n2, current_version):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'btn-ver-1' # Default to v1
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-ver-2':
        print("🌙 Night mode 버튼 클릭 - v2 레이아웃 전환")
        return create_layout_v2(), 'v2'
    else: # btn-ver-1 or default
        if button_id == 'btn-ver-1':
            print("☀️ Day mode 버튼 클릭 - v1 레이아웃 전환")
        return create_layout_v1(), 'v1'



@app.callback(
    Output('sensor-line-toggle', 'value'),
    Input('btn-select-all', 'n_clicks'),
    Input('btn-deselect-all', 'n_clicks'),
    State('sensor-line-toggle', 'value'),
    prevent_initial_call=True
)
def toggle_all_lines(n_all, n_none, current):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current
    bid = ctx.triggered[0]['prop_id'].split('.')[0]
    if bid == 'btn-select-all':
        return [i for i in range(1,9)]
    if bid == 'btn-deselect-all':
        return []
    return current

@app.callback(
    Output('reconnect-btn', 'children'),
    [Input('reconnect-btn', 'n_clicks')]
)
def reconnect_arduino(n_clicks):
    global ARDUINO_CONNECTED
    if n_clicks > 0:
        print("🔄 수동 재연결 시도...")
        try:
            arduino.disconnect()
            time.sleep(1)
        except Exception as e:
            print(f"연결 해제 중 오류: {e}")
        try:
            if arduino.connect():
                if arduino.start_reading():
                    ARDUINO_CONNECTED = True
                    print("✅ 수동 재연결 성공!")
                    return "✅ 재연결 성공"
                else:
                    arduino.disconnect()
                    ARDUINO_CONNECTED = False
                    return "❌ 데이터 읽기 실패"
            else:
                ARDUINO_CONNECTED = False
                return "❌ 연결 실패"
        except PermissionError:
            ARDUINO_CONNECTED = False
            return "❌ 포트 접근 거부"
        except Exception as e:
            ARDUINO_CONNECTED = False
            return f"❌ 오류: {str(e)[:15]}..."
    return "Arduino 재연결"

@app.callback(
    Output('json-toggle-btn', 'children'),
    [Input('json-toggle-btn', 'n_clicks')]
)
def toggle_json_mode(n_clicks):
    if n_clicks > 0 and ARDUINO_CONNECTED:
        command = {"type": "config", "action": "toggle_json_mode"}
        if arduino.send_command(command):
            return "📡 JSON 토글 전송됨"
        return "❌ 명령 전송 실패"
    return "JSON 모드 토글"

@app.callback(
    Output('stats-btn', 'children'),
    [Input('stats-btn', 'n_clicks')]
)
def request_stats(n_clicks):
    if n_clicks > 0 and ARDUINO_CONNECTED:
        command = {"type": "request", "action": "get_stats"}
        if arduino.send_command(command):
            return "📊 통계 요청됨"
        return "❌ 요청 실패"
    return "통계 요청"

@app.callback(
    [Output('port-dropdown', 'options'),
     Output('port-dropdown', 'value'),
     Output('port-dropdown-2', 'options'),
     Output('port-dropdown-2', 'value')],
    [Input('interval-component', 'n_intervals')],
    [State('port-dropdown', 'value'),
    State('port-dropdown-2', 'value')],
    prevent_initial_call=True
)
def refresh_port_options(_n, current_value_1, current_value_2):
    try:
        options, default_val = _get_initial_port_options()
        values_set = {o['value'] for o in options}
        value1 = current_value_1 if current_value_1 in values_set else default_val
        value2 = current_value_2 if current_value_2 in values_set else value1
        return options, value1, options, value2
    except Exception:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('connect-port-btn', 'children'),
    Input('connect-port-btn', 'n_clicks'),
    State('port-dropdown', 'value'),
    prevent_initial_call=True
)
def connect_to_selected_port(n_clicks, selected):
    global ARDUINO_CONNECTED
    if not n_clicks: return "선택 포트로 연결"
    if not selected: return "❌ 포트 선택 필요"
    try:
        try:
            arduino.disconnect()
            time.sleep(0.5)
        except Exception: pass
        arduino.port = selected
        if arduino.connect():
            if arduino.start_reading():
                ARDUINO_CONNECTED = True
                return f"✅ 연결됨: {selected}"
        ARDUINO_CONNECTED = False
        return "❌ 연결 실패"
    except Exception as e:
        ARDUINO_CONNECTED = False
        return f"❌ 오류: {str(e)[:20]}..."

@app.callback(
    Output('connect-port-btn-2', 'children'),
    Input('connect-port-btn-2', 'n_clicks'),
    State('port-dropdown-2', 'value'),
    prevent_initial_call=True
)
def connect_to_selected_port_sidebar(n_clicks, selected):
    return connect_to_selected_port(n_clicks, selected)


@app.callback(
    Output('last-command-result', 'data'),
    Output('threshold-store', 'data'),
    Input('btn-change-id', 'n_clicks'),
    Input('btn-change-thresholds', 'n_clicks'),
    Input('btn-change-interval', 'n_clicks'),
    State('input-old-id', 'value'),
    State('input-new-id', 'value'),
    State('input-target-id', 'value'),
    State('input-tl', 'value'),
    State('input-th', 'value'),
    State('input-interval', 'value'),
    State('threshold-store', 'data'),
    prevent_initial_call=True
)
def handle_quick_commands(n1, n2, n3, old_id, new_id, target_id, tl, th, interval_ms, threshold_map):
    result = {'ok': False, 'message': 'no-op'}
    if not ARDUINO_CONNECTED:
        return ({'ok': False, 'message': 'Arduino 미연결'}, threshold_map)

    ctx = dash.callback_context
    if not ctx.triggered: return (result, threshold_map)
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    try:
        if button_id == 'btn-change-id':
            if old_id is None or new_id is None: return ({'ok': False, 'message': 'ID 값을 입력하세요'}, threshold_map)
            cmd = f"SET_ID {int(old_id)} {int(new_id)}"
            ok = arduino.send_text_command(cmd)
            result = {'ok': ok, 'message': f'ID 변경: {old_id}→{new_id}'}
        elif button_id == 'btn-change-thresholds':
            if target_id is None or tl is None or th is None: return ({'ok': False, 'message': 'ID/TL/TH 입력 필요'}, threshold_map)
            cmd = f"SET_THRESHOLD {int(target_id)} {float(tl)} {float(th)}"
            ok = arduino.send_text_command(cmd)
            tm = dict(threshold_map or {})
            tm[str(int(target_id))] = {'TL': float(tl), 'TH': float(th)}
            result = {'ok': ok, 'message': f'임계값 설정: ID {target_id}, TL={tl}, TH={th}'}
            return (result, tm)
        elif button_id == 'btn-change-interval':
            if interval_ms is None: return ({'ok': False, 'message': '주기를 입력하세요'}, threshold_map)
            cmd = f"SET_INTERVAL {int(interval_ms)}"
            ok = arduino.send_text_command(cmd)
            result = {'ok': ok, 'message': f'주기 변경: {interval_ms}ms'}
    except Exception as e:
        result = {'ok': False, 'message': f'에러: {e}'}
    return (result, threshold_map)

# V2 Callbacks
@app.callback(
    Output('connect-port-btn-v2', 'children'),
    Input('connect-port-btn-v2', 'n_clicks'),
    State('port-dropdown-v2', 'value'),
    prevent_initial_call=True
)
def connect_to_selected_port_v2(n_clicks, selected):
    return connect_to_selected_port(n_clicks, selected)

@app.callback(
    Output('reconnect-btn-v2', 'children'),
    Input('reconnect-btn-v2', 'n_clicks')
)
def reconnect_arduino_v2(n_clicks):
    return reconnect_arduino(n_clicks)

@app.callback(
    Output('json-toggle-btn-v2', 'children'),
    Input('json-toggle-btn-v2', 'n_clicks')
)
def toggle_json_mode_v2(n_clicks):
    return toggle_json_mode(n_clicks)

@app.callback(
    Output('stats-btn-v2', 'children'),
    Input('stats-btn-v2', 'n_clicks')
)
def request_stats_v2(n_clicks):
    return request_stats(n_clicks)

# Unified callback for v2 port dropdown (now the ONLY callback touching these outputs)
@app.callback(
    [Output('port-dropdown-v2', 'options'),
     Output('port-dropdown-v2', 'value')],
    [Input('ui-version-store', 'data')],
    [State('port-dropdown-v2', 'value')],
    prevent_initial_call=True  # fire only when user switches to v2 the first time
)
def unified_refresh_v2_ports(ui_version, current_value):
    """Update v2 port dropdown ONLY when switching into v2.

    Avoids early startup race causing KeyError before callback map stabilizes.
    Interval-based refreshing can be reintroduced later if needed via a second callback.
    """
    if ui_version != 'v2':
        return dash.no_update, dash.no_update
    try:
        options, default_val = _get_initial_port_options()
        values_set = {o['value'] for o in options}
        value = current_value if current_value in values_set else default_val
        return options, value
    except Exception:
        return dash.no_update, dash.no_update

# NOTE: v2 포트 드롭다운 자동 새로고침 콜백 제거 (초기 렌더 순환 오류 방지). 필요시 안전한 조건 추가 후 재도입.
    
# Removed periodic refresh for v2 ports (caused early runtime errors before layout swap).
# Port list can still be updated via v1 controls or by switching modes; reintroduce if needed with safe guards.

def cleanup_resources():
    print("🔧 리소스 정리 중...")
    try:
        if arduino and hasattr(arduino, 'is_connected') and arduino.is_connected:
            arduino.disconnect()
            print("🔌 Arduino 연결 종료")
    except Exception as e:
        print(f"⚠️ Arduino 연결 해제 중 오류: {e}")
    try:
        import threading
        active_threads = threading.active_count()
        if active_threads > 1:
            print(f"⏳ 활성 스레드 {active_threads}개 종료 대기...")
            time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ 스레드 정리 중 오류: {e}")
    
    print("✅ 리소스 정리 완료")

# Debug: list registered callbacks at import time (initial attempt)
try:
    print("[DEBUG] Registered callback output keys (initial scan):")
    for k in app.callback_map.keys():
        print("  -", k)
    print(f"[DEBUG] Total callbacks registered: {len(app.callback_map)}")
except Exception as _e:
    print("[DEBUG] Failed to print callback_map keys (initial):", _e)

# Force a second scan after all decorators executed (in case ordering affected initial)
def _post_registration_audit():
    try:
        print("[DEBUG] Post-registration callback audit:")
        for k in app.callback_map.keys():
            print("  *", k)
        print(f"[DEBUG] Callback count: {len(app.callback_map)}")
    except Exception as e:
        print("[DEBUG] Callback audit failed:", e)
_post_registration_audit()

# --- Night mode per-sensor mini graph updater ---
@app.callback(
    [Output(f'sensor-{i}-mini-graph', 'figure') for i in range(1,9)],
    Input('interval-component', 'n_intervals'),
    State('ui-version-store', 'data'),
    prevent_initial_call=True
)
def update_v2_mini_graphs(_n, ui_version):
    # Only update when in v2; otherwise keep previous figures
    if ui_version != 'v2':
        return [dash.no_update]*8
    _, _, _current_temps, latest_data, _msgs = _snapshot()
    figures = []
    if latest_data:
        try:
            df = pd.DataFrame(latest_data)
            df['sensor_id'] = df['sensor_id'].astype(int)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        except Exception:
            # Fallback minimal frame
            df = pd.DataFrame(latest_data)
        ranges_debug = []
        for sid in range(1,9):
            sub = df[df['sensor_id']==sid]
            fig = go.Figure()
            if not sub.empty:
                x = sub['timestamp']
                y = sub['temperature']
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color=COLOR_SEQ[(sid-1)%len(COLOR_SEQ)], width=2)))
                try:
                    vmin = float(min(y)); vmax = float(max(y))
                    vmin = min(vmin, TL_DEFAULT); vmax = max(vmax, TH_DEFAULT)
                    if vmin == vmax:
                        vmin -= 0.5; vmax += 0.5
                    pad = (vmax - vmin) * 0.1
                    fig.update_yaxes(range=[vmin - pad, vmax + pad])
                    ranges_debug.append(f"{sid}:{vmin:.1f}-{vmax:.1f}")
                except Exception:
                    pass
                fig.update_xaxes(showgrid=False, tickfont=dict(color='#aaa'), nticks=3)
                fig.update_yaxes(showgrid=False, tickfont=dict(color='#aaa'), nticks=3)
                try:
                    fig.add_hline(y=TH_DEFAULT, line_dash='dash', line_color='red')
                    fig.add_hline(y=TL_DEFAULT, line_dash='dash', line_color='blue')
                except Exception:
                    pass
            else:
                fig.add_annotation(text='데이터 없음', showarrow=False, font=dict(color='white', size=10))
            fig.update_layout(
                template='plotly_dark',
                margin=dict(l=4, r=4, t=4, b=4),
                height=100,
                xaxis=dict(title=None),
                yaxis=dict(title=None),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            figures.append(fig)
        if ranges_debug:
            print("🌙 v2 mini graphs 갱신: " + ", ".join(ranges_debug))
    else:
        for sid in range(1,9):
            fig = go.Figure()
            fig.add_annotation(text='데이터 없음', showarrow=False, font=dict(color='white', size=10))
            fig.update_layout(template='plotly_dark', margin=dict(l=4, r=4, t=4, b=4), height=100,
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            figures.append(fig)
    return figures

# --- Per-sensor interval modal logic ---
def _format_interval(ms: int) -> str:
    if ms < 60000:
        return f"{int(ms/1000)}초"
    if ms < 3600000:
        return f"{int(ms/60000)}분"
    return f"{round(ms/3600000,1)}시간"

@app.callback(
    Output('interval-modal', 'style'),
    Output('interval-modal-target-sensor', 'data'),
    [Input(f'btn-change-interval-v2-{i}', 'n_clicks') for i in range(1,9)] + [Input('interval-cancel-btn','n_clicks')],
    State('interval-modal-target-sensor', 'data'),
    prevent_initial_call=True
)
def open_close_interval_modal(*args):
    *btn_clicks, cancel_clicks, current_target = args
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trig = ctx.triggered[0]['prop_id'].split('.')[0]
    if trig == 'interval-cancel-btn':
        return {'display':'none'}, None
    for idx, n in enumerate(btn_clicks, start=1):
        if trig == f'btn-change-interval-v2-{idx}' and n:
            return {'position': 'fixed', 'top':0,'left':0,'right':0,'bottom':0,'backgroundColor':'rgba(0,0,0,0.6)','display':'flex','alignItems':'center','justifyContent':'center','zIndex':2000}, idx
    return {'display':'none'}, None

@app.callback(
    Output('interval-selected-preview','children'),
    Input('interval-select','value'),
    State('interval-modal-target-sensor','data'),
    prevent_initial_call=True
)
def preview_interval(value, target):
    if value is None or target is None:
        return ""
    return f"센서 {target} 선택됨: {_format_interval(int(value))}"

@app.callback(
    Output('interval-confirm-dialog','displayed'),
    Output('pending-interval-selection','data'),
    Input('interval-apply-btn','n_clicks'),
    State('interval-select','value'),
    State('interval-modal-target-sensor','data'),
    prevent_initial_call=True
)
def trigger_confirm(n_apply, value, target):
    if not n_apply or value is None or target is None:
        raise dash.exceptions.PreventUpdate
    return True, {'sensor': target, 'interval_ms': int(value)}

@app.callback(
    Output('sensor-intervals-store','data'),
    Output('interval-modal','style'),
    Output('interval-confirm-dialog','displayed'),
    Input('interval-confirm-dialog','submit_n_clicks'),
    State('pending-interval-selection','data'),
    State('sensor-intervals-store','data'),
    prevent_initial_call=True
)
def apply_interval(submit_clicks, pending, intervals_map):
    if not submit_clicks or not pending:
        raise dash.exceptions.PreventUpdate
    intervals = dict(intervals_map or {})
    sensor = str(pending['sensor'])
    ms = int(pending['interval_ms'])
    intervals[sensor] = ms
    if ARDUINO_CONNECTED:
        try:
            cmd = f"SET_INTERVAL {sensor} {ms}"
            ok = arduino.send_text_command(cmd)
            print(f"🕒 센서 {sensor} 주기 설정 {ms}ms 전송 결과: {ok}")
        except Exception as e:
            print(f"주기 전송 오류: {e}")
    return intervals, {'display':'none'}, False

@app.callback(
    [Output(f'btn-change-interval-v2-{i}','children') for i in range(1,9)],
    Input('sensor-intervals-store','data')
)
def update_interval_button_labels(intervals_map):
    labels = []
    for i in range(1,9):
        ms = (intervals_map or {}).get(str(i), 1000)
        labels.append(f"측정주기 변경 (현재 {_format_interval(ms)})")
    return labels


if __name__ == '__main__':
    try:
        print("🚀 DS18B20 JSON 대시보드 시작")
        print("📡 Arduino 연결 상태:", "연결됨" if ARDUINO_CONNECTED else "연결 안됨")
        print("🌐 웹 인터페이스: http://127.0.0.1:8050")
        print("💡 Ctrl+C로 안전하게 종료하세요")

        app.run(debug=False, host='127.0.0.1', port=8050, 
                use_reloader=False, threaded=True)

    except KeyboardInterrupt:
        print("\n🛑 사용자가 애플리케이션을 종료했습니다")
    except SystemExit:
        pass
    except Exception as e:
        print(f"\n❌ 애플리케이션 오류: {e}")
    finally:
        cleanup_resources()