# /sc:git — 사용법 (한글)

원본: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/SuperClaude/Commands/git.md
라이선스: MIT. 요약 번역본.

## 목적
Git 작업 지원: 브랜치, 커밋, PR 관리, 히스토리 분석

## 입력
- 저장소 경로, 작업 종류(브랜치/커밋/리베이스/PR)

## 출력
- Git 명령어, 메시지 제안, 안전 체크

## 주요 플래그
- --persona-devops | --persona-scribe, --validate, --safe-mode

## 절차
1) 목표/안전한 순서 파악(히스토리 손실 방지)
2) 명령 준비, 커밋 메시지 작성
3) 상태/차이 검증, 필요시 시크릿 스캔
4) 실행 및 원격 상태 확인

## 예시
- `/sc:git prepare-release --persona-devops --validate`
