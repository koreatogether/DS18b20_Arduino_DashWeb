# /sc:implement — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/implement.md
라이선스: MIT. 요약 번역본.

## 목적
기획/명세에 따라 기능을 코드로 구현합니다.

## 입력
- 명세/이슈, 대상 모듈, 완료 기준

## 출력
- 코드 변경, 테스트, 변경 내역

## 주요 플래그
- --persona-backend|frontend, --seq, --validate, --safe-mode

## 절차
1) 요구사항 확인, 인터페이스 파악
2) 점진적 구현, 테스트 포함
3) 빌드/테스트/정적 체크
4) 변경점/영향 요약

## 예시
- `/sc:implement feature:sensor-calibration --seq --validate`
