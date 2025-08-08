# /sc:design — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/design.md
라이선스: MIT. 요약 번역본.

## 목적
아키텍처/설계 대안 제시, 장단점 비교, 최적안 추천

## 입력
- 문제 정의, 제약조건, 품질 속성

## 출력
- 대안, 의사결정표, 선택안, 다음 단계

## 주요 플래그
- --persona-architect, --think-hard | --ultrathink, --seq, --c7

## 절차
1) 요구사항/제약조건 파악
2) 2~3가지 대안 제시, 장단점 비교
3) 선택 및 근거, 인터페이스/경계 정의
4) 마일스톤/검증 기준 계획

## 예시
- `/sc:design "multi-sensor data pipeline" --persona-architect --ultrathink --seq`
