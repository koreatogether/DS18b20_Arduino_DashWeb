"""종합 그래프 섹션 - 전체 센서 실시간 그래프"""
from dash import html, dcc


# 센서별 색상 시퀀스
COLOR_SEQ = ["#2C7BE5", "#00A3A3", "#E67E22", "#6F42C1", "#FF6B6B", "#20C997", "#795548", "#FFB400"]


def create_combined_graph_section():
    """전체 센서 실시간 그래프 섹션 생성"""
    combined_graph_block = html.Div([
        html.H4(
            "전체 센서 실시간 그래프 (1~8)", 
            style={
                'margin': '0 0 8px 0', 
                'textAlign': 'center', 
                'color': 'white'
            }
        ),
        html.Div([
            # 메인 그래프
            dcc.Graph(
                id='combined-graph', 
                style={'flex': '1', 'height': '480px'}, 
                config={'displaylogo': False}
            ),
            
            # 그래프 컨트롤 패널
            html.Div([
                html.Strong(
                    "표시 센서", 
                    style={
                        'color': 'white', 
                        'display': 'block', 
                        'marginBottom': '4px'
                    }
                ),
                
                # 센서 선택 체크리스트
                dcc.Checklist(
                    id='sensor-line-toggle',
                    options=[{'label': f"센서 {i}", 'value': i} for i in range(1,9)],
                    value=[i for i in range(1,9)],
                    labelStyle={
                        'display': 'block', 
                        'margin': '2px 0', 
                        'color': 'white'
                    }
                ),
                
                # 색상 범례
                html.Div([
                    html.Div([
                        html.Span(style={
                            'display': 'inline-block', 
                            'width': '10px', 
                            'height': '10px',
                            'backgroundColor': COLOR_SEQ[i-1], 
                            'marginRight': '6px',
                            'borderRadius': '2px'
                        }),
                        html.Span(
                            f"센서 {i}", 
                            style={'fontSize': '11px', 'color': 'white'}
                        )
                    ], style={
                        'display': 'flex', 
                        'alignItems': 'center', 
                        'margin': '2px 0'
                    })
                    for i in range(1,9)
                ], id='sensor-color-legend', style={
                    'marginTop': '6px', 
                    'marginBottom': '6px'
                }),
                
                # 전체 선택/해제 버튼
                html.Button(
                    '전체 선택', 
                    id='btn-select-all', 
                    n_clicks=0, 
                    style={
                        'marginTop': '6px', 
                        'width': '100%'
                    }
                ),
                html.Button(
                    '전체 해제', 
                    id='btn-deselect-all', 
                    n_clicks=0, 
                    style={
                        'marginTop': '4px', 
                        'width': '100%'
                    }
                ),
            ], style={'width': '140px', 'marginLeft': '12px'})
        ], style={'display': 'flex', 'alignItems': 'flex-start'})
    ], style={
        'padding': '16px', 
        'backgroundColor': '#1e1e1e', 
        'borderRadius': '10px', 
        'border': '1px solid #444', 
        'marginBottom': '20px'
    })
    
    return combined_graph_block