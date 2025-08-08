#ifndef ICOMMAND_PROCESSOR_H
#define ICOMMAND_PROCESSOR_H

#include <Arduino.h>

/**
 * 명령 처리 인터페이스 (DIP 적용)
 * 명령 파싱, 검증, 처리 추상화
 */
class ICommandProcessor {
public:
    virtual ~ICommandProcessor() = default;
    
    // 명령 처리
    virtual void processIncomingCommands() = 0;
    virtual bool isValidCommand(const char* command) const = 0;
    virtual bool validateParameters(const char* command) const = 0;
    
    // 명령 실행
    virtual void executeCommand(const char* command) = 0;
    virtual void sendHelpMessage() const = 0;
    
    // 상태 조회
    virtual bool getSystemStatus(char* output, int maxSize) const = 0;
    virtual void resetSystem() = 0;
};

#endif