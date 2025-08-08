# /sc:explain — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/explain.md
라이선스: MIT. 요약 번역본.

## 목적
코드, 오류, 시스템을 대상 독자에게 쉽게 설명합니다.

## 입력
- 대상 파일/코드/로그, 독자 수준

## 출력
- 단계별 설명, 예시 포함

## 주요 플래그
- --persona-mentor, --c7, --think

## 절차
1) 독자/상황 파악
2) 핵심 요소/흐름 추출
3) 비유/예시로 설명
4) 참고자료/학습 경로 제시

## 예시
- `/sc:explain src/CommandProcessor.cpp --persona-mentor --c7`
