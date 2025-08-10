"""센서 도구 컴포넌트 - 각 센서별 도구 아이콘들"""

from dash import html


def create_individual_tools():
    """각 센서별 개별 설정 도구 8개 생성"""
    tool_sections = []

    for i in range(1, 9):
        tool_section = html.Div(
            [
                html.Div(
                    [
                        html.Span(
                            "⚙️",
                            style={
                                "fontSize": "20px",
                                "marginBottom": "5px",
                                "display": "block",
                            },
                        ),
                        html.Span(
                            "🔧",
                            style={
                                "fontSize": "20px",
                                "marginBottom": "5px",
                                "display": "block",
                            },
                        ),
                        html.Span("📊", style={"fontSize": "20px", "display": "block"}),
                    ],
                    style={"textAlign": "center"},
                )
            ],
            style={
                "padding": "10px",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "backgroundColor": "#2a2a2a",
                "borderRadius": "5px",
                "border": "1px solid #555",
            },
        )

        tool_sections.append(tool_section)

    return tool_sections


def create_expanded_individual_tools():
    """확장된 개별 도구 (향후 기능 추가용)"""
    expanded_tools = []

    for i in range(1, 9):
        expanded_tool = html.Div(
            [
                html.Div(
                    [
                        html.Span("⚙️", style={"fontSize": "24px", "marginBottom": "10px"}),
                        html.Div(
                            [
                                html.Button(
                                    "상세 설정",
                                    id=f"btn-detail-settings-{i}",
                                    style={
                                        "backgroundColor": "#444",
                                        "color": "white",
                                        "border": "none",
                                        "padding": "5px 10px",
                                        "marginBottom": "5px",
                                        "width": "100%",
                                    },
                                ),
                                html.Button(
                                    "알람 설정",
                                    id=f"btn-alarm-settings-{i}",
                                    style={
                                        "backgroundColor": "#444",
                                        "color": "white",
                                        "border": "none",
                                        "padding": "5px 10px",
                                        "marginBottom": "5px",
                                        "width": "100%",
                                    },
                                ),
                                html.Button(
                                    "데이터 내보내기",
                                    id=f"btn-export-data-{i}",
                                    style={
                                        "backgroundColor": "#444",
                                        "color": "white",
                                        "border": "none",
                                        "padding": "5px 10px",
                                        "width": "100%",
                                    },
                                ),
                            ],
                            style={"display": "none"},
                            id=f"tool-menu-{i}",
                        ),
                    ]
                )
            ],
            style={
                "padding": "20px",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
            },
        )

        expanded_tools.append(expanded_tool)

    return expanded_tools
