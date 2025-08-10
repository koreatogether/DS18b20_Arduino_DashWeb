"""Day Mode (v1) 레이아웃 함수"""

import datetime
from typing import Any, cast

from dash import dcc, html


def create_layout_v1(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE):
    """Day mode (v1) 레이아웃 생성"""
    return html.Div(
        [
            html.H1(
                "☀️ DS18B20 센서 데이터 대시보드 (Day Mode)",
                style={"textAlign": "center", "color": "#2c3e50"},
            ),
            html.Div(
                f"UI Build: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                style={
                    "textAlign": "center",
                    "color": "#6c757d",
                    "fontSize": "12px",
                    "marginBottom": "6px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        id="connection-status",
                        style={
                            "textAlign": "center",
                            "margin": "10px",
                            "padding": "10px",
                            "border": "2px solid",
                            "borderRadius": "5px",
                        },
                    ),
                    html.Div(
                        [
                            html.H3("포트 연결", style={"margin": "4px 0"}),
                            html.Span("포트 선택: ", style={"marginRight": "6px"}),
                            dcc.Dropdown(
                                id="port-dropdown",
                                options=cast(Any, INITIAL_PORT_OPTIONS),
                                value=selected_port or INITIAL_PORT_VALUE,
                                placeholder="자동 감지 또는 포트 선택",
                                style={
                                    "display": "inline-block",
                                    "width": "260px",
                                    "marginRight": "8px",
                                },
                            ),
                            html.Button(
                                "선택 포트로 연결",
                                id="connect-port-btn",
                                n_clicks=0,
                                style={"display": "inline-block"},
                            ),
                        ],
                        style={"textAlign": "center", "marginTop": "8px"},
                    ),
                ]
            ),
            html.Hr(),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("센서 상태", style={"textAlign": "center"}),
                            html.Div(
                                id="sensor-cards",
                                children=[
                                    html.Div(
                                        [
                                            html.H4(f"센서 {i}", style={"margin": "5px"}),
                                            html.Div(
                                                id=f"sensor-{i}-temp",
                                                children="--°C",
                                                style={
                                                    "fontSize": "24px",
                                                    "fontWeight": "bold",
                                                },
                                            ),
                                            html.Div(
                                                id=f"sensor-{i}-status",
                                                children="연결 대기",
                                                style={
                                                    "fontSize": "12px",
                                                    "color": "#666",
                                                },
                                            ),
                                            html.Div(
                                                id=f"sensor-{i}-address",
                                                children="주소: ----:----:----:----",
                                                style={
                                                    "fontSize": "13px",
                                                    "color": "#999",
                                                    "marginTop": "16px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "inline-block",
                                            "margin": "10px",
                                            "padding": "20px",
                                            "border": "1px solid #ddd",
                                            "borderRadius": "8px",
                                            "width": "170px",
                                            "textAlign": "center",
                                            "backgroundColor": "#f9f9f9",
                                        },
                                    )
                                    for i in range(1, 9)
                                ],
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H4(
                                                "전체 센서 실시간 그래프 (1~8)",
                                                style={
                                                    "margin": "0 0 8px 0",
                                                    "textAlign": "center",
                                                },
                                            ),
                                            html.Div(
                                                [
                                                    dcc.Graph(
                                                        id="combined-graph",
                                                        style={"flex": "1"},
                                                        config={"displaylogo": False},
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Strong("표시 센서"),
                                                            dcc.Checklist(
                                                                id="sensor-line-toggle",
                                                                options=[
                                                                    {
                                                                        "label": f"센서 {i}",
                                                                        "value": i,
                                                                    }
                                                                    for i in range(1, 9)
                                                                ],
                                                                value=[i for i in range(1, 9)],
                                                                labelStyle={
                                                                    "display": "block",
                                                                    "margin": "2px 0",
                                                                },
                                                            ),
                                                            html.Button(
                                                                "전체 선택",
                                                                id="btn-select-all",
                                                                n_clicks=0,
                                                                style={
                                                                    "marginTop": "6px",
                                                                    "width": "100%",
                                                                },
                                                            ),
                                                            html.Button(
                                                                "전체 해제",
                                                                id="btn-deselect-all",
                                                                n_clicks=0,
                                                                style={
                                                                    "marginTop": "4px",
                                                                    "width": "100%",
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "width": "140px",
                                                            "marginLeft": "12px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "flex-start",
                                                },
                                            ),
                                        ],
                                        style={
                                            "marginTop": "20px",
                                            "padding": "10px",
                                            "border": "1px solid #ddd",
                                            "borderRadius": "8px",
                                            "backgroundColor": "#fff",
                                        },
                                    )
                                ]
                            ),
                        ],
                        style={"flex": "1", "minWidth": "340px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "flex-start",
                    "flexWrap": "wrap",
                },
            ),
            html.Hr(),
            html.Div(
                [
                    dcc.Graph(
                        id="temp-graph",
                        style={"height": "440px"},
                        config={"displaylogo": False},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("상세 그래프 센서 선택"),
                                    dcc.Dropdown(
                                        id="detail-sensor-dropdown",
                                        options=[{"label": f"센서 {i}", "value": i} for i in range(1, 65)],
                                        value=1,
                                        clearable=False,
                                        style={"width": "200px"},
                                    ),
                                ],
                                style={"marginBottom": "10px"},
                            ),
                            dcc.Graph(
                                id="detail-sensor-graph",
                                style={"height": "440px"},
                                config={"displaylogo": False},
                            ),
                        ],
                        style={"marginTop": "20px"},
                    ),
                ],
                style={"margin": "20px"},
            ),
            html.Div(
                [
                    html.H3("제어 패널"),
                    html.Button(
                        "Arduino 재연결",
                        id="reconnect-btn",
                        n_clicks=0,
                        style={"margin": "5px", "padding": "10px"},
                    ),
                    html.Button(
                        "JSON 모드 토글",
                        id="json-toggle-btn",
                        n_clicks=0,
                        style={"margin": "5px", "padding": "10px"},
                    ),
                    html.Button(
                        "통계 요청",
                        id="stats-btn",
                        n_clicks=0,
                        style={"margin": "5px", "padding": "10px"},
                    ),
                ],
                style={
                    "margin": "20px",
                    "padding": "15px",
                    "backgroundColor": "#f0f0f0",
                    "borderRadius": "5px",
                },
            ),
            html.Div(
                [
                    html.H3("시스템 로그"),
                    html.Div(
                        id="system-log",
                        style={
                            "height": "200px",
                            "overflow": "auto",
                            "border": "1px solid #ddd",
                            "padding": "10px",
                            "backgroundColor": "#f8f8f8",
                            "fontFamily": "monospace",
                        },
                    ),
                ],
                style={"margin": "20px"},
            ),
        ]
    )
