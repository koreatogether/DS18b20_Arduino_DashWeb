"""센서 온도 섹션 - 개별 온도 창 8개"""
import dash
from dash import html, dcc
import plotly.graph_objects as go


def create_sensor_temperature_cards():
    """개별 센서 온도 카드 8개 생성"""
    sensor_cards = []
    
    for i in range(1, 9):
        # Placeholder figure (will be replaced by live callback)
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=80, t=10, b=10),
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, visible=False),
            height=100,
            showlegend=False
        )
        
        card = html.Div([
            # 온도 표시 영역
            html.Div([
                html.H4(f"센서 ID {i}", style={
                    'color': 'white', 
                    'marginBottom': '5px'
                }),
                html.P("--°C", 
                      id=f'sensor-{i}-temp', 
                      style={
                          'fontSize': '32px', 
                          'fontWeight': 'bold', 
                          'color': 'white', 
                          'margin': '0'
                      })
            ], style={'flex': '0 1 150px', 'padding': '20px'}),
            
            # 미니 그래프 영역 (개별 그래프 섹션에서 관리)
            html.Div([
                dcc.Graph(
                    id=f'sensor-{i}-mini-graph', 
                    figure=fig, 
                    style={'height': '100px'}, 
                    config={'displayModeBar': False}
                )
            ], style={'flex': '1', 'padding': '10px'}),
            
        ], style={
            'display': 'flex', 
            'alignItems': 'center', 
            'backgroundColor': '#1e1e1e', 
            'borderRadius': '10px', 
            'marginBottom': '15px', 
            'border': '1px solid #444'
        })
        
        sensor_cards.append(card)
    
    return sensor_cards