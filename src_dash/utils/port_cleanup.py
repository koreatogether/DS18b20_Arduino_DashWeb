"""
COM 포트 정리 유틸리티
강제 종료 시 포트 점유 문제 해결
"""

import subprocess
import time


def kill_python_processes():
    """Python 프로세스들을 안전하게 종료"""
    try:
        # Python 프로세스 찾기
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe"],
            capture_output=True,
            text=True,
        )

        if "python.exe" in result.stdout:
            print("🔍 실행 중인 Python 프로세스 발견")

            # 모든 Python 프로세스 종료
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
            print("🔪 Python 프로세스 종료 완료")

            # 포트 해제 대기
            time.sleep(2)
            print("⏳ 포트 해제 대기 완료")

        else:
            print("✅ 실행 중인 Python 프로세스 없음")

    except Exception as e:
        print(f"❌ 프로세스 정리 오류: {e}")


def check_port_status(port="COM4"):
    """포트 상태 확인"""
    try:
        import serial

        ser = serial.Serial(port, 115200, timeout=1)
        ser.close()
        print(f"✅ {port} 포트 사용 가능")
        return True
    except Exception as e:
        print(f"❌ {port} 포트 사용 불가: {e}")
        return False


if __name__ == "__main__":
    print("🧹 포트 정리 유틸리티")
    kill_python_processes()
    check_port_status()
    print("✅ 정리 완료")
