# 2.after_trans.py (post_process_all.py 호출 추가)
import argparse
import subprocess
from pathlib import Path
import os
from utils import get_srt_home  # 공통 utils import

def run_command(cmd):
    """subprocess로 명령어 실행, 실패 시 예외 발생."""
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
    parser = argparse.ArgumentParser(description="SRT 번역 후처리: restore_all.py → merge_all.py → compare_all.py 순서로 실행합니다.")
    parser.add_argument('-t', '--target', help="compare_all.py의 mp4 검색 대상 경로 (기본: Windows V:/, Linux /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    # SRT_HOME 설정
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    # target 경로 설정
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
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
    
    # 2-5. post_process_all.py 호출 (Post-processing 전체 적용 추가)
    print("\n--- post_process_all.py 실행 ---")
    post_process_all_cmd = ['python', 'post_process_all.py', '-s', str(srt_home_path)]
    run_command(post_process_all_cmd)
    
    # 2-6. compare_all.py 호출
    print("\n--- compare_all.py 실행 ---")
    compare_all_cmd = ['python', 'compare_all.py', '-t', str(target_path), '-s', str(srt_home_path)]
    run_command(compare_all_cmd)
    
    print("\nafter_trans.py 완료")

if __name__ == "__main__":
    main()