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
from night_sections.night_layout import create_layout_v2
from day_sections.day_layout import create_layout_v1
from day_sections.day_callbacks import register_day_callbacks
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
    +[Output('system-log','children')],
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
    return [connection_status, connection_style] + sensor_temps + sensor_statuses + [log_entries]

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

# create_layout_v2 함수는 night_layout.py로 이동됨
# create_layout_v1 함수는 day_sections/day_layout.py로 이동됨


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
    html.Div(id='main-content', children=create_layout_v1(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE)),
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
        html.Div(id='system-log'),
        dcc.Dropdown(id='port-dropdown'),
        dcc.Dropdown(id='port-dropdown-2'),
        dcc.Checklist(id='sensor-line-toggle'),
        html.Button(id='btn-select-all'),
        html.Button(id='btn-deselect-all'),
        html.Button(id='reconnect-btn'),
        html.Button(id='json-toggle-btn'),
        html.Button(id='stats-btn'),
        html.Button(id='connect-port-btn'),
        html.Button(id='connect-port-btn-2'),
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
        # v2 컴포넌트들 (validation용)
        html.Div(id='system-log-v2'),
        dcc.Dropdown(id='port-dropdown-v2'),
        html.Button(id='connect-port-btn-v2'),
        html.Button(id='reconnect-btn-v2'),
        html.Button(id='json-toggle-btn-v2'),
        html.Button(id='stats-btn-v2'),
        *[dcc.Graph(id=f'sensor-{i}-mini-graph') for i in range(1,9)],
        html.Div(id='interval-modal'),
        dcc.Dropdown(id='interval-select'),
        html.Button(id='interval-apply-btn'),
        html.Button(id='interval-cancel-btn'),
        dcc.ConfirmDialog(id='interval-confirm-dialog'),
        html.Div(id='interval-selected-preview'),
        *[html.Button(id=f'btn-change-interval-v2-{i}') for i in range(1,9)],
        *[html.Button(id=f'btn-change-id-v2-{i}') for i in range(1,9)],
        *[html.Button(id=f'btn-change-thresholds-v2-{i}') for i in range(1,9)],
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
        return create_layout_v2(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE, app, arduino, ARDUINO_CONNECTED, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot), 'v2'
    else: # btn-ver-1 or default
        if button_id == 'btn-ver-1':
            print("☀️ Day mode 버튼 클릭 - v1 레이아웃 전환")
        return create_layout_v1(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE), 'v1'



# Day mode 콜백들은 day_sections/day_callbacks.py로 이동됨

# V2 콜백들은 night_layout.py와 sections로 이동됨

# 콜백 등록
register_day_callbacks(app, arduino, {'connected': ARDUINO_CONNECTED}, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot)

# Night 콜백도 앱 시작 시 미리 등록
try:
    from night_sections.night_callbacks import register_night_callbacks
    register_night_callbacks(app, arduino, {'connected': ARDUINO_CONNECTED}, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot)
    print("✅ Night 콜백 사전 등록 완료")
except Exception as e:
    print(f"⚠️ Night 콜백 등록 실패: {e}")

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

# Night mode 미니 그래프 및 모달 콜백들은 sections로 이동됨


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