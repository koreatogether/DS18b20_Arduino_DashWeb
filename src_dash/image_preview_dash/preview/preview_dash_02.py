"""
DS18B20 대시보드 UI 미리보기 - 다크 테마 모바일 스타일
실제 Arduino 연결 없이 UI만 확인할 수 있는 간단한 버전
"""
import datetime
import random
import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Dash 앱 초기화
app = dash.Dash(__name__)

# 시뮬레이션 데이터 생성 함수
def generate_sensor_data(sensor_id):
    """개별 센서용 시뮬레이션 데이터 생성"""
    data = []
    base_temp = 25.0 + (sensor_id * 0.5)  # 센서별 기본 온도
    
    # 최근 50개 포인트 생성
    for i in range(50, 0, -1):
        # 사인파 + 노이즈로 자연스러운 온도 변화 생성
        temp = base_temp + 2 * random.sin(i * 0.1) + random.uniform(-1, 1)
        data.append(round(temp, 1))
    
    return data

# 현재 온도 시뮬레이션
def get_current_temps():
    """현재 온도 시뮬레이션 데이터"""
    return {
        i: {
            'temperature': round(25.0 + (i * 0.5) + random.uniform(-0.5, 0.5), 1),
            'status': 'normal'
        } for i in range(1, 9)
    }

# 다크 테마 스타일 정의
dark_theme = {
    'backgroundColor': '#1e1e1e',
    'color': '#ffffff',
    'fontFamily': 'Arial, sans-serif'
}

sensor_card_style = {
    'backgroundColor': '#2d2d2d',
    'border': '1px solid #444',
    'borderRadius': '8px',
    'padding': '15px',
    'margin': '10px 0',
    'color': '#ffffff'
}

# 기본 레이아웃 - 다크 테마 모바일 스타일
app.layout = html.Div([
    # 센서 섹션들
    html.Div(id='sensor-sections', children=[
        html.Div([
            # 센서 정보 (왼쪽)
            html.Div([
                html.Div(f"Section {i} 01", style={
                    'fontSize': '12px', 
                    'color': '#888',
                    'marginBottom': '5px'
                }),
                html.Div(id=f'sensor-{i}-temp', children="25.6°C", style={
                    'fontSize': '28px',
                    'fontWeight': 'bold',
                    'color': '#ffffff',
                    'marginBottom': '10px'
                }),
            ], style={
                'width': '80px',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'padding': '10px'
            }),
            
            # 그래프 영역 (중앙)
            html.Div([
                html.Div([
                    html.Span("ID 변경", style={
                        'backgroundColor': '#444',
                        'padding': '2px 8px',
                        'borderRadius': '4px',
                        'fontSize': '10px',
                        'marginRight': '5px'
                    }),
                    html.Span(f"Line {i}", style={
                        'color': '#888',
                        'fontSize': '10px'
                    })
                ], style={'marginBottom': '5px'}),
                
                html.Div([
                    html.Span("상/하한 임계값 변경", style={
                        'backgroundColor': '#444',
                        'padding': '2px 8px',
                        'borderRadius': '4px',
                        'fontSize': '10px',
                        'marginRight': '5px'
                    })
                ], style={'marginBottom': '5px'}),
                
                html.Div([
                    html.Span("측정 주기 변경", style={
                        'backgroundColor': '#444',
                        'padding': '2px 8px',
                        'borderRadius': '4px',
                        'fontSize': '10px'
                    })
                ], style={'marginBottom': '10px'}),
                
                # 미니 그래프
                dcc.Graph(
                    id=f'mini-graph-{i}',
                    style={'height': '80px'},
                    config={'displayModeBar': False}
                )
            ], style={
                'flex': '1',
                'padding': '10px'
            }),
            
            # 설정 아이콘 (우측)
            html.Div([
                html.Div("🔧", style={
                    'fontSize': '20px',
                    'color': '#888',
                    'cursor': 'pointer'
                })
            ], style={
                'width': '40px',
                'display': 'inline-block',
                'textAlign': 'center',
                'verticalAlign': 'middle',
                'padding': '10px'
            })
            
        ], style={
            **sensor_card_style,
            'display': 'flex',
            'alignItems': 'center'
        })
        for i in range(1, 9)
    ]),
    
    # 제어 패널
    html.Div([
        html.H3("제어 패널", style={'color': '#ffffff', 'marginBottom': '15px'}),
        
        # 포트 연결
        html.Div([
            html.Span("포트 연결", style={'color': '#ffffff', 'marginRight': '10px'}),
            html.Span("포트 선택", style={'color': '#888', 'marginRight': '10px'}),
            html.Button("COM1", style={
                'backgroundColor': '#444',
                'color': '#ffffff',
                'border': 'none',
                'padding': '5px 15px',
                'borderRadius': '4px',
                'marginRight': '10px'
            }),
            html.Button("연결", style={
                'backgroundColor': '#555',
                'color': '#ffffff',
                'border': 'none',
                'padding': '5px 15px',
                'borderRadius': '4px'
            })
        ], style={'marginBottom': '20px'})
    ], style={
        **sensor_card_style,
        'margin': '20px 0'
    }),
    
    # 시스템 로그
    html.Div([
        html.H3("시스템 로그", style={'color': '#ffffff', 'marginBottom': '15px'}),
        html.Div(id='system-log', style={
            'backgroundColor': '#333',
            'border': '1px solid #555',
            'borderRadius': '4px',
            'padding': '15px',
            'height': '150px',
            'overflow': 'auto',
            'fontFamily': 'monospace',
            'fontSize': '12px',
            'color': '#ffffff'
        })
    ], style={
        **sensor_card_style,
        'margin': '20px 0'
    }),

    # 자동 갱신
    dcc.Interval(
        id='interval-component',
        interval=2000,  # 2초마다 갱신
        n_intervals=0
    ),
], style={
    **dark_theme,
    'padding': '20px',
    'minHeight': '100vh'
})

