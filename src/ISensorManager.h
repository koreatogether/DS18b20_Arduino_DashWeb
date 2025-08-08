#ifndef ISENSOR_MANAGER_H
#define ISENSOR_MANAGER_H

#include <Arduino.h>

/**
 * 센서 관리 인터페이스 (DIP 적용)
 * 센서 스캔, 데이터 읽기, 상태 관리 추상화
 */
class ISensorManager {
public:
    virtual ~ISensorManager() = default;
    
    // 센서 초기화 및 스캔
    virtual void initialize() = 0;
    virtual void scanSensors() = 0;
    
    // 센서 데이터 읽기
    virtual void updateSensorData() = 0;
    virtual float readSensorTemperature(int sensorIndex) = 0;
    
    // 센서 상태 관리
    virtual void monitorHealth() = 0;
    virtual int getSensorCount() const = 0;
    virtual bool isSensorConnected(int sensorId) const = 0;
    
    // 센서 설정
    virtual bool setSensorInterval(int sensorId, unsigned long interval) = 0;
    virtual unsigned long getSensorInterval(int sensorId) const = 0;
    virtual void resetSensorErrors() = 0;
    
    // 센서 정보 조회
    virtual bool getSensorInfo(int sensorId, char* output, int maxSize) const = 0;
    virtual bool getAllSensorIntervals(char* output, int maxSize) const = 0;
};

#endif