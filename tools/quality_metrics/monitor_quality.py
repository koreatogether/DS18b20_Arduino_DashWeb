#!/usr/bin/env python3
"""
DS18B20 Embedded Application - Automated Quality Monitoring Script (Python Version)
"""
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_cmd(cmd, cwd=None, shell=True, check=True):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=shell)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)
    return result.returncode

def run_and_tee(cmd, logfile, check=True):
    '''Run a shell command, stream output to both terminal and logfile (like tee).'''
    print(f"$ {cmd}")
    with open(logfile, 'w', encoding='utf-8') as f:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in process.stdout:
            print(line, end='')
            f.write(line)
        process.stdout.close()
        returncode = process.wait()
        if check and returncode != 0:
            print(f"❌ Command failed: {cmd}")
            sys.exit(returncode)
        return returncode

def main():

    print("🔍 DS18B20 Quality Monitoring Started")
    print("==================================")
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏰ Start Time: {start_time}")

    script_dir = Path(__file__).parent.resolve()
    project_root = (script_dir / '../..').resolve()
    os.chdir(project_root)
    print(f"📁 Project Root: {project_root}")

    # 로그 디렉토리 생성
    (project_root / 'logs/quality').mkdir(parents=True, exist_ok=True)
    (project_root / 'logs/comfile').mkdir(parents=True, exist_ok=True)
    (project_root / 'test/logs').mkdir(parents=True, exist_ok=True)

    print("")
    print("🔨 Step 1: Building and Testing")
    print("===============================")

    # 1. 빌드 실행 및 로그 저장 (tee)
    print("⚙️ Building for Arduino UNO R4 WiFi...")
    build_log = project_root / 'logs/comfile/compile_results.txt'
    ret = run_and_tee('pio run -e uno_r4_wifi -v', build_log)
    if ret == 0:
        print("✅ Build completed successfully")
    else:
        print("❌ Build failed")
        sys.exit(1)

    # 2. 테스트 실행 및 로그 저장 (tee) — only if [env:native] exists
    print("")
    print("🧪 Running unit tests...")
    has_native = False
    ini_path = project_root / 'platformio.ini'
    if ini_path.exists():
        try:
            with open(ini_path, 'r', encoding='utf-8') as f:
                has_native = '[env:native]' in f.read()
        except Exception:
            has_native = False
    if has_native:
        test_log = project_root / 'test/logs/test_results_clean.txt'
        ret = run_and_tee('pio test -e native -v', test_log)
        if ret == 0:
            print("✅ Tests completed")
        else:
            print("❌ Tests failed")
            sys.exit(1)
    else:
        print("ℹ️ No [env:native] in platformio.ini. Skipping tests.")

    print("")
    print("📊 Step 2: Quality Metrics Analysis")
    print("==================================")

    # 3-a. 민감정보(시크릿) 스캔
    print("🔒 Running secret scan (TruffleHog)...")
    secret_scan = project_root / 'tools' / 'trufflehog_gitscan.py'
    if secret_scan.exists():
        run_cmd(f'python "{secret_scan}"', check=False)
    else:
        print("ℹ️ Secret scan script not found, skipping.")

    # 3-b. C/C++ robust 정적 분석 (cppcheck via PlatformIO)
    print("🧰 Running C/C++ static analysis (cppcheck)...")
    quality_dir = project_root / 'logs' / 'quality'
    cppcheck_log = quality_dir / 'cppcheck_robust_results.txt'
    robust_script = project_root / 'tools' / 'robust_cppcheck.py'
    if robust_script.exists():
        run_cmd(f'python "{robust_script}"', check=False)
    else:
        run_and_tee('pio check --flags="--enable=all --inconclusive --force --std=c++17 --exclude=.pio/libdeps --exclude=lib"', cppcheck_log, check=False)

    # 3-c. 품질 메트릭 실행
    print("📈 Running quality metrics analysis...")
    run_cmd('python tools/quality_metrics/code_metrics.py')

    # 4. 트렌드 분석
    print("")
    print("📈 Running trend analysis...")
    try:
        run_cmd('python tools/quality_metrics/trend_analyzer.py', check=False)
        print("✅ Trend analysis completed")
    except Exception:
        print("⚠️ Trend analysis failed (this is okay for first run)")

    print("")
    print("📋 Step 3: Summary Report")
    print("========================")

    # 최신 품질 메트릭 결과 표시
    metrics_files = sorted((project_root / 'logs/quality').glob('metrics_*.json'), reverse=True)
    if metrics_files:
        latest_metrics = metrics_files[0]
        import json
        with open(latest_metrics, 'r', encoding='utf-8') as f:
            data = json.load(f)
        quality_score = data.get('quality_score', 0)
        test_success = data.get('test_metrics', {}).get('test_success_rate', 0)
        ram_usage = data.get('build_metrics', {}).get('ram_usage_percent', 0)
        flash_usage = data.get('build_metrics', {}).get('flash_usage_percent', 0)
        print("📊 Quality Summary:")
        print(f"  Overall Quality Score: {quality_score:.1f}/100")
        print(f"  Test Success Rate: {test_success:.1f}%")
        print(f"  RAM Usage: {ram_usage:.1f}%")
        print(f"  Flash Usage: {flash_usage:.1f}%")
        if quality_score >= 90:
            print("🎉 Excellent quality! Keep up the good work!")
        elif quality_score >= 80:
            print("✅ Good quality. Minor improvements possible.")
        elif quality_score >= 70:
            print("⚠️ Acceptable quality. Consider improvements.")
        else:
            print("🚨 Quality needs improvement!")
    else:
        print("❌ No quality metrics found")

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("")
    print(f"⏰ End Time: {end_time}")
    print("✅ Quality monitoring completed successfully!")
    report_files = sorted((project_root / 'logs/quality').glob('quality_report_*.md'), reverse=True)
    latest_report = report_files[0] if report_files else 'No report found'
    print(f"📄 Latest report: {latest_report}")

if __name__ == '__main__':
    main()
