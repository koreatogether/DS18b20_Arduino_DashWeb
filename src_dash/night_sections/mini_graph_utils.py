"""미니 그래프 관련 유틸리티 함수들"""

import pandas as pd
import plotly.graph_objects as go


def prepare_dataframe(latest_data):
    """데이터프레임을 준비하고 전처리합니다."""
    if not latest_data:
        return None

    try:
        df = pd.DataFrame(latest_data)
        df["sensor_id"] = df["sensor_id"].astype(int)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except (ValueError, KeyError, TypeError):
        return pd.DataFrame(latest_data)


def calculate_y_axis_range(y_values, th_default, tl_default):
    """Y축 범위를 계산합니다."""
    try:
        vmin = float(min(y_values))
        vmax = float(max(y_values))
        vmin = min(vmin, tl_default)
        vmax = max(vmax, th_default)

        if vmin == vmax:
            vmin -= 0.5
            vmax += 0.5

        pad = (vmax - vmin) * 0.1
        return [vmin - pad, vmax + pad]
    except (ValueError, KeyError, TypeError):
        return None


def add_threshold_lines(fig, th_default, tl_default):
    """임계선을 그래프에 추가합니다."""
    # Zero line (solid, 1px, 옅은 색상)
    try:
        fig.add_hline(y=0, line_dash="solid", line_color="#ccc", line_width=1)
    except (ValueError, AttributeError):
        pass

    # TH & TL lines (dashed) - 라벨 제거하고 선만 표시
    for val, color in [(th_default, "red"), (tl_default, "blue")]:
        try:
            fig.add_hline(y=val, line_dash="dash", line_color=color)
        except (ValueError, AttributeError):
            pass


def create_empty_mini_graph():
    """데이터가 없을 때 빈 미니 그래프를 생성합니다."""
    fig = go.Figure()
    fig.add_annotation(text="데이터 없음", showarrow=False, font=dict(color="white", size=10))
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=4, r=10, t=16, b=14),
        height=170,
        xaxis=dict(title=None),
        yaxis=dict(title=None),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_sensor_mini_graph(sensor_data, sensor_id, color_seq, th_default, tl_default):
    """개별 센서의 미니 그래프를 생성합니다."""
    fig = go.Figure()

    if sensor_data.empty:
        fig.add_annotation(text="데이터 없음", showarrow=False, font=dict(color="white", size=10))
    else:
        x = sensor_data["timestamp"]
        y = sensor_data["temperature"]
        color = color_seq[(sensor_id - 1) % len(color_seq)]

        # 데이터 라인 추가
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color, width=2)))

        # Y축 범위 설정
        y_range = calculate_y_axis_range(y, th_default, tl_default)
        if y_range:
            fig.update_yaxes(range=y_range)

        # 임계선 추가
        add_threshold_lines(fig, th_default, tl_default)

        # X축 설정 (시:분:초만 표시)
        fig.update_xaxes(
            showgrid=False,
            tickfont=dict(color="#aaa"),
            nticks=4,
            tickformat="%H:%M:%S",
            ticklabelposition="outside bottom",
            ticklabelstandoff=10,
        )

        # Y축 설정 (숫자 제거)
        fig.update_yaxes(showgrid=False, tickfont=dict(color="#aaa"), nticks=3, showticklabels=False)

    # 공통 레이아웃 설정
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=4, r=10, t=16, b=14),
        height=170,
        xaxis=dict(title=None),
        yaxis=dict(title=None),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig
