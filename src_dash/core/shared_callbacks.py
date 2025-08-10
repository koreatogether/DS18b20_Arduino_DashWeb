"""공통 콜백 함수들"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, html


def register_shared_callbacks(app, snapshot_func, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT):
    """공통 콜백들을 등록합니다."""

    @app.callback(
        [Output("connection-status", "children"), Output("connection-status", "style")]
        + [Output(f"sensor-{i}-temp", "children") for i in range(1, 9)]
        + [Output(f"sensor-{i}-status", "children") for i in range(1, 9)]
        + [Output(f"sensor-{i}-address", "children") for i in range(1, 9)]
        + [Output("system-log", "children")],
        Input("interval-component", "n_intervals"),
        State("ui-version-store", "data"),
        prevent_initial_call=True,
    )
    def update_status_and_log(_n, ui_version):
        (
            connection_status,
            connection_style,
            current_temps,
            _latest_data,
            system_messages,
        ) = snapshot_func()
        sensor_temps, sensor_statuses, sensor_addresses = [], [], []

        for i in range(1, 9):
            if i in current_temps:
                info = current_temps[i]
                sensor_temps.append(f"{info['temperature']:.1f}°C")
                status = info.get("status", "")
                if status == "ok":
                    sensor_statuses.append("🟢 정상")
                elif status == "simulated":
                    sensor_statuses.append("🟡 시뮬레이션")
                else:
                    sensor_statuses.append(f"⚠️ {status}")

                # 🔥 센서 주소 추가 (시뮬레이션용 더미 주소)
                address = info.get("address", "")
                if address:
                    # 실제 주소가 있는 경우 (예: "28FF641E8016043C")
                    formatted_address = f"{address[:4]}:{address[4:8]}:" f"{address[8:12]}:{address[12:16]}"
                    sensor_addresses.append(formatted_address)
                elif status == "simulated":
                    # 시뮬레이션 모드용 더미 주소
                    dummy_address = f"28FF{i:02d}1E{i:02d}16{i:02d}3C"
                    formatted_address = (
                        f"{dummy_address[:4]}:{dummy_address[4:8]}:"
                        f"{dummy_address[8:12]}:{dummy_address[12:16]}"
                    )
                    sensor_addresses.append(formatted_address)
                else:
                    sensor_addresses.append("----:----:----:----")
            else:
                sensor_temps.append("--°C")
                sensor_statuses.append("🔴 연결 없음")
                sensor_addresses.append("----:----:----:----")

        log_entries = []
        for msg in system_messages:
            ts = msg["timestamp"].strftime("%H:%M:%S")
            level_icons = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}
            icon = level_icons.get(msg["level"], "📝")
            log_entries.append(html.Div(f"[{ts}] {icon} {msg['message']}"))

        return (
            [connection_status, connection_style]
            + sensor_temps
            + sensor_statuses
            + sensor_addresses
            + [log_entries]
        )

    @app.callback(
        [Output("temp-graph", "figure"), Output("detail-sensor-graph", "figure")],
        [
            Input("interval-component", "n_intervals"),
            Input("detail-sensor-dropdown", "value"),
        ],
        [State("ui-version-store", "data")],
        prevent_initial_call=True,
    )
    def update_main_graphs(_n, detail_sensor_id, ui_version):
        if detail_sensor_id is None:
            detail_sensor_id = 1
        _, _, _current_temps, latest_data, _msgs = snapshot_func()

        # Temp overview graph
        if latest_data:
            df = pd.DataFrame(latest_data)
            # 필수 컬럼 존재 확인
            required_cols = {"timestamp", "sensor_id", "temperature"}
            if required_cols.issubset(df.columns):
                # 변환 시도 (실패해도 치명적 아님)
                if "timestamp" in df.columns:
                    try:
                        df["timestamp"] = pd.to_datetime(df["timestamp"])
                    except Exception:
                        pass
                if "sensor_id" in df.columns:
                    try:
                        df["sensor_id"] = df["sensor_id"].astype(str)
                    except Exception:
                        pass
                try:
                    fig = px.line(
                        df,
                        x="timestamp",
                        y="temperature",
                        color="sensor_id",
                        title="실시간 온도 모니터링 (최근 50개 데이터)",
                        template="plotly_white",
                    )
                except Exception:
                    fig = go.Figure()
                    for sid, g in df.groupby("sensor_id"):
                        fig.add_trace(
                            go.Scatter(
                                x=g.get("timestamp"),
                                y=g.get("temperature"),
                                mode="lines",
                                name=sid,
                            )
                        )
                    fig.update_layout(
                        title="실시간 온도 모니터링 (최근 50개 데이터)",
                        template="plotly_white",
                    )
            else:
                fig = go.Figure()
                fig.update_layout(title="데이터 (형식 오류)", template="plotly_white")
        else:
            fig = go.Figure()
            fig.update_layout(title="데이터 없음", template="plotly_white")

        # Add global TH/TL lines
        try:
            fig.add_hline(
                y=TH_DEFAULT,
                line_dash="dash",
                line_color="red",
                annotation_text="TH",
                annotation_position="top left",
            )
            fig.add_hline(
                y=TL_DEFAULT,
                line_dash="dash",
                line_color="blue",
                annotation_text="TL",
                annotation_position="bottom left",
            )
        except (ValueError, AttributeError):
            pass

        # Detail graph
        if latest_data:
            df_all = pd.DataFrame(latest_data)
            if {"timestamp", "sensor_id", "temperature"}.issubset(df_all.columns):
                try:
                    df_all["timestamp"] = pd.to_datetime(df_all["timestamp"])
                except Exception:
                    pass
                try:
                    df_all["sensor_id"] = df_all["sensor_id"].astype(int)
                except Exception:
                    pass
                one = df_all[df_all["sensor_id"] == detail_sensor_id]
                if not one.empty:
                    try:
                        detail_fig = px.line(
                            one,
                            x="timestamp",
                            y="temperature",
                            title=f"센서 {detail_sensor_id} 상세 그래프",
                            template="plotly_white",
                        )
                    except Exception:
                        detail_fig = go.Figure()
                        detail_fig.add_trace(
                            go.Scatter(
                                x=one.get("timestamp"),
                                y=one.get("temperature"),
                                mode="lines",
                                name=f"센서 {detail_sensor_id}",
                            )
                        )
                else:
                    detail_fig = go.Figure()
                    detail_fig.update_layout(
                        title=f"센서 {detail_sensor_id} 데이터 없음",
                        template="plotly_white",
                    )
            else:
                detail_fig = go.Figure()
                detail_fig.update_layout(title="상세 데이터 (형식 오류)", template="plotly_white")
        else:
            detail_fig = go.Figure()
            detail_fig.update_layout(title="상세 데이터 없음", template="plotly_white")

        try:
            detail_fig.add_hline(y=TH_DEFAULT, line_dash="dash", line_color="red")
            detail_fig.add_hline(y=TL_DEFAULT, line_dash="dash", line_color="blue")
        except (ValueError, AttributeError):
            pass

        fig.update_layout(height=440)
        detail_fig.update_layout(height=440)
        return fig, detail_fig

    @app.callback(
        Output("combined-graph", "figure"),
        [
            Input("interval-component", "n_intervals"),
            Input("sensor-line-toggle", "value"),
        ],
        State("ui-version-store", "data"),
        prevent_initial_call=True,
    )
    def update_combined_graph(_n, selected_sensor_lines, ui_version):
        from .ui_modes import UIMode

        ui_is_night = UIMode.is_night(ui_version)
        # 선택된 센서가 없으면 빈 그래프 반환 (임계선/센서라인 모두 제거)
        if not selected_sensor_lines:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="전체 센서 실시간 온도 (센서 선택 없음)",
                template="plotly_dark" if ui_is_night else "plotly_white",
                height=560 if ui_is_night else 480,
                showlegend=False,
                plot_bgcolor="#000" if ui_is_night else None,
                paper_bgcolor="#000" if ui_is_night else None,
            )
            return empty_fig
        _, _, _current_temps, latest_data, _msgs = snapshot_func()
        # 선택된 센서 ID를 정수 리스트로 변환
        try:
            selected_ids = [int(s) for s in selected_sensor_lines]
        except Exception:
            selected_ids = []

        if latest_data:
            df = pd.DataFrame(latest_data)
            if {"timestamp", "sensor_id", "temperature"}.issubset(df.columns):
                # 타입 변환 (best-effort)
                try:
                    df["sensor_id"] = df["sensor_id"].astype(int)
                except Exception:
                    pass
                try:
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                except Exception:
                    pass
                df = df[df["sensor_id"].isin(selected_ids)]
                fig = go.Figure()
                for sid, g in df.groupby("sensor_id"):
                    if sid in selected_ids:
                        trace_color = (
                            COLOR_SEQ[(sid - 1) % len(COLOR_SEQ)] if isinstance(sid, int) else "#888"
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=g.get("timestamp"),
                                y=g.get("temperature"),
                                mode="lines",
                                name=f"센서 {sid}",
                                line=dict(color=trace_color, width=2),  # type: ignore[arg-type]
                            )
                        )
                if ui_is_night:
                    fig.update_layout(
                        title="전체 센서 실시간 온도",
                        template="plotly_dark",
                        height=560,
                        showlegend=False,
                        plot_bgcolor="#000",
                        paper_bgcolor="#000",
                    )
                    fig.update_xaxes(tickformat="%H:%M:%S")
                else:
                    fig.update_layout(
                        title="전체 센서 실시간 온도",
                        template="plotly_white",
                        height=480,
                        showlegend=False,
                    )
            else:
                fig = go.Figure()
                fig.update_layout(
                    title="전체 센서 실시간 온도 (형식 오류)",
                    height=480,
                    template="plotly_dark" if ui_is_night else "plotly_white",
                )
        else:
            fig = go.Figure()
            fig.update_layout(
                title="전체 센서 실시간 온도 (데이터 없음)",
                height=560 if ui_is_night else 480,
                template="plotly_dark" if ui_is_night else "plotly_white",
                showlegend=False,
                plot_bgcolor="#000" if ui_is_night else None,
                paper_bgcolor="#000" if ui_is_night else None,
            )
            if ui_is_night:
                fig.update_xaxes(tickformat="%H:%M:%S")
        return fig

    # 콜백 충돌 방지를 위해 임시 비활성화
    # @app.callback(
    #     Output('mode-indicator', 'children'),
    #     Output('mode-feedback', 'children'),
    #     Input('ui-version-store', 'data')
    # )
    # def show_mode_indicator_and_feedback(ui_version):
    #     if ui_version == 'v2':
    #         return "현재 모드: 🌙 Night (v2)", "🌙 Night 모드로 전환됨"
    #     return "현재 모드: ☀️ Day (v1)", "☀️ Day 모드로 전환됨"
