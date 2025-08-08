# /sc:cleanup — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/cleanup.md
라이선스: MIT. 요약 번역본.

## 목적
기술 부채 감소: 불필요한 코드 제거, 단순화, 표준화

## 입력
- 범위: 경로/모듈
- 대상: 미사용 코드, 경고, 중복

## 출력
- 정리된 파일, 리팩터/제거 내역

## 주요 플래그
- --persona-refactorer, --think, --seq, --validate

## 절차
1) 문제 영역 탐색(죽은 코드, 중복 등)
2) 안전한 변경 순서 계획, 필요시 억제 구문 추가
3) 실행: 작은 단위, 되돌릴 수 있게 커밋, 동작 유지
4) 검증: 빌드/테스트/정적 분석

## 예시
- `/sc:cleanup src/ --persona-refactorer --seq --validate`
