import argparse
from pathlib import Path
import os
from utils import get_srt_home  # 공통 utils import
from separate_srt import separate_srt_file  # separate_srt.py의 함수 import (직접 호출)

def separate_all_files(origin_dir, separated_dir):
    processed_count = 0
    chunk_total = 0
    for file in origin_dir.glob('*.srt'):
        chunks = separate_srt_file(file, separated_dir)
        if chunks > 0:
            processed_count += 1
            chunk_total += chunks
        else:
            print(f"스킵됨: {file} - 처리 실패")
    
    print(f"총 {processed_count}개의 SRT 파일이 처리되었습니다. (총 {chunk_total}개의 chunk 생성)")

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/origin의 모든 SRT 파일을 800개 자막 블록 chunk로 나누어 SRT_HOME/origin_separate에 저장합니다.")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    # SRT_HOME 설정
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    origin_dir = srt_home_path / 'origin'
    separated_dir = srt_home_path / 'origin_separate'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 디렉토리: {origin_dir}")
    print(f"분할 디렉토리: {separated_dir}")
    
    if not origin_dir.exists():
        print(f"오류: {origin_dir}가 존재하지 않습니다.")
        return
    
    separate_all_files(origin_dir, separated_dir)

if __name__ == "__main__":
    main()