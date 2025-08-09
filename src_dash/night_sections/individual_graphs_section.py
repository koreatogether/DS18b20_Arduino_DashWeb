"""개별 그래프 섹션 - 개별 그래프 8개"""
from dash import dcc
import plotly.graph_objects as go


def create_individual_mini_graphs():
    """각 센서별 미니 그래프 8개 생성"""
    mini_graphs = []
    
    for i in range(1, 9):
        # Placeholder figure (will be replaced by live callback)
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, visible=False),
            height=100,
            showlegend=False
        )
        
        mini_graph = dcc.Graph(
            id=f'sensor-{i}-mini-graph', 
            figure=fig, 
            style={'height': '100px'}, 
            config={'displayModeBar': False}
        )
        
        mini_graphs.append(mini_graph)
    
    return mini_graphs


def get_mini_graph_placeholder():
    """미니 그래프용 기본 플레이스홀더 figure 반환"""
    fig = go.Figure()
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False),
        height=100,
        showlegend=False
    )
    return fig