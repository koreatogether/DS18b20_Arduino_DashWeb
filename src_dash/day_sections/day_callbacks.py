"""Day Mode (v1) 콜백 함수들"""
import dash
from dash import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time


def register_day_callbacks(app, arduino, arduino_connected_ref, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot):
    """Day mode 관련 콜백들을 등록"""
    
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
        if n_clicks > 0:
            print("🔄 Day 모드 수동 재연결 시도...")
            try:
                arduino.disconnect()
                time.sleep(1)
            except Exception as e:
                print(f"연결 해제 중 오류: {e}")
            try:
                if arduino.connect():
                    if arduino.start_reading():
                        print("✅ Day 모드 수동 재연결 성공!")
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
        Output('json-toggle-btn', 'children'),
        [Input('json-toggle-btn', 'n_clicks')]
    )
    def toggle_json_mode(n_clicks):
        if n_clicks > 0 and arduino.is_healthy():
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
        if n_clicks > 0 and arduino.is_healthy():
            command = {"type": "request", "action": "get_stats"}
            if arduino.send_command(command):
                return "📊 통계 요청됨"
            return "❌ 요청 실패"
        return "통계 요청"

    @app.callback(
        [Output('port-dropdown', 'options'),
         Output('port-dropdown', 'value')],
        [Input('interval-component', 'n_intervals')],
        [State('port-dropdown', 'value')],
        prevent_initial_call=True
    )
    def refresh_port_options(_n, current_value):
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

    @app.callback(
        Output('connect-port-btn', 'children'),
        Input('connect-port-btn', 'n_clicks'),
        State('port-dropdown', 'value'),
        prevent_initial_call=True
    )
    def connect_to_selected_port(n_clicks, selected):
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
                    print(f"✅ Day 모드 Arduino 연결 성공: {selected}")
                    return f"✅ 연결됨: {selected}"
            return "❌ 연결 실패"
        except Exception as e:
            return f"❌ 오류: {str(e)[:20]}..."


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
        if not arduino.is_healthy():
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