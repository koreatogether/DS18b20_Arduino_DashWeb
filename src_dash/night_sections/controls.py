"""제어&로그 섹션 - 제어 패널과 시스템 로그"""

from typing import Any, cast

from dash import dcc, html


def create_control_log_section(initial_port_options, selected_port, initial_port_value):
    """제어 패널과 로그 섹션 생성"""
    control_panel_v2 = html.Div(
        [
            # 포트 연결 섹션
            html.Div(
                [
                    html.H3("포트 연결", style={"margin": "4px 0", "color": "white"}),
                    dcc.Dropdown(
                        id="port-dropdown-v2",
                        options=cast(Any, initial_port_options),
                        value=selected_port or initial_port_value,
                        placeholder="자동 감지 또는 포트 선택",
                        style={"width": "100%", "marginBottom": "10px"},
                    ),
                    html.Button(
                        "선택 포트로 연결",
                        id="connect-port-btn-v2",
                        n_clicks=0,
                        style={"width": "100%", "marginBottom": "20px"},
                    ),
                ],
                style={
                    "padding": "20px",
                    "backgroundColor": "#1e1e1e",
                    "borderRadius": "10px",
                    "marginBottom": "15px",
                },
            ),
            # 제어 패널 섹션
            html.Div(
                [
                    html.H3("제어 패널", style={"color": "white"}),
                    html.Button(
                        "Arduino 재연결",
                        id="reconnect-btn-v2",
                        n_clicks=0,
                        style={"margin": "5px", "width": "100%"},
                    ),
                    html.Button(
                        "JSON 모드 토글",
                        id="json-toggle-btn-v2",
                        n_clicks=0,
                        style={"margin": "5px", "width": "100%"},
                    ),
                    html.Button(
                        "통계 요청",
                        id="stats-btn-v2",
                        n_clicks=0,
                        style={"margin": "5px", "width": "100%"},
                    ),
                ],
                style={
                    "padding": "20px",
                    "backgroundColor": "#1e1e1e",
                    "borderRadius": "10px",
                    "marginBottom": "15px",
                },
            ),
            # 시스템 로그 섹션
            html.Div(
                [
                    html.H3("시스템 로그", style={"color": "white"}),
                    html.Div(
                        id="system-log-v2",
                        style={
                            "height": "200px",
                            "overflow": "auto",
                            "border": "1px solid #444",
                            "padding": "10px",
                            "backgroundColor": "#111",
                            "fontFamily": "monospace",
                        },
                    ),
                ],
                style={
                    "padding": "20px",
                    "backgroundColor": "#1e1e1e",
                    "borderRadius": "10px",
                },
            ),
        ]
    )

    return control_panel_v2
