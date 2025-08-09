"""Night Mode (v2) 레이아웃 - 섹션별로 분리된 구조"""
from dash import html
from night_sections.sensor_function_buttons_section import create_sensor_cards_with_buttons
from night_sections.combined_graph_section import create_combined_graph_section
from night_sections.control_log_section import create_control_log_section
from night_sections.modal_section import create_interval_modal, create_confirm_dialog
from night_sections.night_callbacks import register_night_callbacks


def create_layout_v2(initial_port_options, selected_port, initial_port_value, app=None, arduino=None, arduino_connected=None, color_seq=None, th_default=None, tl_default=None, snapshot_func=None):
    """Night mode (v2) – dark theme; 섹션별로 분리된 구조"""
    
    # 1. 센서 온도 섹션 (개별 온도 창 8개) + 센서 기능 버튼 섹션 + 개별 도구 섹션
    sensor_cards = create_sensor_cards_with_buttons()
    
    # 2. 모달 섹션 (측정 주기 선택 모달)
    interval_modal = create_interval_modal()
    confirm_dialog = create_confirm_dialog()
    
    # 3. 종합 그래프 섹션
    combined_graph_block = create_combined_graph_section()
    
    # 4. 제어&로그 섹션
    control_panel_v2 = create_control_log_section(
        initial_port_options, 
        selected_port, 
        initial_port_value
    )
    
    # 5. 숨겨진 플레이스홀더 (공유 콜백 출력용)
    hidden_placeholders = html.Div([
        html.Div(id='connection-status'),
        html.Div(id='temp-graph'),  # dcc.Graph 대신 html.Div 사용
        html.Div(id='system-log'),
        html.Div(id='detail-sensor-dropdown'),  # dcc.Dropdown 대신 html.Div 사용
        html.Div(id='detail-sensor-graph'),  # dcc.Graph 대신 html.Div 사용
        *[html.Div(id=f'sensor-{i}-status') for i in range(1,9)]
    ], style={'display': 'none'})
    
    # 전체 레이아웃 구성
    return html.Div(
        style={
            'backgroundColor': 'black',
            'color': 'white',
            'padding': '20px',
            'height': '100vh',
            'overflowY': 'scroll'
        },
        children=[
            # 헤더
            html.H2(
                "🌙 Sensor Dashboard - Night Mode (v2)", 
                style={
                    'textAlign': 'center', 
                    'marginBottom': '20px'
                }
            ),
            
            # 1. 센서 온도 섹션 (개별 온도 창 8개 + 기능 버튼 + 개별 도구)
            *sensor_cards,
            
            # 2. 모달 섹션
            interval_modal,
            confirm_dialog,
            
            # 3. 종합 그래프 섹션
            combined_graph_block,
            
            # 4. 제어&로그 섹션
            control_panel_v2,
            
            # 5. 숨겨진 플레이스홀더
            hidden_placeholders
        ]
    )