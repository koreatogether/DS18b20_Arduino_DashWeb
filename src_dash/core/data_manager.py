"""데이터 스냅샷 및 시뮬레이션 관리 모듈"""
import datetime
import random


def create_snapshot_function(arduino, arduino_connected_ref):
    """스냅샷 함수를 생성합니다."""
    
    def snapshot():
        """Collect current data snapshot from Arduino or simulation."""
        arduino_connected = arduino_connected_ref.get('connected', False)
        
        if arduino_connected and not arduino.is_healthy():
            arduino_connected_ref['connected'] = False
            print("⚠️ Arduino 연결 상태 불량 감지 - 시뮬레이션 모드 전환")
            
        if arduino_connected and arduino.is_healthy():
            stats = arduino.get_connection_stats()
            connection_status = f"🟢 Arduino 연결됨 (데이터: {stats['sensor_data_count']}개)"
            connection_style = {
                'textAlign': 'center',
                'margin': '10px',
                'padding': '10px',
                'border': '2px solid green',
                'borderRadius': '5px',
                'color': 'green'
            }
            current_temps = arduino.get_current_temperatures()
            latest_data = arduino.get_latest_sensor_data(count=50)
            system_messages = arduino.get_system_messages(count=10)
            print(f"🔍 실제 데이터 사용: 현재온도={len(current_temps)}개, 최신데이터={len(latest_data)}개")
        else:
            connection_status = "🔴 Arduino 연결 끊김 (시뮬레이션 모드)"
            connection_style = {
                'textAlign': 'center',
                'margin': '10px',
                'padding': '10px',
                'border': '2px solid red',
                'borderRadius': '5px',
                'color': 'red'
            }
            current_temps = {
                i: {
                    'temperature': round(20 + random.uniform(-5, 15), 1),
                    'status': 'simulated'
                } for i in range(1, 5)
            }
            times = [datetime.datetime.now() - datetime.timedelta(seconds=i) for i in range(30, 0, -1)]
            latest_data = []
            for t in times:
                for sid in range(1, 5):
                    latest_data.append({
                        'timestamp': t,
                        'sensor_id': sid,
                        'temperature': 20 + random.uniform(-5, 15)
                    })
            system_messages = [{
                'timestamp': datetime.datetime.now(),
                'message': 'Simulation mode active',
                'level': 'warning'
            }]
        
        return connection_status, connection_style, current_temps, latest_data, system_messages
    
    return snapshot