"""센서 카드 컴포넌트 - 온도 표시, 기능 버튼, 미니 그래프, 도구를 통합한 센서 카드들"""

from dash import dcc, html


def create_sensor_function_buttons():
    """각 센서별 기능 버튼들 생성 (8개 센서 x 3개 버튼 = 24개)"""
    button_sections = []

    for i in range(1, 9):
        button_group = html.Div(
            [
                html.Button(
                    "ID 변경",
                    id=f"btn-change-id-v2-{i}",
                    style={
                        "backgroundColor": "#555",
                        "color": "white",
                        "border": "none",
                        "padding": "5px 10px",
                        "margin": "0 5px",
                    },
                ),
                html.Button(
                    "상/하한 온도 임계값 변경",
                    id=f"btn-change-thresholds-v2-{i}",
                    style={
                        "backgroundColor": "#555",
                        "color": "white",
                        "border": "none",
                        "padding": "5px 10px",
                        "margin": "0 5px",
                    },
                ),
                html.Button(
                    "측정주기 변경 (현재 1초)",
                    id=f"btn-change-interval-v2-{i}",
                    style={
                        "backgroundColor": "#555",
                        "color": "white",
                        "border": "none",
                        "padding": "5px 10px",
                        "margin": "0 5px",
                    },
                ),
            ],
            style={"marginBottom": "10px"},
        )

        button_sections.append(button_group)

    return button_sections


def create_sensor_cards_with_buttons(TH_DEFAULT=55.0, TL_DEFAULT=-25.0):
    """온도 카드와 기능 버튼을 결합한 완전한 센서 카드들 - 원하는 구조로 복구"""
    from .mini_graphs import get_mini_graph_placeholder
    from .sensor_tools import create_individual_tools

    sensor_cards = []
    tool_sections = create_individual_tools()

    for i in range(1, 9):
        # 미니 그래프 플레이스홀더
        fig = get_mini_graph_placeholder()

        card = html.Div(
            [
                # 왼쪽: 개별 센서 온도창
                html.Div(
                    [
                        html.H4(
                            f"센서 ID {i}",
                            style={
                                "color": "white",
                                "marginBottom": "5px",
                                "textAlign": "center",
                            },
                        ),
                        html.P(
                            "--°C",
                            id=f"sensor-{i}-temp",
                            style={
                                "fontSize": "28px",
                                "fontWeight": "bold",
                                "color": "white",
                                "margin": "0",
                                "textAlign": "center",
                            },
                        ),
                        html.Div(
                            "정상",
                            id=f"sensor-{i}-status",
                            style={
                                "fontSize": "12px",
                                "color": "#4CAF50",
                                "textAlign": "center",
                                "marginTop": "2px",
                            },
                        ),
                        html.Div(
                            "----:----:----:----",
                            id=f"sensor-{i}-address",
                            style={
                                "fontSize": "13px",
                                "color": "#999",
                                "textAlign": "center",
                                "marginTop": "16px",
                                "fontFamily": "monospace",
                                "lineHeight": "1.2",
                            },
                        ),
                    ],
                    style={
                        "flex": "0 1 120px",
                        "padding": "15px",
                        "borderRight": "1px solid #444",
                    },
                ),
                # 중간: 위에서 아래로 3개의 조정버튼
                html.Div(
                    [
                        html.Button(
                            "ID 변경",
                            id=f"btn-change-id-v2-{i}",
                            style={
                                "backgroundColor": "#555",
                                "color": "white",
                                "border": "none",
                                "padding": "8px 12px",
                                "margin": "3px 0",
                                "width": "100%",
                                "borderRadius": "4px",
                            },
                        ),
                        html.Button(
                            "상/하한 온도 임계값 변경",
                            id=f"btn-change-thresholds-v2-{i}",
                            style={
                                "backgroundColor": "#555",
                                "color": "white",
                                "border": "none",
                                "padding": "8px 12px",
                                "margin": "3px 0",
                                "width": "100%",
                                "borderRadius": "4px",
                            },
                        ),
                        html.Button(
                            "측정주기 변경 (현재 1초)",
                            id=f"btn-change-interval-v2-{i}",
                            style={
                                "backgroundColor": "#555",
                                "color": "white",
                                "border": "none",
                                "padding": "8px 12px",
                                "margin": "3px 0",
                                "width": "100%",
                                "borderRadius": "4px",
                            },
                        ),
                    ],
                    style={
                        "flex": "0 1 200px",
                        "padding": "10px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "borderRight": "1px solid #444",
                    },
                ),
                # 오른쪽 위: 개별 그래프와 숫자 표시
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    id=f"sensor-{i}-mini-graph",
                                    figure=fig,
                                    style={"height": "200px"},
                                    config={"displayModeBar": False},
                                )
                            ],
                            style={"flex": "1"},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    f"TH {TH_DEFAULT:.1f}",
                                    style={
                                        "color": "red",
                                        "fontSize": "16px",
                                        "marginBottom": "15px",
                                        "marginTop": "-40px",
                                    },
                                ),
                                html.Div(
                                    id=f"sensor-{i}-current-temp",
                                    children="--°C",
                                    style={
                                        "color": "white",
                                        "fontSize": "16px",
                                        "fontWeight": "bold",
                                        "marginBottom": "10px",
                                    },
                                ),
                                html.Div(
                                    "0",
                                    style={
                                        "color": "#aaa",
                                        "fontSize": "16px",
                                        "marginBottom": "8px",
                                        "textAlign": "center",
                                    },
                                ),
                                html.Div(
                                    f"TL {TL_DEFAULT:.1f}",
                                    style={"color": "green", "fontSize": "16px"},
                                ),
                            ],
                            style={
                                "width": "60px",
                                "padding": "10px",
                                "display": "flex",
                                "flexDirection": "column",
                                "justifyContent": "center",
                            },
                        ),
                    ],
                    style={"flex": "1", "padding": "5px", "display": "flex"},
                ),
                # 오른쪽 아래: 도구 아이콘
                html.Div(
                    [tool_sections[i - 1]],
                    style={
                        "flex": "0 1 80px",
                        "padding": "10px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                    },
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "stretch",
                "backgroundColor": "#1e1e1e",
                "borderRadius": "10px",
                "marginBottom": "28px",
                "border": "1px solid #444",
                "minHeight": "190px",
            },
        )

        sensor_cards.append(card)

    return sensor_cards
