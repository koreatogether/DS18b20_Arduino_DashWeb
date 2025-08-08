# /sc:estimate — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/estimate.md
라이선스: MIT. 요약 번역본.

## 목적
예상 작업량, 시간, 위험을 산출합니다.

## 입력
- 작업 목록, 범위, 제약조건

## 출력
- 가정, 위험, 버퍼가 포함된 추정치

## 주요 플래그
- --persona-architect | --persona-qa | --persona-performance, --seq

## 절차
1) 작업을 작은 단위로 분해
2) 기본 작업량 산출, 위험 버퍼 추가
3) 중요 경로/의존성 파악
4) 최적/예상/최악 범위와 신뢰도 제시

## 예시
- `/sc:estimate roadmap/ --persona-architect --seq`
