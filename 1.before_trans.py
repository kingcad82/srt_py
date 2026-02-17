# 1.before_trans.py
# 새 버전: base_filename 폴더 구조 전체 지원

import argparse
import subprocess
from pathlib import Path
import os
from utils import get_srt_home

def run_command(cmd):
    """subprocess 실행 (Windows 한글 출력 호환)"""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=False)
        try:
            stdout = result.stdout.decode('cp949')
            stderr = result.stderr.decode('cp949')
        except UnicodeDecodeError:
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
        
        print(stdout)
        if stderr:
            print(f"경고: {stderr}")
    except subprocess.CalledProcessError as e:
        print(f"오류: 명령어 실행 실패 - {e}")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="SRT 번역 전처리 전체 흐름 (base 폴더 구조 지원)\n"
                    "collect_srt → rename_all → post_process_all → trim_repeats → separate_all"
    )
    parser.add_argument('-t', '--target', help="collect_srt 검색 대상 경로")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    parser.add_argument('-l', '--lang', required=True, 
                        help="언어 코드 (e.g. ja) - 필수")
    parser.add_argument('-c', '--chunk-size', type=int, default=800, 
                        help="separate 시 chunk 크기 (기본 800)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
    print("="*60)
    print(">> before_trans.py 시작 (base 폴더 구조)")
    print(f"SRT_HOME     : {srt_home_path}")
    print(f"검색 경로    : {target_path}")
    print(f"언어 코드    : {args.lang}")
    print(f"chunk 크기   : {args.chunk_size}")
    print("="*60)
    
    # 1. collect_srt.py
    print("\n[1/5] collect_srt.py 실행...")
    run_command(['python', 'collect_srt.py', '-t', str(target_path), '-s', str(srt_home_path)])
    
    # 2. rename_all.py
    print("\n[2/5] rename_all.py 실행...")
    run_command(['python', 'rename_all.py', '-l', args.lang, '-s', str(srt_home_path)])
    
    # 3. post_process_all.py
    print("\n[3/5] post_process_all.py 실행...")
    run_command(['python', 'post_process_all.py', '-s', str(srt_home_path)])
    
    # 4. trim_repeats_srt.py
    print("\n[4/5] trim_repeats_srt.py 실행...")
    run_command(['python', 'trim_repeats_srt.py', '-s', str(srt_home_path)])
    
    # 5. separate_all.py
    print("\n[5/5] separate_all.py 실행...")
    run_command(['python', 'separate_all.py', '-s', str(srt_home_path), '-c', str(args.chunk_size)])
    
    print("\n>> before_trans.py 모든 단계 완료!")
    print(f"   -> origin_separate/base/ 폴더에 chunk 파일들이 준비되었습니다.")

if __name__ == "__main__":
    main()