# 실시간 데이터 업데이트 콜백
@callback(
    [Output('system-log', 'children')] +
    [Output(f'sensor-{i}-temp', 'children') for i in range(1, 9)] +
    [Output(f'mini-graph-{i}', 'figure') for i in range(1, 9)],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n_intervals):
    """대시보드 업데이트 (시뮬레이션 데이터 사용)"""
    
    # 현재 온도 데이터
    current_temps = get_current_temps()
    
    # 센서별 온도 업데이트
    sensor_temps = []
    mini_graphs = []

    for i in range(1, 9):
        if i in current_temps:
            temp_info = current_temps[i]
            sensor_temps.append(f"{temp_info['temperature']:.1f}°C")
        else:
            sensor_temps.append("--°C")
        
        # 각 센서별 미니 그래프 생성
        sensor_data = generate_sensor_data(i)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=sensor_data,
            mode='lines',
            line=dict(color='#00ff88', width=2),
            showlegend=False
        ))
        
        fig.update_layout(
            plot_bgcolor='#2d2d2d',
            paper_bgcolor='#2d2d2d',
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                color='#888'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#444',
                showticklabels=False,
                zeroline=False,
                color='#888'
            ),
            height=80
        )
        
        mini_graphs.append(fig)

    # 시스템 로그 생성
    current_time = datetime.datetime.now()
    log_entries = [
        html.Div(f"[{current_time.strftime('%H:%M:%S')}] 시스템 시작됨", 
                style={'color': '#00ff88', 'marginBottom': '5px'}),
        html.Div(f"[{current_time.strftime('%H:%M:%S')}] 센서 데이터 수신 중...", 
                style={'color': '#ffffff', 'marginBottom': '5px'}),
        html.Div(f"[{current_time.strftime('%H:%M:%S')}] 모든 센서 정상 작동", 
                style={'color': '#00ff88', 'marginBottom': '5px'}),
        html.Div(f"[{current_time.strftime('%H:%M:%S')}] 데이터 업데이트 완료", 
                style={'color': '#888', 'marginBottom': '5px'}),
    ]

    return [log_entries] + sensor_temps + mini_graphs

if __name__ == '__main__':
    print("🎨 DS18B20 대시보드 UI 미리보기 시작")
    print("🌐 웹 인터페이스: http://127.0.0.1:8051")
    print("💡 이것은 UI 미리보기용입니다. 실제 Arduino 연결은 되지 않습니다.")
    print("💡 Ctrl+C로 종료하세요")
    
    try:
        app.run(debug=False, host='127.0.0.1', port=8051, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 UI 미리보기를 종료합니다")