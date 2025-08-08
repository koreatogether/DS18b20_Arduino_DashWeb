#!/usr/bin/env python3
# trufflehog_gitscan.py
# 깃 저장소 내 민감정보(토큰, 비밀번호 등) 자동 탐지 스크립트 (Python 버전)
# 사용법: python tools/trufflehog_gitscan.py

import os
import subprocess
import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs', 'detection')
os.makedirs(LOG_DIR, exist_ok=True)
now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
RESULT_FILE_GIT = os.path.join(LOG_DIR, f'trufflehog_git_scan_{now}.json')
RESULT_FILE_FS = os.path.join(LOG_DIR, f'trufflehog_filesystem_scan_{now}.json')

# 1. Git 이력 검사
try:
    result = subprocess.run([
        os.path.join(SCRIPT_DIR, 'trufflehog.exe'),
        '--no-update', 'git', 'file://./', '--json'
    ], cwd=SCRIPT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with open(RESULT_FILE_GIT, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    if result.returncode == 0:
        print(f'[TruffleHog] Git 이력 검사 완료. 결과: {RESULT_FILE_GIT}')
        if 'SourceMetadata' in result.stdout:
            print('민감정보(시크릿) 탐지됨.')
        else:
            print('민감정보(시크릿) 탐지 없음.')
    else:
        print(f'[TruffleHog] Git 이력 검사 오류. tools 폴더에 trufflehog.exe가 있는지 확인하세요.')
        print(result.stderr)
        exit(1)
except Exception as e:
    print(f'[TruffleHog] Git 이력 검사 예외: {e}')
    exit(1)

# 2. 파일시스템(로컬 파일) 검사
try:
    fs_scan_path = PROJECT_ROOT.replace('\\', '/').replace(':', '')
    # Windows 드라이브 문자 제거 후 /로 시작하도록 (ex: /e/Project_DS18b20/...)
    if not fs_scan_path.startswith('/'):
        fs_scan_path = '/' + fs_scan_path
    result = subprocess.run([
        os.path.join(SCRIPT_DIR, 'trufflehog.exe'),
        '--no-update', 'filesystem', '--json', fs_scan_path
    ], cwd=SCRIPT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with open(RESULT_FILE_FS, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    if result.returncode == 0:
        print(f'[TruffleHog] 파일시스템 검사 완료. 결과: {RESULT_FILE_FS}')
        if 'SourceMetadata' in result.stdout:
            print('민감정보(시크릿) 탐지됨.')
        else:
            print('민감정보(시크릿) 탐지 없음.')
    else:
        print(f'[TruffleHog] 파일시스템 검사 오류. 실행 경로: {PROJECT_ROOT}, 바이너리: {os.path.join(SCRIPT_DIR, 'trufflehog.exe')}')
        print(result.stderr)
        exit(1)
except Exception as e:
    print(f'[TruffleHog] 파일시스템 검사 예외: {e}')
    exit(1)
