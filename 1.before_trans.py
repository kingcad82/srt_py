import argparse
import subprocess
from pathlib import Path
import os
from utils import get_srt_home

def run_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"경고: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"오류: 명령어 실행 실패 - {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise

def main():
    parser = argparse.ArgumentParser(description="SRT 번역 전처리: collect_srt.py → trim_repeats_srt.py → separate_all.py 순서로 실행합니다.")
    parser.add_argument('-t', '--target', help="collect_srt.py의 검색 대상 경로 (기본: Windows V:/, Linux /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
    print(f"before_trans.py 시작")
    print(f"SRT_HOME: {srt_home_path}")
    print(f"target 경로: {target_path}")
    
    # 1-1. collect_srt.py 호출
    print("\n--- collect_srt.py 실행 ---")
    collect_cmd = ['python', 'collect_srt.py', '-t', str(target_path), '-s', str(srt_home_path)]
    run_command(collect_cmd)
    
    # 추가: trim_repeats_srt.py 호출 (origin 파일 정리)
    print("\n--- trim_repeats_srt.py 실행 ---")
    trim_cmd = ['python', 'trim_repeats_srt.py', '-s', str(srt_home_path)]
    run_command(trim_cmd)
    
    # 1-3. separate_all.py 호출
    print("\n--- separate_all.py 실행 ---")
    separate_all_cmd = ['python', 'separate_all.py', '-s', str(srt_home_path)]
    run_command(separate_all_cmd)
    
    print("\nbefore_trans.py 완료")

if __name__ == "__main__":
    main()