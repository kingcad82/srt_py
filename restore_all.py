import argparse
from pathlib import Path
import os
from utils import get_srt_home  # 공통 utils import
from restore_srt import restore_srt_file  # restore_srt.py의 함수 import (직접 호출)

def restore_all_files(origin_separate_dir, trans_separate_dir):
    processed_count = 0
    skipped_files = []
    for file in origin_separate_dir.glob('*.srt'):
        trans_file = trans_separate_dir / file.name
        if not trans_file.exists():
            skipped_files.append(file.name)
            print(f"스킵됨: {file.name} - SRT_HOME/trans_separate에 해당 파일 없음")
            continue
        
        if restore_srt_file(file, origin_separate_dir, trans_separate_dir):
            processed_count += 1
        else:
            print(f"처리 실패: {file.name}")
    
    print(f"총 {processed_count}개의 SRT 파일이 복원되었습니다.")
    if skipped_files:
        print("\n스킵된 파일 목록:")
        for skipped in skipped_files:
            print(f"- {skipped}")

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/origin_separate의 모든 SRT 파일을 대상으로 restore_srt.py를 실행합니다. trans_separate에 없는 파일은 스킵하고 목록 출력.")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    origin_separate_dir = srt_home_path / 'origin_separate'
    trans_separate_dir = srt_home_path / 'trans_separate'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 분할 디렉토리: {origin_separate_dir}")
    print(f"번역 분할 디렉토리: {trans_separate_dir}")
    
    if not origin_separate_dir.exists():
        print(f"오류: {origin_separate_dir}가 존재하지 않습니다.")
        return
    
    restore_all_files(origin_separate_dir, trans_separate_dir)

if __name__ == "__main__":
    main()