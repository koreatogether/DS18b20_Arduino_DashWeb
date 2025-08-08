/**
 * SensorTests.cpp
 * SensorManager 단위 테스트 (임시 비활성화)
 */

// 테스트 기능 임시 비활성화 - ArduinoAssert 라이브러리 의존성 해결 후 재활성화
#ifdef ENABLE_TESTS

#include "TestUtils.h"
#include "SensorManager.h"

extern SensorManager sensorManager;

void testTemperatureValidation()
{
  // 유효한 온도 테스트
  TEST_ASSERT(sensorManager.isValidTemperature(25.0));
  TEST_ASSERT(sensorManager.isValidTemperature(-10.0));
  TEST_ASSERT(sensorManager.isValidTemperature(100.0));

  // 감시값 테스트
  TEST_ASSERT(!sensorManager.isValidTemperature(INVALID_TEMPERATURE));
  TEST_ASSERT(!sensorManager.isValidTemperature(DEVICE_DISCONNECTED_C));

  // 범위 밖 값 테스트
  TEST_ASSERT(!sensorManager.isValidTemperature(-60.0));
  TEST_ASSERT(!sensorManager.isValidTemperature(130.0));
}

void testSensorIdValidation()
{
  // 유효한 ID 테스트
  TEST_ASSERT(sensorManager.isValidSensorId(1));
  TEST_ASSERT(sensorManager.isValidSensorId(8));

  // 무효한 ID 테스트
  TEST_ASSERT(!sensorManager.isValidSensorId(0));
  TEST_ASSERT(!sensorManager.isValidSensorId(9));
  TEST_ASSERT(!sensorManager.isValidSensorId(-1));
}

void testSensorIndexValidation()
{
  // 유효한 인덱스 테스트
  TEST_ASSERT(sensorManager.isValidSensorIndex(0));
  TEST_ASSERT(sensorManager.isValidSensorIndex(7));

  // 무효한 인덱스 테스트
  TEST_ASSERT(!sensorManager.isValidSensorIndex(-1));
  TEST_ASSERT(!sensorManager.isValidSensorIndex(8));
}

void testThresholdValidation()
{
  // 유효한 임계값 설정 테스트
  TEST_ASSERT(sensorManager.setThresholds(0, 80.0, 20.0));
  TEST_ASSERT(sensorManager.setThresholds(1, 50.0, -10.0));

  // 무효한 임계값 설정 테스트 (상한 <= 하한)
  TEST_ASSERT(!sensorManager.setThresholds(0, 20.0, 80.0));
  TEST_ASSERT(!sensorManager.setThresholds(0, 25.0, 25.0));
}

void runAllSensorTests()
{
  TestRunner testRunner;

  testRunner.runTest("Temperature Validation", testTemperatureValidation);
  testRunner.runTest("Sensor ID Validation", testSensorIdValidation);
  testRunner.runTest("Sensor Index Validation", testSensorIndexValidation);
  testRunner.runTest("Threshold Validation", testThresholdValidation);

  testRunner.printResults();
}

#endif // ENABLE_TESTS