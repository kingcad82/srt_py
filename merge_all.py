import argparse
from pathlib import Path
import os
from utils import get_srt_home, get_base_filename  # 공통 utils import
from merge_srt import merge_srt_file  # merge_srt.py의 함수 import (직접 호출)

def merge_all_files(origin_separate_dir, trans_separate_dir, trans_dir):
    # unique base_filename 추출 (중복 피함, .ja 등 포함)
    base_filenames = set()
    for file in origin_separate_dir.glob('*.srt'):
        base = get_base_filename(file.stem)  # e.g., HMN-520.ja_000 → HMN-520
        base_filenames.add(base)
    
    processed_count = 0
    failed_bases = []
    for base in sorted(base_filenames):
        # lang=None으로 자동 감지 호출
        if merge_srt_file(base, None, origin_separate_dir, trans_separate_dir, trans_dir):
            processed_count += 1
        else:
            failed_bases.append(base)
            print(f"병합 실패: {base}")
    
    print(f"총 {processed_count}개의 base_filename이 병합되었습니다.")
    if failed_bases:
        print("\n실패한 base_filename 목록:")
        for failed in failed_bases:
            print(f"- {failed}")

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/origin_separate의 모든 base_filename을 대상으로 merge_srt.py를 실행합니다. base_filename 자동 추출 후 병합 (lang 자동 감지).")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    origin_separate_dir = srt_home_path / 'origin_separate'
    trans_separate_dir = srt_home_path / 'trans_separate'
    trans_dir = srt_home_path / 'trans'
    
    print(f"검색 경로: {origin_separate_dir}")
    print(f"SRT_HOME: {srt_home_path}")
    
    if not origin_separate_dir.exists():
        print(f"오류: {origin_separate_dir}가 존재하지 않습니다.")
        return
    
    merge_all_files(origin_separate_dir, trans_separate_dir, trans_dir)

if __name__ == "__main__":
    main()