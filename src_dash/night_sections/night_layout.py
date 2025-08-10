"""Night Mode (v2) 레이아웃 - 섹션별로 분리된 구조"""

from dash import html

from .controls import create_control_log_section
from .main_graph import create_combined_graph_section
from .modals import create_confirm_dialog, create_interval_modal
from .sensor_cards import create_sensor_cards_with_buttons


def create_layout_v2(
    initial_port_options,
    selected_port,
    initial_port_value,
    app=None,
    arduino=None,
    arduino_connected=None,
    color_seq=None,
    th_default=None,
    tl_default=None,
    snapshot_func=None,
):
    """Night mode (v2) – dark theme; 섹션별로 분리된 구조"""
    print("🔍 [NIGHT_LAYOUT] create_layout_v2 함수 시작")

    try:
        # 1. 센서 온도 섹션 (개별 온도 창 8개) + 센서 기능 버튼 섹션 + 개별 도구 섹션
        print("🔍 [NIGHT_LAYOUT] 센서 카드 생성 중...")
        sensor_cards = create_sensor_cards_with_buttons(float(th_default or 55.0), float(tl_default or -25.0))
        print(f"✅ [NIGHT_LAYOUT] 센서 카드 {len(sensor_cards)}개 생성 완료")

        # 2. 모달 섹션 (측정 주기 선택 모달)
        print("🔍 [NIGHT_LAYOUT] 모달 섹션 생성 중...")
        interval_modal = create_interval_modal()
        confirm_dialog = create_confirm_dialog()
        print("✅ [NIGHT_LAYOUT] 모달 섹션 생성 완료")

        # 3. 종합 그래프 섹션
        print("🔍 [NIGHT_LAYOUT] 종합 그래프 섹션 생성 중...")
        combined_graph_block = create_combined_graph_section()
        print("✅ [NIGHT_LAYOUT] 종합 그래프 섹션 생성 완료")

        # 4. 제어&로그 섹션
        print("🔍 [NIGHT_LAYOUT] 제어&로그 섹션 생성 중...")
        control_panel_v2 = create_control_log_section(initial_port_options, selected_port, initial_port_value)
        print("✅ [NIGHT_LAYOUT] 제어&로그 섹션 생성 완료")

    except Exception as e:
        print(f"❌ [NIGHT_LAYOUT] 섹션 생성 중 오류: {e}")
        import traceback

        traceback.print_exc()
        raise

    # 5. 숨겨진 플레이스홀더 (공유 콜백 출력용)
    hidden_placeholders = html.Div(
        [
            html.Div(id="connection-status"),
            html.Div(id="temp-graph"),  # dcc.Graph 대신 html.Div 사용
            html.Div(id="system-log"),
            html.Div(id="detail-sensor-dropdown"),  # dcc.Dropdown 대신 html.Div 사용
            html.Div(id="detail-sensor-graph"),  # dcc.Graph 대신 html.Div 사용
            *[html.Div(id=f"sensor-{i}-status") for i in range(1, 9)],
        ],
        style={"display": "none"},
    )

    # 전체 레이아웃 구성
    return html.Div(
        style={
            "backgroundColor": "black",
            "color": "white",
            "padding": "20px",
            "height": "100vh",
            "overflowY": "scroll",
        },
        children=[
            # 헤더
            html.H2(
                "🌙 Sensor Dashboard - Night Mode (v2)",
                style={"textAlign": "center", "marginBottom": "20px"},
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
            hidden_placeholders,
        ],
    )
