/**
 * SecureCommunication.h
 * 상용급 보안 통신 클래스
 */

#ifndef SECURE_COMMUNICATION_H
#define SECURE_COMMUNICATION_H

#include <Arduino.h>
#include <crc32.h>

// 메시지 헤더 구조체
struct SecureMessageHeader
{
    uint8_t magic[4] = {'D', 'S', '1', '8'}; // 고정 매직 번호
    uint16_t sequence;                       // 시퀀스 번호
    uint16_t length;                         // 페이로드 길이
    uint32_t timestamp;                      // 타임스탬프
    uint32_t crc32;                          // CRC32 체크섬
} __attribute__((packed));

class SecureCommunication
{
private:
    uint16_t current_sequence = 0;
    uint32_t last_received_sequence = 0;
    uint32_t message_timeout_ms = 5000;

    // 재전송 관리
    struct PendingMessage
    {
        uint16_t sequence;
        uint32_t timestamp;
        uint8_t retry_count;
        char message[256];
        bool waiting_ack;
    };

    static const uint8_t MAX_PENDING = 8;
    PendingMessage pending_messages[MAX_PENDING];

public:
    SecureCommunication();

    // 보안 메시지 전송
    bool sendSecureMessage(const char *payload);
    bool sendWithRetry(const char *payload, uint8_t max_retries = 3);

    // 메시지 수신 및 검증
    bool receiveSecureMessage(char *payload, size_t max_length);
    bool validateMessage(const SecureMessageHeader &header, const char *payload);

    // ACK 처리
    void sendAck(uint16_t sequence);
    void handleAck(uint16_t sequence);
    void processRetransmissions();

    // 보안 기능
    uint32_t calculateCRC32(const char *data, size_t length);
    bool isSequenceValid(uint16_t sequence);
    void resetCommunication();

    // 통신 상태
    uint8_t getConnectionQuality();
    uint32_t getLastActivityTime();

private:
    uint16_t getNextSequence() { return ++current_sequence; }
    int8_t findPendingMessage(uint16_t sequence);
    void removePendingMessage(uint16_t sequence);
    void addPendingMessage(uint16_t sequence, const char *message);
};

#endif // SECURE_COMMUNICATION_H
