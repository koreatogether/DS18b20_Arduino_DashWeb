"""
Arduino와 JSON 기반 시리얼 통신 모듈
기존 시리얼 통신을 JSON 형태로 개선
"""
import serial
import json
import threading
import time
from datetime import datetime
from collections import deque
import logging
try:
    from port_manager import safe_connect_to_port, find_arduino_port
except ImportError:
    # 포트 관리자가 없는 경우 기본 시리얼 연결 사용
    safe_connect_to_port = None
    find_arduino_port = None

class ArduinoJSONSerial:
    def __init__(self, port='COM4', baudrate=115200, buffer_size=1000):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.is_connected = False
        self.is_running = False
        
        # 데이터 버퍼 (최근 1000개 데이터 저장)
        self.sensor_data = deque(maxlen=buffer_size)
        self.system_messages = deque(maxlen=100)
        self.alerts = deque(maxlen=50)
        
        # 스레드 안전성을 위한 락
        self.data_lock = threading.Lock()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """Arduino와 시리얼 연결 (포트 관리자 또는 기본 연결)"""
        try:
            # 기존 연결 정리
            if self.serial_connection:
                try:
                    if self.serial_connection.is_open:
                        self.serial_connection.close()
                except (OSError, AttributeError):
                    pass
                self.serial_connection = None
                time.sleep(0.5)
            
            # 직접 시리얼 연결 (포트 관리자 우회)
            self.logger.info("직접 시리얼 연결 시도")
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.5,  # 짧은 타임아웃
                write_timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # 연결 후 안정화
            time.sleep(1)
            
            # DTR/RTS 설정 (Arduino 리셋 방지)
            try:
                self.serial_connection.setDTR(False)
                self.serial_connection.setRTS(False)
                time.sleep(0.1)
            except (OSError, AttributeError):
                pass  # 일부 드라이버에서 지원하지 않을 수 있음
            
            # 버퍼 클리어
            try:
                self.serial_connection.flushInput()
                self.serial_connection.flushOutput()
            except (OSError, AttributeError):
                pass
            
            self.is_connected = True
            self.connection_time = datetime.now()
            self.logger.info(f"Arduino 연결 성공: {self.port} (포트 관리자 사용)")
            return True
            
        except Exception as e:
            self.logger.error(f"Arduino 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """연결 종료 (안전한 스레드 및 포트 해제)"""
        self.logger.info("Arduino 연결 종료 시작...")
        
        # 읽기 루프 중단
        self.is_running = False
        
        # 읽기 스레드 안전하게 종료
        if hasattr(self, 'read_thread') and self.read_thread and self.read_thread.is_alive():
            self.logger.info("읽기 스레드 종료 대기...")
            try:
                self.read_thread.join(timeout=3)  # 3초 대기
                if self.read_thread.is_alive():
                    self.logger.warning("읽기 스레드가 정상 종료되지 않았습니다")
                else:
                    self.logger.info("읽기 스레드 정상 종료")
            except Exception as e:
                self.logger.warning(f"스레드 종료 중 오류: {e}")
        
        # 시리얼 연결 안전하게 해제
        if self.serial_connection:
            try:
                if hasattr(self.serial_connection, 'is_open') and self.serial_connection.is_open:
                    # 버퍼 클리어 시도
                    try:
                        self.serial_connection.flushInput()
                        self.serial_connection.flushOutput()
                    except (OSError, AttributeError):
                        pass  # 이미 닫힌 경우 무시
                    
                    # 포트 닫기
                    self.serial_connection.close()
                    self.logger.info("시리얼 포트 닫기 완료")
                    
                # 포트 완전 해제 대기
                time.sleep(0.3)
                
            except Exception as e:
                self.logger.warning(f"시리얼 포트 해제 중 오류: {e}")
            finally:
                self.serial_connection = None
        
        # 상태 초기화
        self.is_connected = False
        
        # 데이터 버퍼 클리어
        with self.data_lock:
            self.sensor_data.clear()
            self.system_messages.clear()
            self.alerts.clear()
        
        self.logger.info("Arduino 연결 완전 종료")
    
    def start_reading(self):
        """백그라운드에서 데이터 읽기 시작 (안전한 스레드 관리)"""
        if not self.is_connected:
            self.logger.error("Arduino가 연결되지 않았습니다")
            return False
        
        # 기존 스레드가 실행 중이면 먼저 정리
        if hasattr(self, 'read_thread') and self.read_thread and self.read_thread.is_alive():
            self.logger.warning("기존 읽기 스레드가 실행 중입니다. 정리 중...")
            self.is_running = False
            self.read_thread.join(timeout=2)
        
        # 새 스레드 시작
        self.is_running = True
        self.read_thread = threading.Thread(
            target=self._read_loop, 
            daemon=True,
            name="ArduinoReader"
        )
        
        try:
            self.read_thread.start()
            self.logger.info("데이터 읽기 스레드 시작")
            return True
        except Exception as e:
            self.logger.error(f"스레드 시작 실패: {e}")
            self.is_running = False
            return False
    
    def _read_loop(self):
        """시리얼 데이터 읽기 루프 (디버그 로깅 추가)"""
        consecutive_errors = 0
        max_errors = 5
        last_debug_time = time.time()
        
        self.logger.info("Arduino 데이터 읽기 루프 시작")
        
        while self.is_running and self.is_connected:
            try:
                # 연결 상태 확인
                if not self.serial_connection or not self.serial_connection.is_open:
                    self.logger.warning("시리얼 연결이 끊어졌습니다")
                    self.is_connected = False
                    break
                
                # 5초마다 연결 상태 디버그 출력
                current_time = time.time()
                if current_time - last_debug_time > 5:
                    waiting_bytes = self.serial_connection.in_waiting
                    self.logger.info(f"Arduino 상태: 대기 바이트={waiting_bytes}, 연결={self.is_connected}")
                    last_debug_time = current_time
                
                if self.serial_connection.in_waiting:
                    try:
                        line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            self.logger.info(f"Arduino에서 수신: {line}")
                            self._process_message(line)
                            consecutive_errors = 0  # 성공 시 오류 카운터 리셋
                    except Exception as read_error:
                        self.logger.warning(f"데이터 읽기 오류: {read_error}")
                        time.sleep(0.1)
                
                time.sleep(0.01)  # CPU 사용률 조절
                
            except serial.SerialException as e:
                consecutive_errors += 1
                self.logger.error(f"시리얼 통신 오류 ({consecutive_errors}/{max_errors}): {e}")
                
                if consecutive_errors >= max_errors:
                    self.logger.error("연속 오류 한계 도달, 연결 종료")
                    self.is_connected = False
                    break
                    
                time.sleep(0.5)  # 오류 시 더 긴 대기
                
            except UnicodeDecodeError as e:
                self.logger.warning(f"문자 디코딩 오류: {e}")
                time.sleep(0.01)
                
            except Exception as e:
                consecutive_errors += 1
                self.logger.error(f"예상치 못한 오류 ({consecutive_errors}/{max_errors}): {e}")
                
                if consecutive_errors >= max_errors:
                    self.logger.error("연속 오류 한계 도달, 연결 종료")
                    self.is_connected = False
                    break
                    
                time.sleep(1)
        
        self.logger.info("데이터 읽기 루프 종료")
    
    def _process_message(self, message):
        """수신된 메시지 처리"""
        try:
            # JSON 파싱 시도
            if message.startswith('{') and message.endswith('}'):
                data = json.loads(message)
                self._handle_json_message(data)
            else:
                # 기존 CSV 형태 메시지 처리 (하위 호환성)
                self._handle_csv_message(message)
                
        except json.JSONDecodeError:
            # JSON이 아닌 경우 CSV로 처리
            self._handle_csv_message(message)
        except Exception as e:
            self.logger.error(f"메시지 처리 오류: {e}")
    
    def _handle_json_message(self, data):
        """JSON 메시지 처리"""
        with self.data_lock:
            msg_type = data.get('type', 'unknown')
            timestamp = datetime.now()
            
            if msg_type == 'sensor':
                sensor_record = {
                    'timestamp': timestamp,
                    'sensor_id': data.get('id'),
                    'temperature': data.get('temp'),
                    'status': data.get('status', 'ok'),
                    'raw_data': data
                }
                self.sensor_data.append(sensor_record)
                self.logger.info(f"✅ JSON 센서 데이터 저장: ID={data.get('id')}, 온도={data.get('temp')}°C, 총 데이터={len(self.sensor_data)}개")
                
            elif msg_type == 'alert':
                alert_record = {
                    'timestamp': timestamp,
                    'sensor_id': data.get('id'),
                    'alert_type': data.get('alert'),
                    'temperature': data.get('temp'),
                    'severity': data.get('severity', 'warning'),
                    'raw_data': data
                }
                self.alerts.append(alert_record)
                
            elif msg_type == 'system':
                system_record = {
                    'timestamp': timestamp,
                    'message': data.get('msg'),
                    'level': data.get('level', 'info'),
                    'raw_data': data
                }
                self.system_messages.append(system_record)
                
            elif msg_type == 'heartbeat':
                # 하트비트 처리
                self.last_heartbeat = timestamp
                self.logger.debug(f"하트비트 수신: {data}")
    
    def _handle_csv_message(self, message):
        """기존 CSV 형태 메시지 처리 (하위 호환성)"""
        parts = message.split(',')
        if len(parts) < 2:
            return
            
        msg_type = parts[0]
        timestamp = datetime.now()
        
        with self.data_lock:
            if msg_type == 'SENSOR_DATA' and len(parts) >= 4:
                sensor_record = {
                    'timestamp': timestamp,
                    'sensor_id': int(parts[1]),
                    'temperature': float(parts[2]),
                    'status': 'ok',
                    'raw_data': {'csv': message}
                }
                self.sensor_data.append(sensor_record)
                self.logger.info(f"✅ CSV 센서 데이터 저장: ID={parts[1]}, 온도={parts[2]}°C, 총 데이터={len(self.sensor_data)}개")
                
            elif msg_type == 'ALERT' and len(parts) >= 5:
                alert_record = {
                    'timestamp': timestamp,
                    'sensor_id': int(parts[1]),
                    'alert_type': parts[2],
                    'temperature': float(parts[3]),
                    'severity': 'warning',
                    'raw_data': {'csv': message}
                }
                self.alerts.append(alert_record)
                
            elif msg_type in ['SYSTEM', 'STATUS']:
                system_record = {
                    'timestamp': timestamp,
                    'message': ','.join(parts[1:]),
                    'level': 'info',
                    'raw_data': {'csv': message}
                }
                self.system_messages.append(system_record)
    
    def send_command(self, command_dict):
        """Arduino에 JSON 명령 전송"""
        if not self.is_connected:
            return False
            
        try:
            json_command = json.dumps(command_dict)
            self.serial_connection.write((json_command + '\n').encode('utf-8'))
            self.logger.info(f"명령 전송: {json_command}")
            return True
        except Exception as e:
            self.logger.error(f"명령 전송 실패: {e}")
            return False
    
    def get_latest_sensor_data(self, sensor_id=None, count=10):
        """최신 센서 데이터 조회"""
        with self.data_lock:
            if sensor_id is None:
                return list(self.sensor_data)[-count:]
            else:
                filtered_data = [d for d in self.sensor_data if d['sensor_id'] == sensor_id]
                return filtered_data[-count:]
    
    def get_current_temperatures(self):
        """모든 센서의 현재 온도 반환"""
        with self.data_lock:
            current_temps = {}
            for data in reversed(self.sensor_data):
                sensor_id = data['sensor_id']
                if sensor_id not in current_temps:
                    current_temps[sensor_id] = {
                        'temperature': data['temperature'],
                        'timestamp': data['timestamp'],
                        'status': data['status']
                    }
            return current_temps
    
    def get_recent_alerts(self, count=10):
        """최근 알림 조회"""
        with self.data_lock:
            return list(self.alerts)[-count:]
    
    def get_system_messages(self, count=10):
        """최근 시스템 메시지 조회"""
        with self.data_lock:
            return list(self.system_messages)[-count:]
    
    def is_healthy(self):
        """연결 상태 확인 (개선된 상태 체크 + 디버그)"""
        if not self.is_connected:
            self.logger.debug("연결 상태: 연결되지 않음")
            return False
        
        # 시리얼 포트 물리적 연결 확인
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                self.is_connected = False
                self.logger.debug("연결 상태: 시리얼 포트 닫힘")
                return False
        except Exception as e:
            self.is_connected = False
            self.logger.debug(f"연결 상태: 포트 확인 오류 - {e}")
            return False
            
        # 최근 30초 내에 하트비트가 있는지 확인
        if hasattr(self, 'last_heartbeat'):
            time_diff = (datetime.now() - self.last_heartbeat).total_seconds()
            if time_diff < 30:
                self.logger.debug(f"연결 상태: 하트비트 정상 ({time_diff:.1f}초 전)")
                return True
        
        # 하트비트가 없으면 센서 데이터로 확인 (60초 여유)
        with self.data_lock:
            if self.sensor_data:
                last_data_time = self.sensor_data[-1]['timestamp']
                time_diff = (datetime.now() - last_data_time).total_seconds()
                if time_diff < 60:
                    self.logger.debug(f"연결 상태: 센서 데이터 정상 ({time_diff:.1f}초 전)")
                    return True
                else:
                    self.logger.debug(f"연결 상태: 센서 데이터 오래됨 ({time_diff:.1f}초 전)")
        
        # 연결된 지 30초 이내라면 아직 건강한 것으로 간주 (시간 연장)
        if hasattr(self, 'connection_time'):
            time_diff = (datetime.now() - self.connection_time).total_seconds()
            if time_diff < 30:  # 10초 → 30초로 연장
                self.logger.debug(f"연결 상태: 연결 초기 ({time_diff:.1f}초)")
                return True
        
        # 데이터 수신 상태 로깅
        with self.data_lock:
            data_count = len(self.sensor_data)
            msg_count = len(self.system_messages)
            self.logger.info(f"🔍 연결 상태: 불량 - 센서데이터:{data_count}개, 시스템메시지:{msg_count}개")
            
            # 최근 데이터 확인
            if self.sensor_data:
                latest = self.sensor_data[-1]
                time_diff = (datetime.now() - latest['timestamp']).total_seconds()
                self.logger.info(f"🔍 최신 센서 데이터: {time_diff:.1f}초 전, ID={latest['sensor_id']}, 온도={latest['temperature']}°C")
        
        return False
    
    def get_connection_stats(self):
        """연결 통계 정보"""
        with self.data_lock:
            return {
                'is_connected': self.is_connected,
                'is_healthy': self.is_healthy(),
                'sensor_data_count': len(self.sensor_data),
                'alert_count': len(self.alerts),
                'system_message_count': len(self.system_messages),
                'port': self.port,
                'baudrate': self.baudrate
            }

# 사용 예시 및 테스트 코드
if __name__ == "__main__":
    # Arduino JSON 시리얼 통신 테스트
    arduino = ArduinoJSONSerial(port='COM4')
    
    if arduino.connect():
        arduino.start_reading()
        
        try:
            # 10초간 데이터 수집
            time.sleep(10)
            
            # 결과 출력
            print("=== 연결 통계 ===")
            stats = arduino.get_connection_stats()
            for key, value in stats.items():
                print(f"{key}: {value}")
            
            print("\n=== 최신 센서 데이터 ===")
            latest_data = arduino.get_latest_sensor_data(count=5)
            for data in latest_data:
                print(f"센서 {data['sensor_id']}: {data['temperature']}°C at {data['timestamp']}")
            
            print("\n=== 현재 온도 ===")
            current_temps = arduino.get_current_temperatures()
            for sensor_id, info in current_temps.items():
                print(f"센서 {sensor_id}: {info['temperature']}°C ({info['status']})")
            
            print("\n=== 최근 알림 ===")
            alerts = arduino.get_recent_alerts()
            for alert in alerts:
                print(f"알림: 센서 {alert['sensor_id']} - {alert['alert_type']} ({alert['temperature']}°C)")
                
        except KeyboardInterrupt:
            print("\n테스트 중단")
        finally:
            arduino.disconnect()
    else:
        print("Arduino 연결 실패")