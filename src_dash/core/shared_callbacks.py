"""공통 콜백 함수들"""
import dash
from dash import html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def register_shared_callbacks(app, snapshot_func, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT):
    """공통 콜백들을 등록합니다."""
    
    @app.callback(
        [Output('connection-status','children'), Output('connection-status','style')]
        +[Output(f'sensor-{i}-temp','children') for i in range(1,9)]
        +[Output(f'sensor-{i}-status','children') for i in range(1,9)]
        +[Output('system-log','children')],
        Input('interval-component','n_intervals'), 
        State('ui-version-store','data'), 
        prevent_initial_call=True
    )
    def update_status_and_log(_n, ui_version):
        connection_status, connection_style, current_temps, _latest_data, system_messages = snapshot_func()
        sensor_temps, sensor_statuses = [], []
        
        for i in range(1,9):
            if i in current_temps:
                info = current_temps[i]
                sensor_temps.append(f"{info['temperature']:.1f}°C")
                status = info.get('status','')
                if status == 'ok': 
                    sensor_statuses.append('🟢 정상')
                elif status == 'simulated': 
                    sensor_statuses.append('🟡 시뮬레이션')
                else: 
                    sensor_statuses.append(f"⚠️ {status}")
            else:
                sensor_temps.append('--°C')
                sensor_statuses.append('🔴 연결 없음')
        
        log_entries = []
        for msg in system_messages:
            ts = msg['timestamp'].strftime('%H:%M:%S')
            level_icons = {"info":"ℹ️","warning":"⚠️","error":"❌"}
            icon = level_icons.get(msg['level'],'📝')
            log_entries.append(html.Div(f"[{ts}] {icon} {msg['message']}"))
        
        return [connection_status, connection_style] + sensor_temps + sensor_statuses + [log_entries]

    @app.callback(
        [Output('temp-graph','figure'), Output('detail-sensor-graph','figure')],
        [Input('interval-component','n_intervals'), Input('detail-sensor-dropdown','value')],
        [State('threshold-store','data'), State('ui-version-store','data')], 
        prevent_initial_call=True
    )
    def update_main_graphs(_n, detail_sensor_id, threshold_map, ui_version):
        if detail_sensor_id is None: 
            detail_sensor_id = 1
        _, _, _current_temps, latest_data, _msgs = snapshot_func()
        
        # Temp overview graph
        if latest_data:
            df = pd.DataFrame(latest_data)
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['sensor_id'] = df['sensor_id'].astype(str)
            except Exception: 
                pass
            try:
                fig = px.line(df, x='timestamp', y='temperature', color='sensor_id',
                              title='실시간 온도 모니터링 (최근 50개 데이터)', template='plotly_white')
            except Exception:
                fig = go.Figure()
                for sid, g in df.groupby('sensor_id'):
                    fig.add_trace(go.Scatter(x=g['timestamp'], y=g['temperature'], mode='lines', name=sid))
                fig.update_layout(title='실시간 온도 모니터링 (최근 50개 데이터)', template='plotly_white')
        else:
            fig = go.Figure()
            fig.update_layout(title='데이터 없음', template='plotly_white')
        
        # Add global TH/TL lines
        try:
            fig.add_hline(y=TH_DEFAULT, line_dash='dash', line_color='red', 
                         annotation_text='TH', annotation_position='top left')
            fig.add_hline(y=TL_DEFAULT, line_dash='dash', line_color='blue', 
                         annotation_text='TL', annotation_position='bottom left')
        except Exception:
            pass

        # Detail graph
        if latest_data:
            df_all = pd.DataFrame(latest_data)
            try:
                df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
                df_all['sensor_id'] = df_all['sensor_id'].astype(int)
            except Exception: 
                pass
            one = df_all[df_all['sensor_id']==detail_sensor_id]
            if not one.empty:
                try:
                    detail_fig = px.line(one, x='timestamp', y='temperature', 
                                       title=f'센서 {detail_sensor_id} 상세 그래프', template='plotly_white')
                except Exception:
                    detail_fig = go.Figure()
                    detail_fig.add_trace(go.Scatter(x=one['timestamp'], y=one['temperature'], 
                                                  mode='lines', name=f'센서 {detail_sensor_id}'))
            else:
                detail_fig = go.Figure()
                detail_fig.update_layout(title=f'센서 {detail_sensor_id} 데이터 없음', template='plotly_white')
        else:
            detail_fig = go.Figure()
            detail_fig.update_layout(title='상세 데이터 없음', template='plotly_white')
        
        try:
            detail_fig.add_hline(y=TH_DEFAULT, line_dash='dash', line_color='red')
            detail_fig.add_hline(y=TL_DEFAULT, line_dash='dash', line_color='blue')
        except Exception:
            pass
        
        fig.update_layout(height=440)
        detail_fig.update_layout(height=440)
        return fig, detail_fig

    @app.callback(
        Output('combined-graph','figure'), 
        [Input('interval-component','n_intervals'), Input('sensor-line-toggle','value')], 
        State('ui-version-store','data'), 
        prevent_initial_call=True
    )
    def update_combined_graph(_n, selected_sensor_lines, ui_version):
        # 빈 선택이면 전체 센서 표시 (전체 그래프 역할 유지)
        if not isinstance(selected_sensor_lines, list) or len(selected_sensor_lines) == 0:
            selected_sensor_lines = [i for i in range(1,9)]
        _, _, _current_temps, latest_data, _msgs = snapshot_func()
        
        if latest_data:
            try:
                df = pd.DataFrame(latest_data)
                df['sensor_id'] = df['sensor_id'].astype(int)
                # 시간 포맷을 시:분:초로만 보여주기 위해 datetime 변환
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                except Exception:
                    pass
                df = df[df['sensor_id'].isin(selected_sensor_lines)]
                fig = go.Figure()
                color_map = {int(sid): COLOR_SEQ[(sid-1)%len(COLOR_SEQ)] for sid in range(1,9)}
                for sid, g in df.groupby('sensor_id'):
                    fig.add_trace(go.Scatter(x=g['timestamp'], y=g['temperature'], mode='lines', 
                                           name=f'센서 {sid}', 
                                           line=dict(color=color_map.get(int(sid),'#888'), width=2)))
                if ui_version == 'v2':
                    fig.update_layout(title='전체 센서 실시간 온도', template='plotly_dark', height=560, 
                                    showlegend=False, plot_bgcolor='#000', paper_bgcolor='#000')
                    # 연도 제거하고 시:분:초만 표시
                    fig.update_xaxes(tickformat="%H:%M:%S")
                else:
                    fig.update_layout(title='전체 센서 실시간 온도', template='plotly_white', height=480, 
                                    showlegend=False)
                try:
                    fig.add_hline(y=TH_DEFAULT, line_dash='dash', line_color='red')
                    fig.add_hline(y=TL_DEFAULT, line_dash='dash', line_color='blue')
                except Exception:
                    pass
            except Exception:
                fig = go.Figure()
                fig.update_layout(title='전체 센서 실시간 온도 (오류)', height=480, 
                                template='plotly_dark' if ui_version=='v2' else 'plotly_white')
        else:
            fig = go.Figure()
            fig.update_layout(title='전체 센서 실시간 온도 (데이터 없음)', height=560 if ui_version=='v2' else 480, 
                            template='plotly_dark' if ui_version=='v2' else 'plotly_white')
            if ui_version=='v2':
                fig.update_xaxes(tickformat="%H:%M:%S")
        return fig

    # 콜백 충돌 방지를 위해 임시 비활성화
    # @app.callback(
    #     Output('mode-indicator', 'children'),
    #     Output('mode-feedback', 'children'),
    #     Input('ui-version-store', 'data')
    # )
    # def show_mode_indicator_and_feedback(ui_version):
    #     if ui_version == 'v2':
    #         return "현재 모드: 🌙 Night (v2)", "🌙 Night 모드로 전환됨"
    #     return "현재 모드: ☀️ Day (v1)", "☀️ Day 모드로 전환됨"
    pass