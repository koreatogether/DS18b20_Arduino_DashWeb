# /sc:test — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/test.md
라이선스: MIT. 요약 번역본.

## 목적
테스트 실행, 리포트 생성, 커버리지/품질 게이트 개선

## 입력
- 테스트 유형: 단위 | 통합 | E2E | 보안 | 성능

## 출력
- 테스트 로그, 커버리지, 실패 분석

## 주요 플래그
- --persona-qa, --play(E2E), --seq, --validate, --coverage

## 절차
1) 범위/유형 선택, 픽스처 수집
2) 테스트 실행, 로그/지표 수집
3) 실패 분석, 후속 작업 생성
4) 커버리지 갱신, 임계치 적용

## 예시
- `/sc:test --type security --play --persona-qa`
