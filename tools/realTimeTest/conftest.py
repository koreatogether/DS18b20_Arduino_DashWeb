import pytest, serial, time

@pytest.fixture(scope="session")
def ser():
    port = "COM4"
    s = serial.Serial(port, 115200, timeout=2)
    # Reset board via DTR toggle for clean state
    try:
        s.setDTR(False)
        time.sleep(0.1)
        s.setDTR(True)
    except Exception:
        pass
    time.sleep(2)
    # Clear any buffered data
    s.reset_input_buffer()
    s.reset_output_buffer()
    # Send a cancel command, then a menu command to ensure a known state
    s.write(b'c\n')
    time.sleep(0.2)
    s.write(b'menu\n')
    time.sleep(0.2)
    s.reset_input_buffer() # Clear any responses
    yield s
    s.close()

def read_output(ser, timeout=2):
    end = time.time() + timeout
    buf = ""
    while time.time() < end:
        try:
            line = ser.readline().decode('utf-8', errors='replace')
            buf += line
        except UnicodeDecodeError:
            # 디코딩 에러가 발생하면 무시하고 계속
            continue
    return buf
