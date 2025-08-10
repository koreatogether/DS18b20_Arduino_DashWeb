"""모달 섹션 - 측정 주기 선택 모달 등"""

from dash import dcc, html


def create_interval_modal():
    """측정 주기 선택 모달 생성"""
    interval_modal = html.Div(
        id="interval-modal",
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "right": 0,
            "bottom": 0,
            "backgroundColor": "rgba(0,0,0,0.6)",
            "display": "none",
            "alignItems": "center",
            "justifyContent": "center",
            "zIndex": 2000,
        },
        children=[
            html.Div(
                style={
                    "backgroundColor": "#222",
                    "padding": "20px",
                    "borderRadius": "8px",
                    "width": "320px",
                    "color": "white",
                    "boxShadow": "0 0 10px #000",
                },
                children=[
                    html.H4("측정 주기 선택", style={"marginTop": 0}),
                    dcc.Dropdown(
                        id="interval-select",
                        options=[
                            {"label": "1초", "value": 1000},
                            {"label": "5초", "value": 5000},
                            {"label": "10초", "value": 10000},
                            {"label": "20초", "value": 20000},
                            {"label": "30초", "value": 30000},
                            {"label": "1분", "value": 60000},
                            {"label": "3분", "value": 180000},
                            {"label": "5분", "value": 300000},
                            {"label": "10분", "value": 600000},
                            {"label": "20분", "value": 1200000},
                            {"label": "40분", "value": 2400000},
                            {"label": "1시간", "value": 3600000},
                        ],
                        placeholder="주기 선택",
                        style={"marginBottom": "10px"},
                    ),
                    html.Div(
                        id="interval-selected-preview",
                        style={
                            "marginBottom": "10px",
                            "fontSize": "14px",
                            "color": "#ddd",
                        },
                    ),
                    html.Div(
                        [
                            html.Button(
                                "적용",
                                id="interval-apply-btn",
                                n_clicks=0,
                                style={"marginRight": "10px"},
                            ),
                            html.Button(
                                "취소",
                                id="interval-cancel-btn",
                                n_clicks=0,
                                style={"backgroundColor": "#444", "color": "white"},
                            ),
                        ],
                        style={"textAlign": "right"},
                    ),
                ],
            )
        ],
    )

    return interval_modal


def create_confirm_dialog():
    """확인 대화상자 생성"""
    return dcc.ConfirmDialog(id="interval-confirm-dialog")
