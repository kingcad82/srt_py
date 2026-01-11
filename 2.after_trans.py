# 2.after_trans.py (수정: subprocess 출력 bytes 캡처 후 cp949 또는 utf-8 디코딩 시도, Windows 호환 강화)
import argparse
import subprocess
from pathlib import Path
import os
import sys  # sys.stdout 재인코딩
from utils import get_srt_home  # 공통 utils import

def run_command(cmd):
    """subprocess로 명령어 실행, Windows 한글 깨짐 방지 (bytes 캡처 후 디코딩 시도)."""
    try:
        # bytes로 캡처 (text=False), 인코딩 문제 방지
        result = subprocess.run(cmd, check=True, capture_output=True, text=False)
        
        # stdout/stderr 디코딩 시도: 먼저 cp949 (Windows 한국어 기본), 실패 시 utf-8 with replace
        try:
            stdout = result.stdout.decode('cp949')
            stderr = result.stderr.decode('cp949')
        except UnicodeDecodeError:
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
        
        print(stdout)
        if stderr:
            print(f"\n경고: {stderr}")
    except subprocess.CalledProcessError as e:
        # 에러 시도 동일 디코딩
        try:
            stdout_err = e.stdout.decode('cp949') if e.stdout else ''
            stderr_err = e.stderr.decode('cp949') if e.stderr else ''
        except UnicodeDecodeError:
            stdout_err = e.stdout.decode('utf-8', errors='replace') if e.stdout else ''
            stderr_err = e.stderr.decode('utf-8', errors='replace') if e.stderr else ''
        
        print(f"오류: 명령어 실행 실패 - {e}")
        print(f"stdout: {stdout_err}")
        print(f"stderr: {stderr_err}")
        raise

def main():
    parser = argparse.ArgumentParser(description="SRT 번역 후처리: restore_all.py → merge_all.py → compare_all.py 순서로 실행합니다.")
    parser.add_argument('-t', '--target', help="compare_all.py의 mp4 검색 대상 경로 (기본: Windows V:/, Linux /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
    # Windows 콘솔/리다이렉트 호환: utf-8 재인코딩
    if os.name == 'nt':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    elif os.name == 'posix':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    print(f"after_trans.py 시작")
    print(f"SRT_HOME: {srt_home_path}")
    print(f"target 경로: {target_path}")
    
    # 2-2. restore_all.py 호출
    print("\n--- restore_all.py 실행 ---")
    restore_all_cmd = ['python', 'restore_all.py', '-s', str(srt_home_path)]
    run_command(restore_all_cmd)
    
    # 2-4. merge_all.py 호출
    print("\n--- merge_all.py 실행 ---")
    merge_all_cmd = ['python', 'merge_all.py', '-s', str(srt_home_path)]
    run_command(merge_all_cmd)
    
    # 2-6. compare_all.py 호출
    print("\n--- compare_all.py 실행 ---")
    compare_all_cmd = ['python', 'compare_all.py', '-t', str(target_path), '-s', str(srt_home_path)]
    run_command(compare_all_cmd)
    
    print("\nafter_trans.py 완료")

if __name__ == "__main__":
    main()