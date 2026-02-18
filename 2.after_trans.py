# 2.after_trans.py
# 새 버전: base_filename 폴더 구조 전체 지원

import argparse
import subprocess
from pathlib import Path
import os
import sys
from utils import get_srt_home

def run_command(cmd):
    """subprocess 실행 (Windows 한글 출력 호환 강화)"""
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
        try:
            print("stdout:", e.stdout.decode('utf-8', errors='replace'))
            print("stderr:", e.stderr.decode('utf-8', errors='replace'))
        except:
            pass
        raise

def main():
    parser = argparse.ArgumentParser(
        description="SRT 번역 후처리 전체 흐름 (base 폴더 구조 지원)\n"
                    "restore_all → merge_all → compare_all"
    )
    parser.add_argument('-t', '--target', help="compare_all의 MP4 검색 대상 경로")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    # 기본 MP4 검색 경로를 X: 드라이브로 변경 (Windows)
    target_path = Path(args.target) if args.target else (Path('X:/') if os.name == 'nt' else Path('/home'))
    
    # Windows 콘솔 한글 출력 설정
    if os.name == 'nt':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    print("="*70)
    print(">> after_trans.py 시작 (base 폴더 구조)")
    print(f"SRT_HOME     : {srt_home_path}")
    print(f"MP4 검색 경로 : {target_path}")
    print("="*70)
    
    # 0. organize_trans_separate.py (최우선)
    print("\n[0/4] organize_trans_separate.py 실행...")
    run_command(['python', 'organize_trans_separate.py', '-s', str(srt_home_path)])
    
    # 1. restore_all.py
    print("\n[1/4] restore_all.py 실행...")
    run_command(['python', 'restore_all.py', '-s', str(srt_home_path)])
    
    # 2. merge_all.py
    print("\n[2/4] merge_all.py 실행...")
    run_command(['python', 'merge_all.py', '-s', str(srt_home_path)])
    
    # 3. compare_all.py
    print("\n[3/4] compare_all.py 실행...")
    run_command(['python', 'compare_all.py', '-t', str(target_path), '-s', str(srt_home_path)])
    
    print("\n>> after_trans.py 모든 단계 완료!")
    print("   -> trans_separate 파일 정렬 완료")
    print("   -> 최종 SRT가 MP4와 같은 폴더로 이동되었습니다.")
    print("   -> SRT_HOME 내 관련 파일/폴더가 자동 정리되었습니다.")

if __name__ == "__main__":
    main()