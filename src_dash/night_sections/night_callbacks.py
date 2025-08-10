"""Night Mode (v2) 콜백 함수들"""

import dash
import pandas as pd
from core.ui_modes import UIMode
from dash import Input, Output, State, html

from .connection_utils import (
    attempt_arduino_connection,
    attempt_data_reading,
    create_fallback_port_options,
    get_port_options_safely,
    safe_disconnect_arduino,
)
from .mini_graph_utils import create_empty_mini_graph, create_sensor_mini_graph, prepare_dataframe


def register_night_callbacks(
    app, arduino, arduino_connected_ref, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot
):
    """Night mode 관련 콜백들을 등록"""

    # V2 제어 버튼 콜백들
    @app.callback(
        Output("connect-port-btn-v2", "children"),
        Input("connect-port-btn-v2", "n_clicks"),
        State("port-dropdown-v2", "value"),
        prevent_initial_call=True,
    )
    def connect_to_selected_port_v2(n_clicks, selected):
        """선택된 포트로 Arduino에 연결합니다."""
        if not n_clicks:
            return "선택 포트로 연결"
        if not selected:
            return "❌ 포트 선택 필요"

        try:
            # 기존 연결 안전하게 해제
            safe_disconnect_arduino(arduino)

            # 새 포트로 연결 시도
            if attempt_arduino_connection(arduino, selected):
                if attempt_data_reading(arduino):
                    print(f"✅ Night 모드 Arduino 연결 성공: {selected}")
                    return f"✅ 연결됨: {selected}"

            return "❌ 연결 실패"
        except (OSError, AttributeError, ValueError) as e:
            return f"❌ 오류: {str(e)[:20]}..."

    @app.callback(Output("reconnect-btn-v2", "children"), Input("reconnect-btn-v2", "n_clicks"))
    def reconnect_arduino_v2(n_clicks):
        """Arduino를 재연결합니다."""
        if n_clicks <= 0:
            return "Arduino 재연결"

        print("🔄 Night 모드 수동 재연결 시도...")

        try:
            # 기존 연결 해제 (더 긴 대기 시간)
            try:
                arduino.disconnect()
                import time

                time.sleep(1)
            except (OSError, AttributeError) as e:
                print(f"연결 해제 중 오류: {e}")

            # 재연결 시도
            if attempt_arduino_connection(arduino, None):
                if attempt_data_reading(arduino):
                    print("✅ Night 모드 수동 재연결 성공!")
                    return "✅ 재연결 성공"
                else:
                    arduino.disconnect()
                    return "❌ 데이터 읽기 실패"
            else:
                return "❌ 연결 실패"

        except PermissionError:
            return "❌ 포트 접근 거부"
        except (OSError, AttributeError, ValueError) as e:
            return f"❌ 오류: {str(e)[:15]}..."

    @app.callback(
        Output("json-toggle-btn-v2", "children"),
        Input("json-toggle-btn-v2", "n_clicks"),
    )
    def toggle_json_mode_v2(n_clicks):
        if n_clicks > 0 and arduino.is_healthy():
            command = {"type": "config", "action": "toggle_json_mode"}
            if arduino.send_command(command):
                return "📡 JSON 토글 전송됨"
            return "❌ 명령 전송 실패"
        return "JSON 모드 토글"

    @app.callback(Output("stats-btn-v2", "children"), Input("stats-btn-v2", "n_clicks"))
    def request_stats_v2(n_clicks):
        if n_clicks > 0 and arduino.is_healthy():
            command = {"type": "request", "action": "get_stats"}
            if arduino.send_command(command):
                return "📊 통계 요청됨"
            return "❌ 요청 실패"
        return "통계 요청"

    # V2 시스템 로그 업데이트 콜백
    @app.callback(
        Output("system-log-v2", "children"),
        Input("interval-component", "n_intervals"),
        State("ui-version-store", "data"),
        prevent_initial_call=True,
    )
    def update_system_log_v2(_n, ui_version):
        if not UIMode.is_night(ui_version):
            return dash.no_update
        _, _, _current_temps, _latest_data, system_messages = _snapshot()
        log_entries = []
        for msg in system_messages:
            ts = msg["timestamp"].strftime("%H:%M:%S")
            level_icons = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}
            icon = level_icons.get(msg["level"], "📝")
            log_entries.append(
                html.Div(
                    f"[{ts}] {icon} {msg['message']}",
                    style={"color": "white", "marginBottom": "2px"},
                )
            )
        return log_entries

    # V2 포트 드롭다운 콜백
    @app.callback(
        [Output("port-dropdown-v2", "options"), Output("port-dropdown-v2", "value")],
        [Input("ui-version-store", "data")],
        [State("port-dropdown-v2", "value")],
        prevent_initial_call=True,
    )
    def unified_refresh_v2_ports(ui_version, current_value):
        """V2 포트 드롭다운을 새로고침합니다."""
        if not UIMode.is_night(ui_version):
            return dash.no_update, dash.no_update

        try:
            # 포트 옵션 가져오기
            options, default_val = get_port_options_safely()

            # 포트를 찾을 수 없는 경우 기본 옵션 사용
            if not options:
                options, default_val = create_fallback_port_options()

            # 현재 선택된 값이 유효한지 확인
            values_set = {o["value"] for o in options}
            value = current_value if current_value in values_set else default_val

            return options, value
        except (ImportError, AttributeError, OSError):
            return dash.no_update, dash.no_update

    # 미니 그래프 업데이트 콜백
    @app.callback(
        [Output(f"sensor-{i}-mini-graph", "figure") for i in range(1, 9)],
        Input("interval-component", "n_intervals"),
        State("ui-version-store", "data"),
        prevent_initial_call=True,
    )
    def update_v2_mini_graphs(_n, ui_version):
        """V2 미니 그래프들을 업데이트합니다."""
        if not UIMode.is_night(ui_version):
            return [dash.no_update] * 8

        _, _, _current_temps, latest_data, _msgs = _snapshot()

        # 데이터가 없는 경우 빈 그래프 반환
        if not latest_data:
            return [create_empty_mini_graph() for _ in range(8)]

        # 데이터프레임 준비
        df = prepare_dataframe(latest_data)
        if df is None:
            return [create_empty_mini_graph() for _ in range(8)]

        # 각 센서별 그래프 생성
        figures = []
        ranges_debug = []

        for sid in range(1, 9):
            sensor_data = df[df["sensor_id"] == sid]
            fig = create_sensor_mini_graph(sensor_data, sid, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT)
            figures.append(fig)

            # 디버그 정보 수집
            if not sensor_data.empty:
                y = sensor_data["temperature"]
                vmin, vmax = float(min(y)), float(max(y))
                ranges_debug.append(f"{sid}:{vmin:.1f}-{vmax:.1f}")

        if ranges_debug:
            print("🌙 v2 mini graphs 갱신: " + ", ".join(ranges_debug))

        return figures

    # 별도 온도 표시 업데이트 콜백
    @app.callback(
        [Output(f"sensor-{i}-current-temp", "children") for i in range(1, 9)],
        Input("interval-component", "n_intervals"),
        State("ui-version-store", "data"),
        prevent_initial_call=True,
    )
    def update_v2_temp_displays(_n, ui_version):
        if not UIMode.is_night(ui_version):
            return [dash.no_update] * 8
        _, _, current_temps, latest_data, _msgs = _snapshot()
        temp_displays = []
        for sid in range(1, 9):
            if latest_data:
                try:
                    df = pd.DataFrame(latest_data)
                    df["sensor_id"] = df["sensor_id"].astype(int)
                    sub = df[df["sensor_id"] == sid]
                    if not sub.empty:
                        temperature_series = pd.Series(sub["temperature"])
                        latest_temp = temperature_series.iloc[-1]
                        temp_displays.append(f"{latest_temp:.1f}°C")
                    else:
                        temp_displays.append("--°C")
                except (KeyError, IndexError, ValueError):
                    temp_displays.append("--°C")
            else:
                temp_displays.append("--°C")
        return temp_displays

    # 모달 관련 콜백들
    def _format_interval(ms: int) -> str:
        if ms < 60000:
            return f"{int(ms/1000)}초"
        if ms < 3600000:
            return f"{int(ms/60000)}분"
        return f"{round(ms/3600000, 1)}시간"

    @app.callback(
        Output("interval-modal", "style"),
        Output("interval-modal-target-sensor", "data"),
        [Input(f"btn-change-interval-v2-{i}", "n_clicks") for i in range(1, 9)]
        + [Input("interval-cancel-btn", "n_clicks")]
        + [Input("interval-confirm-dialog", "submit_n_clicks")],
        State("interval-modal-target-sensor", "data"),
        prevent_initial_call=True,
    )
    def open_close_interval_modal(*args):
        *btn_clicks, cancel_clicks, submit_clicks, current_target = args
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        trig = ctx.triggered[0]["prop_id"].split(".")[0]
        if trig == "interval-cancel-btn" or trig == "interval-confirm-dialog":
            return {"display": "none"}, None
        for idx, n in enumerate(btn_clicks, start=1):
            if trig == f"btn-change-interval-v2-{idx}" and n:
                return {
                    "position": "fixed",
                    "top": 0,
                    "left": 0,
                    "right": 0,
                    "bottom": 0,
                    "backgroundColor": "rgba(0,0,0,0.6)",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "zIndex": 2000,
                }, idx
        return {"display": "none"}, None

    @app.callback(
        Output("interval-selected-preview", "children"),
        Input("interval-select", "value"),
        State("interval-modal-target-sensor", "data"),
        prevent_initial_call=True,
    )
    def preview_interval(value, target):
        if value is None or target is None:
            return ""
        return f"센서 {target} 선택됨: {_format_interval(int(value))}"

    @app.callback(
        Output("pending-interval-selection", "data"),
        Input("interval-apply-btn", "n_clicks"),
        State("interval-select", "value"),
        State("interval-modal-target-sensor", "data"),
        prevent_initial_call=True,
    )
    def trigger_confirm(n_apply, value, target):
        if not n_apply or value is None or target is None:
            raise dash.exceptions.PreventUpdate
        return {"sensor": target, "interval_ms": int(value), "show_dialog": True}

    @app.callback(
        Output("sensor-intervals-store", "data"),
        Output("interval-confirm-dialog", "displayed"),
        Input("interval-confirm-dialog", "submit_n_clicks"),
        State("pending-interval-selection", "data"),
        State("sensor-intervals-store", "data"),
        prevent_initial_call=True,
    )
    def apply_interval(submit_clicks, pending, intervals_map):
        if not submit_clicks or not pending:
            raise dash.exceptions.PreventUpdate
        intervals = dict(intervals_map or {})
        sensor = str(pending["sensor"])
        ms = int(pending["interval_ms"])
        intervals[sensor] = ms
        if arduino.is_healthy():
            try:
                cmd = f"SET_INTERVAL {sensor} {ms}"
                ok = arduino.send_text_command(cmd)
                print(f"🕒 센서 {sensor} 주기 설정 {ms}ms 전송 결과: {ok}")
            except (OSError, AttributeError, ValueError) as e:
                print(f"주기 전송 오류: {e}")
        return intervals, False

    @app.callback(
        [Output(f"btn-change-interval-v2-{i}", "children") for i in range(1, 9)],
        Input("sensor-intervals-store", "data"),
    )
    def update_interval_button_labels(intervals_map):
        labels = []
        for i in range(1, 9):
            ms = (intervals_map or {}).get(str(i), 1000)
            labels.append(f"측정주기 변경 (현재 {_format_interval(ms)})")
        return labels

    # 전체 선택/해제 버튼 콜백 (sensor-line-toggle)
    @app.callback(
        Output("sensor-line-toggle", "value", allow_duplicate=True),
        [Input("btn-select-all", "n_clicks"), Input("btn-deselect-all", "n_clicks")],
        [State("sensor-line-toggle", "value")],
        prevent_initial_call=True,
    )
    def select_deselect_all(select_clicks, deselect_clicks, current_values):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        # 센서 ID 리스트 상수
        all_sensors = [i for i in range(1, 9)]
        if btn_id == "btn-select-all":
            return all_sensors
        if btn_id == "btn-deselect-all":
            return []
        return dash.no_update
