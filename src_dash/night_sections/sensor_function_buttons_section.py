"""센서 기능 버튼 섹션 - ID 변경, 상/하한 온도 임계값 변경, 측정주기 변경 버튼들 24개"""
from dash import html, dcc


def create_sensor_function_buttons():
    """각 센서별 기능 버튼들 생성 (8개 센서 x 3개 버튼 = 24개)"""
    button_sections = []
    
    for i in range(1, 9):
        button_group = html.Div([
            html.Button(
                'ID 변경', 
                id=f'btn-change-id-v2-{i}', 
                style={
                    'backgroundColor': '#555', 
                    'color': 'white', 
                    'border': 'none', 
                    'padding': '5px 10px', 
                    'margin': '0 5px'
                }
            ),
            html.Button(
                '상/하한 온도 임계값 변경', 
                id=f'btn-change-thresholds-v2-{i}', 
                style={
                    'backgroundColor': '#555', 
                    'color': 'white', 
                    'border': 'none', 
                    'padding': '5px 10px', 
                    'margin': '0 5px'
                }
            ),
            html.Button(
                '측정주기 변경 (현재 1초)', 
                id=f'btn-change-interval-v2-{i}', 
                style={
                    'backgroundColor': '#555', 
                    'color': 'white', 
                    'border': 'none', 
                    'padding': '5px 10px', 
                    'margin': '0 5px'
                }
            ),
        ], style={'marginBottom': '10px'})
        
        button_sections.append(button_group)
    
    return button_sections


def create_sensor_cards_with_buttons():
    """온도 카드와 기능 버튼을 결합한 완전한 센서 카드들 - 원하는 구조로 복구"""
    from .individual_graphs_section import get_mini_graph_placeholder
    from .individual_tools_section import create_individual_tools
    
    sensor_cards = []
    tool_sections = create_individual_tools()
    
    for i in range(1, 9):
        # 미니 그래프 플레이스홀더
        fig = get_mini_graph_placeholder()
        
        card = html.Div([
            # 왼쪽: 개별 센서 온도창
            html.Div([
                html.H4(f"센서 ID {i}", style={'color': 'white', 'marginBottom': '5px', 'textAlign': 'center'}),
                html.P("--°C", id=f'sensor-{i}-temp', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': 'white', 'margin': '0', 'textAlign': 'center'})
            ], style={'flex': '0 1 120px', 'padding': '15px', 'borderRight': '1px solid #444'}),
            
            # 중간: 위에서 아래로 3개의 조정버튼
            html.Div([
                html.Button('ID 변경', 
                    id=f'btn-change-id-v2-{i}', 
                    style={'backgroundColor': '#555', 'color': 'white', 'border': 'none', 'padding': '8px 12px', 'margin': '3px 0', 'width': '100%', 'borderRadius': '4px'}
                ),
                html.Button('상/하한 온도 임계값 변경', 
                    id=f'btn-change-thresholds-v2-{i}', 
                    style={'backgroundColor': '#555', 'color': 'white', 'border': 'none', 'padding': '8px 12px', 'margin': '3px 0', 'width': '100%', 'borderRadius': '4px'}
                ),
                html.Button('측정주기 변경 (현재 1초)', 
                    id=f'btn-change-interval-v2-{i}', 
                    style={'backgroundColor': '#555', 'color': 'white', 'border': 'none', 'padding': '8px 12px', 'margin': '3px 0', 'width': '100%', 'borderRadius': '4px'}
                ),
            ], style={'flex': '0 1 200px', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'borderRight': '1px solid #444'}),
            
            # 오른쪽 위: 개별 그래프
            html.Div([
            dcc.Graph(id=f'sensor-{i}-mini-graph', figure=fig, style={'height': '170px'}, config={'displayModeBar': False})
            ], style={'flex': '1', 'padding': '5px'}),
            
            # 오른쪽 아래: 도구 아이콘
            html.Div([
                tool_sections[i-1]
            ], style={'flex': '0 1 80px', 'padding': '10px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
            
    ], style={'display': 'flex', 'alignItems': 'stretch', 'backgroundColor': '#1e1e1e', 'borderRadius': '10px', 'marginBottom': '28px', 'border': '1px solid #444', 'minHeight': '190px'})
        
        sensor_cards.append(card)
    
    return sensor_cards