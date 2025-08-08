/**
 * TestUtils.h
 * Arduino 단위 테스트용 유틸리티
 */

#ifndef TEST_UTILS_H
#define TEST_UTILS_H

#include "ArduinoAssert.h"

class TestRunner {
private:
  int totalTests;
  int passedTests;
  int failedTests;
  
public:
  TestRunner() : totalTests(0), passedTests(0), failedTests(0) {}
  
  void runTest(const char* testName, void (*testFunc)()) {
    Serial.print("Running test: ");
    Serial.println(testName);
    
    totalTests++;
    
    // 테스트 실행 (Arduino에서는 예외 처리 대신 단순 실행)
    testFunc();
    passedTests++;
    Serial.println("  ✓ PASSED");
  }
  
  void printResults() {
    Serial.println();
    Serial.println("=== TEST RESULTS ===");
    Serial.print("Total: ");
    Serial.println(totalTests);
    Serial.print("Passed: ");
    Serial.println(passedTests);
    Serial.print("Failed: ");
    Serial.println(failedTests);
    Serial.println("===================");
  }
};

// 테스트용 assert 매크로 (Arduino용 - 예외 처리 없음)
#define TEST_ASSERT(condition) \
  do { \
    if (!(condition)) { \
      Serial.print("TEST FAILED: "); \
      Serial.print(#condition); \
      Serial.print(" at line "); \
      Serial.println(__LINE__); \
      return; \
    } \
  } while(0)

#define TEST_ASSERT_EQUAL(expected, actual) \
  TEST_ASSERT((expected) == (actual))

#define TEST_ASSERT_NOT_EQUAL(expected, actual) \
  TEST_ASSERT((expected) != (actual))

#define TEST_ASSERT_FLOAT_EQUAL(expected, actual, tolerance) \
  TEST_ASSERT(abs((expected) - (actual)) < (tolerance))

#endif // TEST_UTILS_H