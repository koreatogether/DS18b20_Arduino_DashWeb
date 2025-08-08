# Python + Dash 구현 계획서

## 🎯 현재 Processing vs Dash 비교

### Processing 한계
- ❌ 데스크톱에서만 실행
- ❌ Java 기반, 메모리 사용량 많음
- ❌ 웹 배포 불가
- ❌ 모바일 지원 없음
- ❌ 복잡한 UI 컴포넌트 구현 어려움

### Dash 장점
- ✅ **웹 기반** - 브라우저에서 실행
- ✅ **모바일 반응형** - 스마트폰에서도 접근
- ✅ **원격 모니터링** - 인터넷을 통한 접근
- ✅ **강력한 시각화** - Plotly 기반 인터랙티브 그래프
- ✅ **데이터베이스 연동** - SQLite, PostgreSQL 등 쉽게 연결
- ✅ **클라우드 배포** - Heroku, AWS 등 쉬운 배포
- ✅ **Python 생태계** - pandas, numpy, scikit-learn 등 활용

## 📊 기능 매핑 테이블

| Processing 기능    | Dash 구현                         | 개선 사항                          |
| ------------------ | --------------------------------- | ---------------------------------- |
| 실시간 온도 그래프 | `dcc.Graph` + `dcc.Interval`      | 더 부드러운 애니메이션, 줌/팬 기능 |
| 센서 상태 표시     | `dash_bootstrap_components` Cards | 더 세련된 UI, 반응형               |
| 설정 팝업          | `dbc.Modal`                       | 모던한 모달 UI                     |
| 에러 알림          | `dbc.Alert` + `dbc.Toast`         | 더 직관적인 알림 시스템            |
| 시리얼 통신        | `pyserial`                        | 동일한 기능, 더 안정적             |
| 데이터 저장        | SQLite + pandas                   | 영구 저장, 데이터 분석 가능        |
| 로깅               | Python `logging` 모듈             | 구조화된 로그, 로그 레벨 관리      |

## 🏗️ 아키텍처 설계

### 1. 프로젝트 구조
```
dash_sensor_monitor/
├── app.py                 # 메인 Dash 앱
├── components/
│   ├── temperature_graph.py    # 온도 그래프 컴포넌트
│   ├── sensor_cards.py         # 센서 상태 카드
│   ├── control_panel.py        # 제어 패널
│   └── settings_modal.py       # 설정 모달
├── data/
│   ├── serial_manager.py       # 시리얼 통신 관리
│   ├── database.py            # 데이터베이스 관리
│   └── sensor_data.py         # 센서 데이터 모델
├── utils/
│   ├── config.py              # 설정 관리
│   └── logger.py              # 로깅 유틸리티
└── requirements.txt
```

### 2. 핵심 컴포넌트

#### A. 실시간 데이터 수집
```python
import serial
import threading
import sqlite3
import pandas as pd
from datetime import datetime

class SerialDataCollector:
    def __init__(self, port='COM3', baudrate=115200):
        self.serial_connection = serial.Serial(port, baudrate)
        self.is_running = False
        self.data_buffer = []
        
    def start_collection(self):
        """백그라운드에서 데이터 수집 시작"""
        self.is_running = True
        threading.Thread(target=self._collect_data, daemon=True).start()
        
    def _collect_data(self):
        """Arduino에서 데이터 읽기"""
        while self.is_running:
            if self.serial_connection.in_waiting:
                line = self.serial_connection.readline().decode().strip()
                # CSV 파싱: "SENSOR,1,25.4,timestamp"
                if line.startswith("SENSOR"):
                    parts = line.split(',')
                    sensor_data = {
                        'sensor_id': int(parts[1]),
                        'temperature': float(parts[2]),
                        'timestamp': datetime.now()
                    }
                    self.data_buffer.append(sensor_data)
```

#### B. Dash 메인 앱
```python
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 레이아웃 정의
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("DS18B20 온도 모니터링", className="text-center mb-4"),
        ], width=12)
    ]),
    
    # 센서 상태 카드들
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"센서 {i}", className="card-title"),
                    html.H2(id=f"temp-{i}", children="--°C"),
                    dbc.Badge(id=f"status-{i}", children="연결됨", 
                             color="success", className="ms-1"),
                ])
            ], className="mb-3")
        ], width=3) for i in range(1, 9)
    ]),
    
    # 실시간 그래프
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="temperature-graph")
        ], width=12)
    ]),
    
    # 제어 패널
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("시작", id="start-btn", color="success"),
                dbc.Button("정지", id="stop-btn", color="danger"),
                dbc.Button("설정", id="settings-btn", color="primary"),
            ])
        ], width=12)
    ], className="mt-3"),
    
    # 자동 업데이트를 위한 인터벌
    dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
    
    # 데이터 저장소
    dcc.Store(id="sensor-data-store"),
    
], fluid=True)

# 콜백 함수들
@app.callback(
    [Output("temperature-graph", "figure"),
     Output("sensor-data-store", "data")] +
    [Output(f"temp-{i}", "children") for i in range(1, 9)] +
    [Output(f"status-{i}", "children") for i in range(1, 9)],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    # 데이터베이스에서 최신 데이터 가져오기
    df = get_latest_sensor_data()
    
    # 그래프 업데이트
    fig = create_temperature_graph(df)
    
    # 센서별 최신 온도 및 상태 업데이트
    temp_outputs = []
    status_outputs = []
    
    for sensor_id in range(1, 9):
        sensor_df = df[df['sensor_id'] == sensor_id]
        if not sensor_df.empty:
            latest_temp = sensor_df.iloc[-1]['temperature']
            temp_outputs.append(f"{latest_temp:.1f}°C")
            status_outputs.append("연결됨")
        else:
            temp_outputs.append("--°C")
            status_outputs.append("연결 끊김")
    
    return [fig, df.to_dict('records')] + temp_outputs + status_outputs
```

