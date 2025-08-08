"""
Arduino 시리얼 통신 모듈 (완전 재작성)
간단하고 안정적인 시리얼 통신 구현
"""
import serial
import json
import threading
import time
import queue
from datetime import datetime
from collections import deque
import logging


class ArduinoSerial:
    """간단하고 안정적인 Arduino 시리얼 통신 클래스"""
    
    def __init__(self, port=None, baudrate=115200):
        if port is None:
            try:
                from port_manager import find_arduino_port
                port = find_arduino_port() or 'COM4'
            except ImportError:
                port = 'COM4'
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.is_connected = False
        self.is_running = False
        
        # 데이터 저장소
        self.sensor_data = deque(maxlen=1000)
        self.system_messages = deque(maxlen=100)
        self.alerts = deque(maxlen=50)
        
        # 스레드 안전성
        self.data_lock = threading.Lock()
        self.read_thread = None
        
        # 통계
        self.total_received = 0
        self.last_data_time = None
        self.connection_time = None
        
        # 로깅
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Arduino 연결"""
        try:
            self.logger.info(f"Arduino 연결 시도: {self.port}")
            
            # 기존 연결 정리
            if self.serial_connection:
                try:
                    self.serial_connection.close()
                except:
                    pass
                time.sleep(0.5)
            
            # 새 연결 생성
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1,  # 매우 짧은 타임아웃
                write_timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # 연결 안정화
            time.sleep(1)
            
            # 버퍼 클리어
            self.serial_connection.flushInput()
            self.serial_connection.flushOutput()
            
            self.is_connected = True
            self.connection_time = datetime.now()
            self.logger.info("✅ Arduino 연결 성공!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Arduino 연결 실패: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """연결 해제"""
        self.logger.info("Arduino 연결 해제 시작...")
        
        # 읽기 중단
        self.is_running = False
        
        # 스레드 종료 대기
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
        
        # 시리얼 연결 해제
        if self.serial_connection:
            try:
                self.serial_connection.close()
            except:
                pass
            self.serial_connection = None
        
        self.is_connected = False
        self.logger.info("🔌 Arduino 연결 해제 완료")
    
    def start_reading(self):
        """데이터 읽기 시작"""
        if not self.is_connected:
            self.logger.error("Arduino가 연결되지 않았습니다")
            return False
        
        self.is_running = True
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        
        self.logger.info("📡 데이터 읽기 시작")
        return True
    
    def _read_loop(self):
        """데이터 읽기 루프 (재작성된 안정적 버전)"""
        self.logger.info("🔄 데이터 읽기 루프 시작")
        
        buffer = ""
        last_status_time = time.time()
        
        while self.is_running and self.is_connected:
            try:
                # 연결 상태 확인
                if not self.serial_connection or not self.serial_connection.is_open:
                    self.logger.warning("시리얼 연결 끊어짐")
                    self.is_connected = False
                    break
                
                # 데이터 읽기 (바이트 단위)
                if self.serial_connection.in_waiting > 0:
                    try:
                        # 한 번에 모든 대기 중인 데이터 읽기
                        data = self.serial_connection.read(self.serial_connection.in_waiting)
                        if data:
                            # 문자열로 변환하고 버퍼에 추가
                            text = data.decode('utf-8', errors='ignore')
                            buffer += text
                            
                            # 완전한 라인들 처리
                            while '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                                line = line.strip()
                                if line:
                                    self.logger.info(f"📥 수신: {line}")
                                    self._process_line(line)
                                    self.total_received += 1
                                    self.last_data_time = datetime.now()
                    
                    except UnicodeDecodeError as e:
                        self.logger.warning(f"문자 디코딩 오류: {e}")
                
                # 5초마다 상태 출력
                current_time = time.time()
                if current_time - last_status_time > 5:
                    waiting = self.serial_connection.in_waiting if self.serial_connection else 0
                    self.logger.info(f"📊 상태: 대기바이트={waiting}, 총수신={self.total_received}개")
                    last_status_time = current_time
                
                # CPU 사용률 조절
                time.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"읽기 루프 오류: {e}")
                time.sleep(0.1)
        
        self.logger.info("🔄 데이터 읽기 루프 종료")
    
    def _process_line(self, line):
        """수신된 라인 처리"""
        try:
            # JSON 형태인지 확인
            if line.startswith('{') and line.endswith('}'):
                self._handle_json(line)
            else:
                self._handle_csv(line)
        except Exception as e:
            self.logger.error(f"라인 처리 오류: {e}")
    
    def _handle_json(self, line):
        """JSON 메시지 처리"""
        try:
            data = json.loads(line)
            msg_type = data.get('type', 'unknown')
            
            with self.data_lock:
                if msg_type == 'sensor':
                    record = {
                        'timestamp': datetime.now(),
                        'sensor_id': data.get('id'),
                        'temperature': data.get('temp'),
                        'status': data.get('status', 'ok'),
                        'source': 'json'
                    }
                    self.sensor_data.append(record)
                    self.logger.info(f"✅ JSON 센서 저장: ID={record['sensor_id']}, 온도={record['temperature']}°C")
                
                elif msg_type == 'system':
                    record = {
                        'timestamp': datetime.now(),
                        'message': data.get('msg'),
                        'level': data.get('level', 'info'),
                        'source': 'json'
                    }
                    self.system_messages.append(record)
        
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON 파싱 오류: {e}")
    
    def _handle_csv(self, line):
        """CSV 메시지 처리"""
        parts = line.split(',')
        if len(parts) < 2:
            return
        
        msg_type = parts[0]
        
        with self.data_lock:
            if msg_type == 'SENSOR_DATA' and len(parts) >= 4:
                try:
                    record = {
                        'timestamp': datetime.now(),
                        'sensor_id': int(parts[1]),
                        'temperature': float(parts[2]),
                        'status': 'ok',
                        'source': 'csv'
                    }
                    self.sensor_data.append(record)
                    self.logger.info(f"✅ CSV 센서 저장: ID={record['sensor_id']}, 온도={record['temperature']}°C")
                
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"CSV 센서 데이터 파싱 오류: {e}")
            
            elif msg_type in ['SYSTEM', 'STATUS', 'HEARTBEAT']:
                record = {
                    'timestamp': datetime.now(),
                    'message': ','.join(parts[1:]) if len(parts) > 1 else line,
                    'level': 'info',
                    'source': 'csv'
                }
                self.system_messages.append(record)
    
    def get_current_temperatures(self):
        """현재 온도 데이터 반환"""
        with self.data_lock:
            current_temps = {}
            # 최신 데이터부터 역순으로 검사
            for data in reversed(self.sensor_data):
                sensor_id = data['sensor_id']
                if sensor_id not in current_temps:
                    current_temps[sensor_id] = {
                        'temperature': data['temperature'],
                        'timestamp': data['timestamp'],
                        'status': data['status']
                    }
            return current_temps
    
    def get_latest_sensor_data(self, count=50):
        """최신 센서 데이터 반환"""
        with self.data_lock:
            return list(self.sensor_data)[-count:]
    
    def get_system_messages(self, count=10):
        """시스템 메시지 반환"""
        with self.data_lock:
            return list(self.system_messages)[-count:]
    
    def is_healthy(self):
        """연결 상태 확인"""
        if not self.is_connected:
            return False
        
        # 물리적 연결 확인
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                return False
        except:
            return False
        
        # 최근 데이터 확인 (60초 이내)
        if self.last_data_time:
            time_diff = (datetime.now() - self.last_data_time).total_seconds()
            return time_diff < 60
        
        # 연결된 지 30초 이내라면 건강한 것으로 간주
        if self.connection_time:
            time_diff = (datetime.now() - self.connection_time).total_seconds()
            return time_diff < 30
        
        return False
    
    def get_connection_stats(self):
        """연결 통계 반환"""
        with self.data_lock:
            return {
                'is_connected': self.is_connected,
                'is_healthy': self.is_healthy(),
                'sensor_data_count': len(self.sensor_data),
                'system_message_count': len(self.system_messages),
                'total_received': self.total_received,
                'port': self.port,
                'baudrate': self.baudrate
            }
    
    def send_command(self, command_dict):
        """명령 전송"""
        if not self.is_connected or not self.serial_connection:
            return False
        
        try:
            json_command = json.dumps(command_dict)
            self.serial_connection.write((json_command + '\n').encode('utf-8'))
            self.logger.info(f"📤 명령 전송: {json_command}")
            return True
        except Exception as e:
            self.logger.error(f"명령 전송 실패: {e}")
            return False

    def send_text_command(self, line: str) -> bool:
        """텍스트 명령 전송 (펌웨어의 텍스트 기반 커맨드와 호환)

        Args:
            line: 줄바꿈 없이 보낼 원시 텍스트 명령 (예: "SET_ID 1 2")

        Returns:
            bool: 전송 성공 여부
        """
        if not self.is_connected or not self.serial_connection:
            return False
        try:
            self.serial_connection.write((line.strip() + '\n').encode('utf-8'))
            self.logger.info(f"📤 텍스트 명령 전송: {line}")
            return True
        except Exception as e:
            self.logger.error(f"텍스트 명령 전송 실패: {e}")
            return False


# 하위 호환성을 위한 별칭
ArduinoJSONSerial = ArduinoSerial


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 새로운 Arduino 시리얼 통신 테스트")
    
    try:
        from port_manager import find_arduino_port
        detected_port = find_arduino_port()
    except ImportError:
        detected_port = None
    arduino = ArduinoSerial(port=detected_port or 'COM4')
    
    if arduino.connect():
        arduino.start_reading()
        
        try:
            # 10초간 테스트
            for i in range(10):
                time.sleep(1)
                stats = arduino.get_connection_stats()
                current_temps = arduino.get_current_temperatures()
                
                print(f"[{i+1:2d}초] 연결={stats['is_connected']}, "
                      f"건강={arduino.is_healthy()}, "
                      f"수신={stats['total_received']}개, "
                      f"센서={len(current_temps)}개")
                
                if current_temps:
                    temp_str = ", ".join([f"ID{k}:{v['temperature']:.1f}°C" 
                                        for k, v in current_temps.items()])
                    print(f"      온도: {temp_str}")
        
        except KeyboardInterrupt:
            print("\n🛑 테스트 중단")
        
        finally:
            arduino.disconnect()
    
    else:
        print("❌ 연결 실패")