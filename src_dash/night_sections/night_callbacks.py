"""Night Mode (v2) 콜백 함수들"""
import dash
from dash import Input, Output, State, dcc, html
import plotly.graph_objects as go
import pandas as pd


def register_night_callbacks(app, arduino, arduino_connected_ref, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot):
    """Night mode 관련 콜백들을 등록"""
    
    # V2 제어 버튼 콜백들
    @app.callback(
        Output('connect-port-btn-v2', 'children'),
        Input('connect-port-btn-v2', 'n_clicks'),
        State('port-dropdown-v2', 'value'),
        prevent_initial_call=True
    )
    def connect_to_selected_port_v2(n_clicks, selected):
        # 기존 connect_to_selected_port 로직 재사용
        if not n_clicks: return "선택 포트로 연결"
        if not selected: return "❌ 포트 선택 필요"
        try:
            try:
                arduino.disconnect()
                import time
                time.sleep(0.5)
            except Exception: pass
            arduino.port = selected
            if arduino.connect():
                if arduino.start_reading():
                    print(f"✅ Night 모드 Arduino 연결 성공: {selected}")
                    return f"✅ 연결됨: {selected}"
            return "❌ 연결 실패"
        except Exception as e:
            return f"❌ 오류: {str(e)[:20]}..."

    @app.callback(
        Output('reconnect-btn-v2', 'children'),
        Input('reconnect-btn-v2', 'n_clicks')
    )
    def reconnect_arduino_v2(n_clicks):
        if n_clicks > 0:
            print("🔄 Night 모드 수동 재연결 시도...")
            try:
                arduino.disconnect()
                import time
                time.sleep(1)
            except Exception as e:
                print(f"연결 해제 중 오류: {e}")
            try:
                if arduino.connect():
                    if arduino.start_reading():
                        print("✅ Night 모드 수동 재연결 성공!")
                        return "✅ 재연결 성공"
                    else:
                        arduino.disconnect()
                        return "❌ 데이터 읽기 실패"
                else:
                    return "❌ 연결 실패"
            except PermissionError:
                return "❌ 포트 접근 거부"
            except Exception as e:
                return f"❌ 오류: {str(e)[:15]}..."
        return "Arduino 재연결"

    @app.callback(
        Output('json-toggle-btn-v2', 'children'),
        Input('json-toggle-btn-v2', 'n_clicks')
    )
    def toggle_json_mode_v2(n_clicks):
        if n_clicks > 0 and arduino.is_healthy():
            command = {"type": "config", "action": "toggle_json_mode"}
            if arduino.send_command(command):
                return "📡 JSON 토글 전송됨"
            return "❌ 명령 전송 실패"
        return "JSON 모드 토글"

    @app.callback(
        Output('stats-btn-v2', 'children'),
        Input('stats-btn-v2', 'n_clicks')
    )
    def request_stats_v2(n_clicks):
        if n_clicks > 0 and arduino.is_healthy():
            command = {"type": "request", "action": "get_stats"}
            if arduino.send_command(command):
                return "📊 통계 요청됨"
            return "❌ 요청 실패"
        return "통계 요청"

    # V2 시스템 로그 업데이트 콜백
    @app.callback(
        Output('system-log-v2', 'children'),
        Input('interval-component', 'n_intervals'),
        State('ui-version-store', 'data'),
        prevent_initial_call=True
    )
    def update_system_log_v2(_n, ui_version):
        if ui_version != 'v2':
            return dash.no_update
        _, _, _current_temps, _latest_data, system_messages = _snapshot()
        log_entries = []
        for msg in system_messages:
            ts = msg['timestamp'].strftime('%H:%M:%S')
            level_icons = {"info":"ℹ️","warning":"⚠️","error":"❌"}
            icon = level_icons.get(msg['level'],'📝')
            log_entries.append(html.Div(f"[{ts}] {icon} {msg['message']}", style={'color': 'white', 'marginBottom': '2px'}))
        return log_entries

    # V2 포트 드롭다운 콜백
    @app.callback(
        [Output('port-dropdown-v2', 'options'),
         Output('port-dropdown-v2', 'value')],
        [Input('ui-version-store', 'data')],
        [State('port-dropdown-v2', 'value')],
        prevent_initial_call=True
    )
    def unified_refresh_v2_ports(ui_version, current_value):
        if ui_version != 'v2':
            return dash.no_update, dash.no_update
        try:
            from core.port_manager import find_arduino_port
            try:
                from serial.tools import list_ports
            except Exception:
                list_ports = None
                
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
                
            values_set = {o['value'] for o in options}
            value = current_value if current_value in values_set else default_val
            return options, value
        except Exception:
            return dash.no_update, dash.no_update

    # 미니 그래프 업데이트 콜백
    @app.callback(
        [Output(f'sensor-{i}-mini-graph', 'figure') for i in range(1,9)],
        Input('interval-component', 'n_intervals'),
        State('ui-version-store', 'data'),
        prevent_initial_call=True
    )
    def update_v2_mini_graphs(_n, ui_version):
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
                    # 시간 축을 시:분:초만 표시 (연/월/일 제거)
                    fig.update_xaxes(
                        showgrid=False,
                        tickfont=dict(color='#aaa'),
                        nticks=4,
                        tickformat="%H:%M:%S",
                        ticklabelposition="outside bottom",
                        ticklabelstandoff=10
                    )
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
                    margin=dict(l=4, r=4, t=16, b=14),
                    height=170,
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
                fig.update_layout(template='plotly_dark', margin=dict(l=4, r=4, t=16, b=14), height=170,
                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                figures.append(fig)
        return figures

    # 모달 관련 콜백들
    def _format_interval(ms: int) -> str:
        if ms < 60000:
            return f"{int(ms/1000)}초"
        if ms < 3600000:
            return f"{int(ms/60000)}분"
        return f"{round(ms/3600000,1)}시간"

    @app.callback(
        Output('interval-modal', 'style'),
        Output('interval-modal-target-sensor', 'data'),
        [Input(f'btn-change-interval-v2-{i}', 'n_clicks') for i in range(1,9)] + [Input('interval-cancel-btn','n_clicks')] + [Input('interval-confirm-dialog', 'submit_n_clicks')],
        State('interval-modal-target-sensor', 'data'),
        prevent_initial_call=True
    )
    def open_close_interval_modal(*args):
        *btn_clicks, cancel_clicks, submit_clicks, current_target = args
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        trig = ctx.triggered[0]['prop_id'].split('.')[0]
        if trig == 'interval-cancel-btn' or trig == 'interval-confirm-dialog':
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
        Output('pending-interval-selection','data'),
        Input('interval-apply-btn','n_clicks'),
        State('interval-select','value'),
        State('interval-modal-target-sensor','data'),
        prevent_initial_call=True
    )
    def trigger_confirm(n_apply, value, target):
        if not n_apply or value is None or target is None:
            raise dash.exceptions.PreventUpdate
        return {'sensor': target, 'interval_ms': int(value), 'show_dialog': True}

    @app.callback(
        Output('sensor-intervals-store','data'),
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
        if arduino.is_healthy():
            try:
                cmd = f"SET_INTERVAL {sensor} {ms}"
                ok = arduino.send_text_command(cmd)
                print(f"🕒 센서 {sensor} 주기 설정 {ms}ms 전송 결과: {ok}")
            except Exception as e:
                print(f"주기 전송 오류: {e}")
        return intervals, False

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