#### C. 인터랙티브 그래프
```python
def create_temperature_graph(df):
    """Plotly 기반 인터랙티브 온도 그래프 생성"""
    fig = go.Figure()
    
    # 센서별 라인 추가
    for sensor_id in df['sensor_id'].unique():
        sensor_data = df[df['sensor_id'] == sensor_id]
        fig.add_trace(go.Scatter(
            x=sensor_data['timestamp'],
            y=sensor_data['temperature'],
            mode='lines+markers',
            name=f'센서 {sensor_id}',
            line=dict(width=2),
            hovertemplate='<b>센서 %s</b><br>'
                         '온도: %{y:.1f}°C<br>'
                         '시간: %{x}<br>'
                         '<extra></extra>' % sensor_id
        ))
    
    fig.update_layout(
        title="실시간 온도 모니터링",
        xaxis_title="시간",
        yaxis_title="온도 (°C)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig
```

### 3. 데이터베이스 설계
```python
import sqlite3
import pandas as pd

class SensorDatabase:
    def __init__(self, db_path="sensor_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id INTEGER NOT NULL,
                temperature REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                is_valid BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_config (
                sensor_id INTEGER PRIMARY KEY,
                name TEXT,
                upper_limit REAL DEFAULT 30.0,
                lower_limit REAL DEFAULT 10.0,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_reading(self, sensor_id, temperature):
        """센서 읽기 데이터 삽입"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_readings (sensor_id, temperature, timestamp)
            VALUES (?, ?, datetime('now'))
        ''', (sensor_id, temperature))
        
        conn.commit()
        conn.close()
    
    def get_recent_data(self, hours=1):
        """최근 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query('''
            SELECT * FROM sensor_readings 
            WHERE timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp
        '''.format(hours), conn)
        
        conn.close()
        return df
```

## 🎨 UI/UX 개선 사항

### 1. 반응형 디자인
- **Bootstrap 기반**: 모바일, 태블릿, 데스크톱 최적화
- **다크 모드 지원**: 사용자 선호도에 따른 테마 변경
- **접근성**: 시각 장애인을 위한 스크린 리더 지원

### 2. 향상된 시각화
- **실시간 애니메이션**: 부드러운 데이터 업데이트
- **인터랙티브 기능**: 줌, 팬, 범례 토글
- **경고 시각화**: 임계값 초과 시 색상 변경

### 3. 사용자 경험
- **설정 저장**: 브라우저 로컬 스토리지 활용
- **알림 시스템**: 브라우저 푸시 알림
- **데이터 내보내기**: CSV, Excel 형태로 다운로드

## 🚀 배포 및 확장성

### 1. 로컬 개발
```bash
pip install dash plotly pandas pyserial sqlite3
python app.py
# http://localhost:8050 에서 접근
```

### 2. 클라우드 배포 (Heroku)
```bash
# Procfile
web: gunicorn app:server

# requirements.txt
dash==2.16.1
plotly==5.17.0
pandas==2.1.4
gunicorn==21.2.0
```

### 3. 고급 기능 확장
- **다중 사용자**: Flask-Login 통합
- **API 엔드포인트**: RESTful API 제공
- **머신러닝**: 온도 예측, 이상 감지
- **IoT 확장**: MQTT, InfluxDB 연동

## 📊 성능 비교

| 항목          | Processing | Dash  |
| ------------- | ---------- | ----- |
| 실행 속도     | ⭐⭐⭐        | ⭐⭐⭐⭐  |
| 메모리 사용량 | ⭐⭐         | ⭐⭐⭐⭐  |
| 확장성        | ⭐⭐         | ⭐⭐⭐⭐⭐ |
| 사용자 경험   | ⭐⭐⭐        | ⭐⭐⭐⭐⭐ |
| 개발 생산성   | ⭐⭐         | ⭐⭐⭐⭐⭐ |
| 유지보수성    | ⭐⭐         | ⭐⭐⭐⭐⭐ |

## 🎯 결론

**Python + Dash가 현재 Processing 프로젝트보다 우수한 선택입니다!**

### 즉시 얻을 수 있는 이점:
1. **웹 기반 접근성** - 어디서나 브라우저로 접근
2. **모던한 UI** - 더 세련되고 직관적인 인터페이스
3. **확장성** - 데이터베이스, 클라우드, API 쉽게 연동
4. **개발 효율성** - Python 생태계의 풍부한 라이브러리

### 마이그레이션 전략:
1. **단계적 이전**: 핵심 기능부터 차례로 구현
2. **병렬 개발**: Processing과 Dash 동시 개발로 안정성 확보
3. **데이터 호환성**: 동일한 Arduino 코드 사용으로 데이터 일관성 유지
