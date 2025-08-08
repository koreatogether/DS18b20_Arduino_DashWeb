# 🌡️ DS18B20 Multi-Sensor Management System

[![Arduino](https://img.shields.io/badge/Arduino-UNO%20R4%20WiFi-00979D?style=flat&logo=arduino&logoColor=white)](https://www.arduino.cc/)
[![PlatformIO](https://img.shields.io/badge/PlatformIO-Compatible-orange?style=flat&logo=platformio&logoColor=white)](https://platformio.org/)
[![C++](https://img.shields.io/badge/C++-17-blue?style=flat&logo=cplusplus&logoColor=white)](https://isocpp.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python&logoColor=white)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-7%20Scenarios%20Passing-brightgreen?style=flat)](tools/realTimeTest/)

> **Professional-grade multi-sensor temperature monitoring system with interactive menu interface and comprehensive test automation**

## ✨ Key Features

🔥 **Multi-Sensor Support** - Manage up to 8 DS18B20 sensors simultaneously  
🎛️ **Interactive Menu System** - Intuitive serial interface for sensor control  
🔧 **Dynamic ID Management** - Individual/batch sensor ID assignment and validation  
📊 **Real-time Monitoring** - Live sensor status table with 15-second updates  
🛡️ **Robust Error Handling** - Input validation, duplicate prevention, connection verification  
🧪 **Automated Testing** - Python-based real-time test framework with 7 comprehensive scenarios  
🏗️ **Clean Architecture** - Layered design with dependency injection patterns  
⚡ **Cross-Platform** - Compatible with PlatformIO and Arduino IDE  

## 🚀 Quick Start

### Hardware Requirements
- Arduino UNO R4 WiFi
- DS18B20 temperature sensors (1-8 units)
- 4.7kΩ pull-up resistor
- OneWire bus connection (Pin 2)

### Software Setup

#### Option 1: PlatformIO (Recommended)
```bash
# Clone the repository
git clone https://github.com/yourusername/DS18B20_Embedded_Application.git
cd DS18B20_Embedded_Application

# Build and upload
pio run --target upload

# Monitor serial output
pio device monitor
```

#### Option 2: Arduino IDE
1. Install required libraries:
   - DallasTemperature (^4.0.3)
   - OneWire (^2.3.7)
   - ArduinoJson (^6.21.3)
2. Open `src/DS18B20_Embedded_ApplicationV2.ino`
3. Select board: Arduino UNO R4 WiFi
4. Upload to device

## 🎮 Usage

### Menu Navigation
```
Serial Monitor (115200 baud) → Type 'm' or 'menu' → Enter
```

### Main Menu Structure
```
===== 센서 제어 메뉴 =====
1. 센서 ID 조정
2. 상/하한 온도 조정
3. 취소 / 상태창으로 돌아가기

--- 센서 ID 조정 메뉴 ---
1. 개별 센서 ID 변경      ← Change individual sensor ID
2. 복수의 센서 ID 변경    ← Batch sensor ID changes
3. 주소순 자동 ID 할당    ← Auto-assign IDs by address
4. 전체 ID 초기화         ← Reset all sensor IDs
5. 이전 메뉴 이동         ← Back to main menu
6. 상태창으로 돌아가기    ← Return to status display
```

### Real-time Status Display
```
| 번호 | ID  | 센서 주소           | 현재 온도 | 상한설정온도 | 상한초과상태 | 하한설정온도 | 하한초과상태 | 센서상태 |
| ---- | --- | ------------       | --------- | ------------ | ------------ | ------------ | ------------ | -------- |
| 1    | 1   | 0x28FF1234567890AB | 25.3°C    | 30.0°C       | 정상         | 20.0°C       | 정상         | 정상     |
| 2    | 2   | 0x28FF9876543210CD | 22.1°C    | 30.0°C       | 정상         | 20.0°C       | 정상         | 정상     |
```

## 🧪 Testing Framework

### Automated Test Scenarios
Our comprehensive test suite includes 7 real-time scenarios:

| Scenario | Description | Coverage |
|----------|-------------|----------|
| **01** | Individual sensor ID change flow | Basic functionality |
| **02** | Multi-sensor ID change flow | Batch operations |
| **03** | Individual sensor complex scenarios | Error handling |
| **04** | Multi-sensor complex scenarios | Advanced workflows |
| **05** | Boundary value testing | Edge cases (min/max values) |
| **06** | Edge case testing | Invalid inputs, duplicates |
| **07** | Dynamic sensor testing | Hardware-agnostic tests |

### Running Tests
```bash
# Run specific scenario
python tools/realTimeTest/pyTestStart.py 01_sensor_individual_id_change_flow.json

# Run all scenarios
for i in {01..07}; do
    python tools/realTimeTest/pyTestStart.py $(ls tools/realTimeTest/scenarioJson/${i}_*.json)
done
```

### Test Features
- 🔄 **Automatic board reset** via DTR signal
- 📝 **JSON-based scenarios** for declarative test definitions
- 🔍 **Serial communication testing** with real hardware
- 📊 **Comprehensive logging** with timestamped results
- 🛡️ **State validation** and error recovery

## 🏗️ Architecture

### System Design
```
┌─────────────────────────────────────────┐
│         Application Layer               │  ← SensorController, MenuController
├─────────────────────────────────────────┤
│           Domain Layer                  │  ← Business logic & validation
├─────────────────────────────────────────┤
│       Infrastructure Layer             │  ← DS18B20 hardware interface
├─────────────────────────────────────────┤
│            HAL Layer                    │  ← OneWire communication
└─────────────────────────────────────────┘
```

### Key Components
- **SensorController**: Manages sensor discovery, ID assignment, and monitoring
- **MenuController**: Handles user interface and state management
- **Real-time Test Engine**: Python-based automated testing framework

## 📊 Project Statistics

- **Lines of Code**: ~2,000+ (C++ firmware)
- **Test Coverage**: 7 comprehensive scenarios
- **Supported Sensors**: Up to 8 DS18B20 units
- **Menu States**: 8 different application states
- **Documentation**: 10+ detailed guides and troubleshooting docs

## 🛠️ Development

### Prerequisites
- PlatformIO Core 6.0+
- Python 3.8+ (for testing)
- Arduino UNO R4 WiFi
- DS18B20 sensors

### Build Configuration
```ini
[env:uno_r4_wifi]
platform = renesas-ra
board = uno_r4_wifi
framework = arduino
lib_deps = 
    milesburton/DallasTemperature@^4.0.3
    paulstoffregen/OneWire@^2.3.7
    ArduinoJson@^6.21.3
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests to ensure compatibility
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📚 Documentation

### 📖 User Guides
- [**Quick Start Guide**](docs/Plan/01_environment_setup_guide.md) - Get up and running in minutes
- [**Menu Flow Diagram**](tools/realTimeTest/menuFlow.md) - Visual guide to menu navigation
- [**Testing Guide**](tools/realTimeTest/README.md) - Comprehensive testing documentation

### 🔧 Developer Resources
- [**Architecture Design**](docs/Plan/02_core_feature_design.md) - System architecture and design patterns
- [**Troubleshooting Guide**](tools/realTimeTest/howFixExtreamError.md) - Common issues and solutions
- [**Test Scenario Development**](tools/realTimeTest/howFix05-06-07.md) - Creating new test scenarios

### 🐛 Problem Resolution
- [**Extreme Error Resolution**](tools/realTimeTest/howFixExtreamError.md) - Critical issue debugging
- [**Scenario 05-07 Fixes**](tools/realTimeTest/howFix05-06-07.md) - Specific test scenario solutions
- [**Scenario 03 Modifications**](tools/realTimeTest/howToFix_03-secenario.md) - Individual scenario fixes

## 🎯 Use Cases

### Industrial Applications
- **HVAC Systems**: Multi-zone temperature monitoring
- **Food Storage**: Cold chain monitoring with alerts
- **Laboratory Equipment**: Precise temperature control
- **Greenhouse Automation**: Climate monitoring and control

### Educational Projects
- **IoT Learning**: Real-world sensor integration
- **Embedded Systems**: State machine and menu design
- **Test Automation**: Hardware-in-the-loop testing
- **Clean Architecture**: Professional software design patterns

## 🏆 Why Choose This Project?

✅ **Production-Ready**: Comprehensive error handling and validation  
✅ **Well-Tested**: 7 automated test scenarios covering all functionality  
✅ **Documented**: Extensive documentation with troubleshooting guides  
✅ **Maintainable**: Clean architecture with clear separation of concerns  
✅ **Extensible**: Easy to add new sensors or modify functionality  
✅ **Educational**: Great learning resource for embedded systems development  

## 📈 Roadmap

- [ ] **Web Interface**: Browser-based sensor monitoring dashboard
- [ ] **Data Logging**: SD card storage for historical data
- [ ] **Wireless Communication**: WiFi-based remote monitoring
- [ ] **Alert System**: Email/SMS notifications for threshold violations
- [ ] **Mobile App**: Smartphone interface for sensor control

## 🤝 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/yourusername/DS18B20_Embedded_Application/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/DS18B20_Embedded_Application/discussions)
- 📖 **Wiki**: [Project Wiki](https://github.com/yourusername/DS18B20_Embedded_Application/wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DallasTemperature Library** - Excellent DS18B20 sensor support
- **OneWire Library** - Reliable OneWire communication
- **PlatformIO** - Outstanding development platform
- **Arduino Community** - Continuous inspiration and support

---

<div align="center">

**⭐ Star this repository if you find it useful! ⭐**

[Report Bug](https://github.com/yourusername/DS18B20_Embedded_Application/issues) · [Request Feature](https://github.com/yourusername/DS18B20_Embedded_Application/issues) · [Documentation](docs/)

</div>