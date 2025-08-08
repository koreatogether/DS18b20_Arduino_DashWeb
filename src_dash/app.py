"""
DS18B20 Arduino 연계 데스크탑 프로그램 메인 파일
JSON 기반 시리얼 통신을 사용하는 실시간 Dash 웹 애플리케이션
"""
import datetime
import random
import sys
import threading
import time
import os

import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from serial_json_communication import ArduinoJSONSerial
from port_manager import find_arduino_port
try:
    from serial.tools import list_ports
except Exception:
    list_ports = None

# Dash 앱 초기화
app = dash.Dash(
    __name__,
    prevent_initial_callbacks=True,  # 초기 로드 시 콜백 발화 방지 (하이드레이션 레이스 컨디션 예방)
)

# 콘솔 인코딩 안전 설정 (Windows cp949 환경에서 이모지로 인한 UnicodeEncodeError 방지)
def _configure_console_encoding():
    try:
        # 환경 변수를 통해 하위 프로세스/도구에도 영향
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        # 직접 스트림 재설정
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

_configure_console_encoding()

# 초기 포트 옵션 계산 (초기 렌더에서 드롭다운이 공백이 되지 않도록 선반영)
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

# 콘솔 상호작용 프롬프트는 제거되었습니다. 포트 선택은 웹 UI에서 처리합니다.

# Arduino 시리얼 통신 초기화 (포트 자동 감지 + 사용자 선택 지원)
detected_port = find_arduino_port()
selected_port = detected_port
SKIP_CONNECT = False
if detected_port:
    print(f"✅ Arduino 포트 자동 감지: {detected_port}")
else:
    print("⚠️ Arduino 포트 자동 감지 실패: 웹 UI에서 포트를 선택해 연결하세요 (시뮬레이션 모드로 시작)")
    SKIP_CONNECT = True

arduino = ArduinoJSONSerial(port=selected_port or 'COM4', baudrate=115200)
ARDUINO_CONNECTED = False

# 앱 시작 시 Arduino 연결 시도 (개선된 연결 로직)
def try_arduino_connection(max_attempts=3):
    """Arduino 연결을 여러 번 시도하는 함수"""
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
    
    print("❌ 모든 연결 시도 실패 - 시뮬레이션 모드로 실행")
    return False

# Arduino 연결 시도
if not SKIP_CONNECT:
    try_arduino_connection()
else:
    print("연결 시도 건너뜀 (시뮬레이션 모드)")

