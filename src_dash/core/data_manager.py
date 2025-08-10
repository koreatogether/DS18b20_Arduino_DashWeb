"""데이터 스냅샷 및 시뮬레이션 관리 모듈"""

import datetime
import random
from typing import Any, Callable, Dict, List, Tuple

# Number of latest sensor data records to retrieve
SNAPSHOT_SIZE = 50


def create_snapshot_function(arduino: Any, arduino_connected_ref: Dict[str, bool]) -> Callable[
    [],
    Tuple[
        str,
        Dict[str, Any],
        Dict[int, Dict[str, Any]],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
    ],
]:
    """스냅샷 함수를 생성합니다.
    Returns:
        Callable that returns a tuple of (
            connection_status: str,
            connection_style: Dict[str, Any],
            current_temps: Dict[int, Dict[str, Any]],
            latest_data: List[Dict[str, Any]],
            system_messages: List[Dict[str, Any]]
        )
    """

    def snapshot() -> Tuple[
        str,
        Dict[str, Any],
        Dict[int, Dict[str, Any]],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
    ]:
        """Collect current data snapshot from Arduino or simulation."""
        arduino_connected = arduino_connected_ref.get("connected", False)

        # 연결 상태 실시간 검증
        if arduino_connected and not arduino.is_healthy():
            arduino_connected_ref["connected"] = False
            print("⚠️ Arduino 연결 상태 불량 감지 - 시뮬레이션 모드 전환")
        elif not arduino_connected and arduino.is_healthy():
            # 연결 상태가 False인데 실제로는 건강한 경우 (연결 상태 동기화)
            arduino_connected_ref["connected"] = True
            print("✅ Arduino 연결 상태 복구 감지 - 실제 데이터 모드 전환")
            arduino_connected = True

        if arduino_connected and arduino.is_healthy():
            stats = arduino.get_connection_stats()
            connection_status = f"🟢 Arduino 연결됨 (데이터: {stats['sensor_data_count']}개)"
            connection_style = {
                "textAlign": "center",
                "margin": "10px",
                "padding": "10px",
                "border": "2px solid green",
                "borderRadius": "5px",
                "color": "green",
            }
            current_temps = arduino.get_current_temperatures()
            latest_data = arduino.get_latest_sensor_data(count=SNAPSHOT_SIZE)
            system_messages = arduino.get_system_messages(count=10)
            print(f"🔍 실제 데이터 사용: 현재온도={len(current_temps)}개, 최신데이터={len(latest_data)}개")
        else:
            connection_status = "🔴 Arduino 연결 끊김 (시뮬레이션 모드)"
            connection_style = {
                "textAlign": "center",
                "margin": "10px",
                "padding": "10px",
                "border": "2px solid red",
                "borderRadius": "5px",
                "color": "red",
            }
            current_temps = {
                i: {
                    "temperature": round(20 + random.uniform(-5, 15), 1),
                    "status": "simulated",
                    "address": f"28FF{i:02d}1E{i:02d}16{i:02d}3C",  # 시뮬레이션용 더미 주소
                }
                for i in range(1, 5)
            }
            times = [datetime.datetime.now() - datetime.timedelta(seconds=i) for i in range(30, 0, -1)]
            latest_data = []
            for t in times:
                for sid in range(1, 5):
                    latest_data.append(
                        {
                            "timestamp": t,
                            "sensor_id": sid,
                            "temperature": 20 + random.uniform(-5, 15),
                        }
                    )
            system_messages = [
                {
                    "timestamp": datetime.datetime.now(),
                    "message": "Simulation mode active",
                    "level": "warning",
                }
            ]

        return (
            connection_status,
            connection_style,
            current_temps,
            latest_data,
            system_messages,
        )

    return snapshot
