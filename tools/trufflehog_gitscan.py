#!/usr/bin/env python3
# trufflehog_gitscan.py
# 깃 저장소 내 민감정보(토큰, 비밀번호 등) 자동 탐지 스크립트 (Python 버전)
# 사용법: python tools/trufflehog_gitscan.py

import os
import shutil
import subprocess
import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs', 'detection')
os.makedirs(LOG_DIR, exist_ok=True)
now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
RESULT_FILE_GIT = os.path.join(LOG_DIR, f'trufflehog_git_scan_{now}.json')
RESULT_FILE_FS = os.path.join(LOG_DIR, f'trufflehog_filesystem_scan_{now}.json')


def find_trufflehog_binary():
    """Resolve trufflehog executable. Prefer local tools/trufflehog.exe, else PATH."""
    local_exe = os.path.join(SCRIPT_DIR, 'trufflehog.exe')
    if os.path.isfile(local_exe):
        return local_exe
    # Fallback to PATH (could be trufflehog.exe or trufflehog)
    path_bin = shutil.which('trufflehog')
    if path_bin:
        return path_bin
    return None


TRUFFLEHOG_BIN = find_trufflehog_binary()
if not TRUFFLEHOG_BIN:
    print('[TruffleHog] 실행 파일을 찾지 못했습니다. tools 폴더에 trufflehog.exe를 두거나 PATH에 trufflehog를 설치하세요.')
    raise SystemExit(1)

# 1. Git 이력 검사
try:
    # Git history scan against the repository root (ensure .git present)
    result = subprocess.run([
        TRUFFLEHOG_BIN,
        '--no-update', 'git', 'file://./', '--json'
    ], cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with open(RESULT_FILE_GIT, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    if result.returncode == 0:
        print(f'[TruffleHog] Git 이력 검사 완료. 결과: {RESULT_FILE_GIT}')
        if result.stdout.strip():
            print('민감정보(시크릿) 탐지됨.')
        else:
            print('민감정보(시크릿) 탐지 없음.')
    else:
        print(f'[TruffleHog] Git 이력 검사 오류. 실행 경로: {PROJECT_ROOT}, 바이너리: {TRUFFLEHOG_BIN}')
        print(result.stderr)
        exit(1)
except Exception as e:
    print(f'[TruffleHog] Git 이력 검사 예외: {e}')
    exit(1)

# 2. 파일시스템(로컬 파일) 검사
try:
    # Filesystem scan directly on the repository root path (native Windows path is fine)
    result = subprocess.run([
        TRUFFLEHOG_BIN,
        '--no-update', 'filesystem', '--json', PROJECT_ROOT
    ], cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with open(RESULT_FILE_FS, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    if result.returncode == 0:
        print(f'[TruffleHog] 파일시스템 검사 완료. 결과: {RESULT_FILE_FS}')
        if result.stdout.strip():
            print('민감정보(시크릿) 탐지됨.')
        else:
            print('민감정보(시크릿) 탐지 없음.')
    else:
        print(f'[TruffleHog] 파일시스템 검사 오류. 실행 경로: {PROJECT_ROOT}, 바이너리: {TRUFFLEHOG_BIN}')
        print(result.stderr)
        exit(1)
except Exception as e:
    print(f'[TruffleHog] 파일시스템 검사 예외: {e}')
    exit(1)