# 기본 레이아웃 정의
app.layout = html.Div([
    html.H1("DS18B20 센서 데이터 대시보드 (JSON 통신)",
            style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.Div(
        f"UI Build: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '12px', 'marginBottom': '6px'}
    ),

    # 연결 상태 표시
    html.Div([
        html.Div(id='connection-status',
                 style={'textAlign': 'center', 'margin': '10px',
                        'padding': '10px', 'border': '2px solid',
                        'borderRadius': '5px'}),
        # 포트 선택 및 연결 컨트롤
        html.Div([
            html.H3('포트 연결', style={'margin': '4px 0'}),
            html.Span('포트 선택: ', style={'marginRight': '6px'}),
            dcc.Dropdown(
                id='port-dropdown',
                options=INITIAL_PORT_OPTIONS,
                value=selected_port or INITIAL_PORT_VALUE,
                         placeholder='자동 감지 또는 포트 선택',
                         style={'display': 'inline-block', 'width': '260px', 'marginRight': '8px'}),
            html.Button('선택 포트로 연결', id='connect-port-btn', n_clicks=0,
                        style={'display': 'inline-block'})
        ], style={'textAlign': 'center', 'marginTop': '8px'})
    ]),

    html.Hr(),

    # 상단: 센서 카드 + 우측 세로 제어 패널
    html.Div([
        html.Div([
            html.H3("센서 상태", style={'textAlign': 'center'}),
            html.Div(id='sensor-cards', children=[
                html.Div([
                    html.H4(f"센서 {i}", style={'margin': '5px'}),
                    html.Div(id=f'sensor-{i}-temp', children="--°C",
                             style={'fontSize': '24px', 'fontWeight': 'bold'}),
                    html.Div(id=f'sensor-{i}-status', children="연결 대기",
                             style={'fontSize': '12px', 'color': '#666'})
                ], style={'display': 'inline-block', 'margin': '10px',
                          'padding': '15px', 'border': '1px solid #ddd',
                          'borderRadius': '5px', 'width': '150px',
                          'textAlign': 'center', 'backgroundColor': '#f9f9f9'})
                for i in range(1, 9)
            ])
    ], style={'flex': '1', 'minWidth': '340px'}),

        # 우측 세로 제어 패널 (포트 연결 + 3개 버튼)
        html.Div([
            html.H3("빠른 설정", style={'textAlign': 'center'}),

            # 사이드바 포트 연결 컨트롤 (중복 배치로 접근성 향상)
            html.Div([
                html.Label('포트 선택', style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='port-dropdown-2',
                    options=INITIAL_PORT_OPTIONS,
                    value=selected_port or INITIAL_PORT_VALUE,
                             placeholder='포트 선택',
                             style={'width': '100%', 'marginBottom': '6px'}),
                html.Button('선택 포트로 연결', id='connect-port-btn-2', n_clicks=0,
                            style={'width': '100%', 'marginBottom': '16px'})
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Button('ID 변경', id='btn-change-id', n_clicks=0,
                            style={'width': '100%', 'marginBottom': '10px'}),
                dcc.Input(id='input-old-id', type='number', placeholder='현재 ID', min=1, max=64,
                          style={'width': '48%', 'marginRight': '4%'}),
                dcc.Input(id='input-new-id', type='number', placeholder='새 ID', min=1, max=64,
                          style={'width': '48%'}),
            ], style={'marginBottom': '15px'}),

            html.Div([
                html.Button('임계값 변경 (TL/TH)', id='btn-change-thresholds', n_clicks=0,
                            style={'width': '100%', 'marginBottom': '10px'}),
                dcc.Input(id='input-target-id', type='number', placeholder='센서 ID', min=1, max=64,
                          style={'width': '100%', 'marginBottom': '6px'}),
                dcc.Input(id='input-tl', type='number', placeholder='TL 하한(°C)', step=0.5,
                          style={'width': '48%', 'marginRight': '4%'}),
                dcc.Input(id='input-th', type='number', placeholder='TH 상한(°C)', step=0.5,
                          style={'width': '48%'}),
            ], style={'marginBottom': '15px'}),

            html.Div([
                html.Button('측정 주기 변경', id='btn-change-interval', n_clicks=0,
                            style={'width': '100%', 'marginBottom': '10px'}),
                dcc.Input(id='input-interval', type='number', placeholder='주기(ms)', min=100, step=100,
                          style={'width': '100%'}),
            ]),
        ], style={'width': '280px', 'marginLeft': '20px', 'padding': '10px',
                  'border': '1px solid #ddd', 'borderRadius': '8px', 'height': '100%'}),
    ], style={'display': 'flex', 'alignItems': 'flex-start', 'flexWrap': 'wrap'}),

    html.Hr(),

    # 온도 그래프 (전체 + 센서별 상세)
    html.Div([
        dcc.Graph(id='temp-graph'),
        html.Div([
            html.Div([
                html.Label('상세 그래프 센서 선택'),
                dcc.Dropdown(id='detail-sensor-dropdown', options=[
                    {'label': f'센서 {i}', 'value': i} for i in range(1, 65)
                ], value=1, clearable=False, style={'width': '200px'}),
            ], style={'marginBottom': '10px'}),
            dcc.Graph(id='detail-sensor-graph')
        ], style={'marginTop': '20px'})
    ], style={'margin': '20px'}),

    # 제어 패널
    html.Div([
        html.H3("제어 패널"),
        html.Button('Arduino 재연결', id='reconnect-btn', n_clicks=0,
                    style={'margin': '5px', 'padding': '10px'}),
        html.Button('JSON 모드 토글', id='json-toggle-btn', n_clicks=0,
                    style={'margin': '5px', 'padding': '10px'}),
        html.Button('통계 요청', id='stats-btn', n_clicks=0,
                    style={'margin': '5px', 'padding': '10px'}),
    ], style={'margin': '20px', 'padding': '15px',
              'backgroundColor': '#f0f0f0', 'borderRadius': '5px'}),

    # 시스템 메시지 및 알림
    html.Div([
        html.H3("시스템 로그"),
        html.Div(id='system-log',
                 style={'height': '200px', 'overflow': 'auto',
                        'border': '1px solid #ddd', 'padding': '10px',
                        'backgroundColor': '#f8f8f8',
                        'fontFamily': 'monospace'})
    ], style={'margin': '20px'}),

    # 자동 갱신 컴포넌트
    dcc.Interval(
        id='interval-component',
        interval=1000,  # 1초마다 갱신
        n_intervals=0
    ),

    # 데이터 저장소
    dcc.Store(id='sensor-data-store'),
    dcc.Store(id='threshold-store', data={}),
    dcc.Store(id='last-command-result'),
    dcc.Store(id='port-options-cache')
])

# 실시간 데이터 업데이트 콜백
@callback(
    [Output('connection-status', 'children'),
     Output('connection-status', 'style'),
     Output('temp-graph', 'figure'),
     Output('system-log', 'children'),
     Output('detail-sensor-graph', 'figure')] +
    [Output(f'sensor-{i}-temp', 'children') for i in range(1, 9)] +
    [Output(f'sensor-{i}-status', 'children') for i in range(1, 9)],
    [Input('interval-component', 'n_intervals'),
     Input('detail-sensor-dropdown', 'value'),
     State('threshold-store', 'data')]
)
def update_dashboard(n_intervals, detail_sensor_id, threshold_map):
    """
    대시보드의 모든 컴포넌트를 실시간으로 업데이트하는 함수.

    Args:
        n_intervals: 인터벌 컴포넌트의 실행 횟수

    Returns:
        tuple: 연결 상태, 스타일, 그래프, 로그, 센서 온도들, 센서 상태들
    """
    global ARDUINO_CONNECTED
    
    # 연결 상태 확인 (개선된 상태 체크)
    global ARDUINO_CONNECTED
    
    # Arduino 연결 상태 재확인
    if ARDUINO_CONNECTED:
        if not arduino.is_healthy():
            ARDUINO_CONNECTED = False
            print("⚠️ Arduino 연결 상태 불량 감지 - 시뮬레이션 모드 전환")
    
    if ARDUINO_CONNECTED and arduino.is_healthy():
        # 연결 통계 정보 가져오기
        stats = arduino.get_connection_stats()
        connection_status = f"🟢 Arduino 연결됨 (데이터: {stats['sensor_data_count']}개)"
        connection_style = {
            'textAlign': 'center', 'margin': '10px', 'padding': '10px',
            'border': '2px solid green', 'borderRadius': '5px',
            'color': 'green'
        }

        # 실제 Arduino 데이터 사용
        current_temps = arduino.get_current_temperatures()
        latest_data = arduino.get_latest_sensor_data(count=50)
        system_messages = arduino.get_system_messages(count=10)
        
        # 디버그: 실제 데이터 확인
        print(f"🔍 실제 데이터 사용: 현재온도={len(current_temps)}개, 최신데이터={len(latest_data)}개")

    else:
        connection_status = "🔴 Arduino 연결 끊김 (시뮬레이션 모드)"
        connection_style = {
            'textAlign': 'center', 'margin': '10px', 'padding': '10px',
            'border': '2px solid red', 'borderRadius': '5px',
            'color': 'red'
        }

        # 시뮬레이션 데이터 사용
        current_temps = {
            i: {
                'temperature': round(20 + random.uniform(-5, 15), 1),
                'status': 'simulated'
            } for i in range(1, 5)
        }

        # 시뮬레이션 그래프 데이터
        times = [
            datetime.datetime.now() - datetime.timedelta(seconds=i)
            for i in range(30, 0, -1)
        ]
        latest_data = []
        for time in times:
            for sensor_id in range(1, 5):
                latest_data.append({
                    'timestamp': time,
                    'sensor_id': sensor_id,
                    'temperature': 20 + random.uniform(-5, 15)
                })

        system_messages = [{
            'timestamp': datetime.datetime.now(),
            'message': 'Simulation mode active',
            'level': 'warning'
        }]
    
    # 그래프 생성 (전체)
    if latest_data:
        df = pd.DataFrame(latest_data)
        # 타입 안전화: 타임스탬프/센서ID 정규화
        try:
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            if 'sensor_id' in df.columns:
                df['sensor_id'] = df['sensor_id'].astype(str)
        except Exception:
            pass
        # 안전한 라인 그래프 생성 시도
        try:
            fig = px.line(
                df, x='timestamp', y='temperature', color='sensor_id',
                title='실시간 온도 모니터링 (최근 50개 데이터)',
                labels={'temperature': '온도 (°C)', 'timestamp': '시간'},
                template='plotly_white'
            )
        except Exception:
            # Fallback: go.Figure로 직접 구성
            fig = go.Figure()
            for sid, g in df.groupby('sensor_id'):
                fig.add_trace(go.Scatter(x=g['timestamp'], y=g['temperature'],
                                         mode='lines', name=str(sid)))
            fig.update_layout(title='실시간 온도 모니터링 (최근 50개 데이터)',
                              xaxis_title='시간', yaxis_title='온도 (°C)',
                              template='plotly_white', legend_title='센서 ID')
        # 동적 자동 스케일링: 극단값 보호 (예: 200°C)
        try:
            ymin = max(-40, float(df['temperature'].min()) - 2)
            ymax = min(200, float(df['temperature'].max()) + 2)
            if ymin < ymax:
                fig.update_yaxes(range=[ymin, ymax])
        except Exception:
            pass
    else:
        fig = px.line(title="데이터 없음")

    # 상세 그래프 (선택 센서 + 임계선 표시)
    if latest_data:
        df_all = pd.DataFrame(latest_data)
        try:
            df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
            df_all['sensor_id'] = df_all['sensor_id'].astype(int)
        except Exception:
            pass
        df_one = df_all[df_all['sensor_id'] == detail_sensor_id]
        if not df_one.empty:
            try:
                detail_fig = px.line(
                    df_one, x='timestamp', y='temperature',
                    title=f'센서 {detail_sensor_id} 상세 그래프',
                    template='plotly_white'
                )
            except Exception:
                detail_fig = go.Figure()
                detail_fig.add_trace(go.Scatter(x=df_one['timestamp'], y=df_one['temperature'],
                                                mode='lines', name=f'센서 {detail_sensor_id}'))
                detail_fig.update_layout(title=f'센서 {detail_sensor_id} 상세 그래프',
                                         xaxis_title='시간', yaxis_title='온도 (°C)',
                                         template='plotly_white')
            # 임계값 점선 추가
            tl = None
            th = None
            if isinstance(threshold_map, dict):
                sid = str(detail_sensor_id)
                if sid in threshold_map:
                    tl = threshold_map[sid].get('TL')
                    th = threshold_map[sid].get('TH')
            shapes = []
            if tl is not None:
                shapes.append({
                    'type': 'line', 'xref': 'paper', 'x0': 0, 'x1': 1,
                    'yref': 'y', 'y0': tl, 'y1': tl,
                    'line': {'color': 'dodgerblue', 'width': 1, 'dash': 'dot'}
                })
            if th is not None:
                shapes.append({
                    'type': 'line', 'xref': 'paper', 'x0': 0, 'x1': 1,
                    'yref': 'y', 'y0': th, 'y1': th,
                    'line': {'color': 'tomato', 'width': 1, 'dash': 'dot'}
                })
            if shapes:
                detail_fig.update_layout(shapes=shapes)
            # 동적 스케일링
            try:
                ymin = max(-40, float(df_one['temperature'].min()) - 2)
                ymax = min(200, float(df_one['temperature'].max()) + 2)
                # 임계 포함 범위 확장
                if tl is not None:
                    ymin = min(ymin, tl - 2)
                if th is not None:
                    ymax = max(ymax, th + 2)
                if ymin < ymax:
                    detail_fig.update_yaxes(range=[ymin, ymax])
            except Exception:
                pass
        else:
            detail_fig = px.line(title=f"센서 {detail_sensor_id} 데이터 없음")
    else:
        detail_fig = px.line(title="상세 데이터 없음")

    # 센서별 온도 및 상태 업데이트
    sensor_temps = []
    sensor_statuses = []

    for i in range(1, 9):
        if i in current_temps:
            temp_info = current_temps[i]
            sensor_temps.append(f"{temp_info['temperature']:.1f}°C")

            if temp_info['status'] == 'ok':
                sensor_statuses.append("🟢 정상")
            elif temp_info['status'] == 'simulated':
                sensor_statuses.append("🟡 시뮬레이션")
            else:
                sensor_statuses.append(f"⚠️ {temp_info['status']}")
        else:
            sensor_temps.append("--°C")
            sensor_statuses.append("🔴 연결 없음")

    # 시스템 로그 생성
    log_entries = []
    for msg in system_messages:
        timestamp_str = msg['timestamp'].strftime("%H:%M:%S")
        level_icons = {
            "info": "ℹ️", "warning": "⚠️", "error": "❌"
        }
        level_icon = level_icons.get(msg['level'], "📝")
        log_entries.append(
            html.Div(f"[{timestamp_str}] {level_icon} {msg['message']}")
        )

    return ([connection_status, connection_style, fig, log_entries, detail_fig] +
            sensor_temps + sensor_statuses)

# 제어 버튼 콜백들
@callback(
    Output('reconnect-btn', 'children'),
    [Input('reconnect-btn', 'n_clicks')]
)
def reconnect_arduino(n_clicks):
    """
    Arduino 재연결 버튼 콜백 함수 (개선된 재연결 로직).

    Args:
        n_clicks: 버튼 클릭 횟수

    Returns:
        str: 버튼에 표시할 텍스트
    """
    global ARDUINO_CONNECTED
    if n_clicks > 0:
        print("🔄 수동 재연결 시도...")
        
        # 기존 연결 정리
        try:
            arduino.disconnect()
            time.sleep(1)  # 포트 해제 대기
        except Exception as e:
            print(f"연결 해제 중 오류: {e}")
        
        # 재연결 시도
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

@callback(
    Output('json-toggle-btn', 'children'),
    [Input('json-toggle-btn', 'n_clicks')]
)
def toggle_json_mode(n_clicks):
    """
    JSON 모드 토글 버튼 콜백 함수.

    Args:
        n_clicks: 버튼 클릭 횟수

    Returns:
        str: 버튼에 표시할 텍스트
    """
    if n_clicks > 0 and ARDUINO_CONNECTED:
        # Arduino에 JSON 모드 토글 명령 전송
        command = {"type": "config", "action": "toggle_json_mode"}
        if arduino.send_command(command):
            return "📡 JSON 토글 전송됨"
        return "❌ 명령 전송 실패"
    return "JSON 모드 토글"

@callback(
    Output('stats-btn', 'children'),
    [Input('stats-btn', 'n_clicks')]
)
def request_stats(n_clicks):
    """
    통계 요청 버튼 콜백 함수.

    Args:
        n_clicks: 버튼 클릭 횟수

    Returns:
        str: 버튼에 표시할 텍스트
    """
    if n_clicks > 0 and ARDUINO_CONNECTED:
        # Arduino에 통계 요청 명령 전송
        command = {"type": "request", "action": "get_stats"}
        if arduino.send_command(command):
            return "📊 통계 요청됨"
        return "❌ 요청 실패"
    return "통계 요청"

# 포트 목록 갱신 (주기적으로 옵션을 업데이트하고, 현재 선택이 없으면 자동 선택)
# 포트 목록 갱신 (주기적으로 옵션을 업데이트하고, 현재 선택이 없으면 자동 선택)
@callback(
    [Output('port-dropdown', 'options'),
     Output('port-dropdown', 'value'),
     Output('port-dropdown-2', 'options'),
     Output('port-dropdown-2', 'value')],
    [Input('interval-component', 'n_intervals')],
    [State('port-dropdown', 'value'),
    State('port-dropdown-2', 'value')],
    prevent_initial_call=True  # 초기 로드 직후 불필요한 트리거 방지
)
def refresh_port_options(_n, current_value_1, current_value_2):
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
        # 감지 실패 시 기본 COM 후보를 제공 (가시성 확보)
        if not options:
            options = [{'label': f'COM{i}', 'value': f'COM{i}'} for i in range(1, 11)]
            default_val = 'COM4'
        # 유지: 현재 값이 여전히 유효하면 그대로
        values_set = {o['value'] for o in options}
        value1 = current_value_1 if current_value_1 in values_set else default_val
        value2 = current_value_2 if current_value_2 in values_set else value1
        return options, value1, options, value2
    except Exception:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# 선택 포트로 연결 시도
@callback(
    Output('connect-port-btn', 'children'),
    Input('connect-port-btn', 'n_clicks'),
    State('port-dropdown', 'value'),
    prevent_initial_call=True
)
def connect_to_selected_port(n_clicks, selected):
    global ARDUINO_CONNECTED
    if not n_clicks:
        return "선택 포트로 연결"
    if not selected:
        return "❌ 포트 선택 필요"
    try:
        # 기존 연결 정리 및 포트 변경
        try:
            arduino.disconnect()
            time.sleep(0.5)
        except Exception:
            pass
        # 대상 포트로 설정 후 연결
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

# 사이드바 버튼도 동일 동작
@callback(
    Output('connect-port-btn-2', 'children'),
    Input('connect-port-btn-2', 'n_clicks'),
    State('port-dropdown-2', 'value'),
    prevent_initial_call=True
)
def connect_to_selected_port_sidebar(n_clicks, selected):
    return connect_to_selected_port(n_clicks, selected)

# 통합 명령 콜백: ID/임계값/주기 변경
@callback(
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

    # 현재 클릭된 버튼 검사
    ctx = dash.callback_context
    if not ctx.triggered:
        return (result, threshold_map)
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    try:
        if button_id == 'btn-change-id':
            if old_id is None or new_id is None:
                return ({'ok': False, 'message': 'ID 값을 입력하세요'}, threshold_map)
            cmd = f"SET_ID {int(old_id)} {int(new_id)}"
            ok = arduino.send_text_command(cmd)
            result = {'ok': ok, 'message': f'ID 변경: {old_id}→{new_id}'}

        elif button_id == 'btn-change-thresholds':
            if target_id is None or tl is None or th is None:
                return ({'ok': False, 'message': 'ID/TL/TH 입력 필요'}, threshold_map)
            cmd = f"SET_THRESHOLD {int(target_id)} {float(tl)} {float(th)}"
            ok = arduino.send_text_command(cmd)
            # 로컬 threshold 저장/업데이트
            tm = dict(threshold_map or {})
            tm[str(int(target_id))] = {'TL': float(tl), 'TH': float(th)}
            result = {'ok': ok, 'message': f'임계값 설정: ID {target_id}, TL={tl}, TH={th}'}
            return (result, tm)

        elif button_id == 'btn-change-interval':
            if interval_ms is None:
                return ({'ok': False, 'message': '주기를 입력하세요'}, threshold_map)
            cmd = f"SET_INTERVAL {int(interval_ms)}"
            ok = arduino.send_text_command(cmd)
            result = {'ok': ok, 'message': f'주기 변경: {interval_ms}ms'}

    except Exception as e:
        result = {'ok': False, 'message': f'에러: {e}'}

    return (result, threshold_map)

def cleanup_resources():
    """리소스 정리 함수"""
    print("🔧 리소스 정리 중...")
    
    # Arduino 연결 안전하게 종료
    try:
        if arduino and hasattr(arduino, 'is_connected') and arduino.is_connected:
            arduino.disconnect()
            print("🔌 Arduino 연결 종료")
    except Exception as e:
        print(f"⚠️ Arduino 연결 해제 중 오류: {e}")
    
    # 스레드 정리 대기
    try:
        import threading
        active_threads = threading.active_count()
        if active_threads > 1:
            print(f"⏳ 활성 스레드 {active_threads}개 종료 대기...")
            time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ 스레드 정리 중 오류: {e}")
    
    print("✅ 리소스 정리 완료")


if __name__ == '__main__':
    try:
        print("🚀 DS18B20 JSON 대시보드 시작")
        print("📡 Arduino 연결 상태:",
              "연결됨" if ARDUINO_CONNECTED else "연결 안됨")
        print("🌐 웹 인터페이스: http://127.0.0.1:8050")
        print("💡 Ctrl+C로 안전하게 종료하세요")

        # debug=False로 설정하여 스레드 문제 방지
        app.run(debug=False, host='127.0.0.1', port=8050, 
                use_reloader=False, threaded=True)

    except KeyboardInterrupt:
        print("\n🛑 사용자가 애플리케이션을 종료했습니다")
    except SystemExit:
        pass  # 정상 종료
    except Exception as e:
        print(f"\n❌ 애플리케이션 오류: {e}")
    finally:
        cleanup_resources()
