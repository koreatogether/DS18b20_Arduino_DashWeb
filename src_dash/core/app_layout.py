"""앱 레이아웃 및 검증 레이아웃 관리"""

from dash import dcc, html

from .ui_modes import UIMode


def create_main_layout(initial_port_options, selected_port, initial_port_value, create_layout_v1):
    """메인 앱 레이아웃을 생성합니다."""
    print("🔍 [LAYOUT] 메인 레이아웃 생성 시작")
    print("🔍 [LAYOUT] 버튼 생성 중...")
    print("✅ [LAYOUT] Day 버튼 생성 완료 (ID: btn-ver-1)")
    print("✅ [LAYOUT] Night 버튼 생성 완료 (ID: btn-ver-2)")

    return html.Div(
        [
            html.Div(
                [
                    html.H1("DS18B20 Dashboard", style={"flex": "1"}),
                    html.Div(
                        [
                            html.Button(
                                "☀️ Day (v1)",
                                id="btn-ver-1",
                                n_clicks=0,
                                **{
                                    "data-testid": "day-button",
                                    "style": {
                                        "marginRight": "10px",
                                        "padding": "12px 20px",
                                        "fontSize": "16px",
                                        "fontWeight": "bold",
                                        "border": "3px solid #007bff",
                                        "borderRadius": "8px",
                                        "backgroundColor": "#007bff",
                                        "color": "white",
                                        "cursor": "pointer",
                                        "transition": "all 0.3s ease",
                                        "boxShadow": "0 2px 4px rgba(0,123,255,0.3)",
                                        "minWidth": "120px",
                                        "height": "50px",
                                    },
                                },
                            ),
                            html.Button(
                                "🌙 Night (v2)",
                                id="btn-ver-2",
                                n_clicks=0,
                                **{
                                    "data-testid": "night-button",
                                    "style": {
                                        "padding": "12px 20px",
                                        "fontSize": "16px",
                                        "fontWeight": "bold",
                                        "border": "3px solid #6c757d",
                                        "borderRadius": "8px",
                                        "backgroundColor": "#6c757d",
                                        "color": "white",
                                        "cursor": "pointer",
                                        "transition": "all 0.3s ease",
                                        "boxShadow": "0 2px 4px rgba(108,117,125,0.3)",
                                        "minWidth": "120px",
                                        "height": "50px",
                                    },
                                },
                            ),
                        ],
                        style={"textAlign": "right"},
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "padding": "10px",
                    "borderBottom": "1px solid #ddd",
                },
            ),
            html.Div(
                id="mode-indicator",
                style={
                    "textAlign": "center",
                    "fontWeight": "bold",
                    "color": "#007bff",
                    "margin": "8px",
                },
            ),
            html.Div(
                id="mode-feedback",
                style={
                    "textAlign": "center",
                    "color": "#28a745",
                    "marginBottom": "8px",
                },
            ),
            dcc.Store(id="ui-version-store", data=UIMode.DAY.value),
            html.Div(
                id="main-content",
                children=create_layout_v1(initial_port_options, selected_port, initial_port_value),
            ),
            # Common components that should always be present
            dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
            dcc.Store(id="sensor-data-store"),
            dcc.Store(id="threshold-store", data={}),
            dcc.Store(id="last-command-result"),
            dcc.Store(id="port-options-cache"),
            dcc.Store(id="sensor-intervals-store"),
            dcc.Store(id="interval-modal-target-sensor"),
            dcc.Store(id="pending-interval-selection"),
        ]
    )


def build_validation_layout():
    """검증 레이아웃을 생성합니다 (모든 컴포넌트 ID의 상위집합)."""
    return html.Div(
        [
            # Version switch buttons (ensure inputs exist for callbacks during validation)
            html.Button(id="btn-ver-1"),
            html.Button(id="btn-ver-2"),
            html.Div(id="main-content"),
            dcc.Store(id="ui-version-store"),
            dcc.Interval(id="interval-component"),
            html.Div(id="connection-status"),
            dcc.Graph(id="temp-graph"),
            html.Div(id="system-log"),
            dcc.Dropdown(id="detail-sensor-dropdown"),
            dcc.Graph(id="detail-sensor-graph"),
            dcc.Graph(id="combined-graph"),
            html.Div(id="system-log"),
            dcc.Dropdown(id="port-dropdown"),
            dcc.Checklist(id="sensor-line-toggle"),
            html.Button(id="btn-select-all"),
            html.Button(id="btn-deselect-all"),
            html.Button(id="reconnect-btn"),
            html.Button(id="json-toggle-btn"),
            html.Button(id="stats-btn"),
            html.Button(id="connect-port-btn"),
            html.Button(id="btn-change-id"),
            html.Button(id="btn-change-thresholds"),
            html.Button(id="btn-change-interval"),
            dcc.Input(id="input-old-id"),
            dcc.Input(id="input-new-id"),
            dcc.Input(id="input-target-id"),
            dcc.Input(id="input-tl"),
            dcc.Input(id="input-th"),
            dcc.Input(id="input-interval"),
            dcc.Store(id="threshold-store"),
            dcc.Store(id="last-command-result"),
            dcc.Store(id="sensor-intervals-store"),
            dcc.Store(id="interval-modal-target-sensor"),
            dcc.Store(id="pending-interval-selection"),
            *[html.Div(id=f"sensor-{i}-temp") for i in range(1, 9)],
            *[html.Div(id=f"sensor-{i}-status") for i in range(1, 9)],
            # v2 컴포넌트들 (validation용)
            html.Div(id="system-log-v2"),
            dcc.Dropdown(id="port-dropdown-v2"),
            html.Button(id="connect-port-btn-v2"),
            html.Button(id="reconnect-btn-v2"),
            html.Button(id="json-toggle-btn-v2"),
            html.Button(id="stats-btn-v2"),
            *[dcc.Graph(id=f"sensor-{i}-mini-graph") for i in range(1, 9)],
            html.Div(id="interval-modal"),
            dcc.Dropdown(id="interval-select"),
            html.Button(id="interval-apply-btn"),
            html.Button(id="interval-cancel-btn"),
            dcc.ConfirmDialog(id="interval-confirm-dialog"),
            html.Div(id="interval-selected-preview"),
            *[html.Button(id=f"btn-change-interval-v2-{i}") for i in range(1, 9)],
            *[html.Button(id=f"btn-change-id-v2-{i}") for i in range(1, 9)],
            *[html.Button(id=f"btn-change-thresholds-v2-{i}") for i in range(1, 9)],
        ]
    )
