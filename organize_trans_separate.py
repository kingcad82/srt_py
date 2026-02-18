# organize_trans_separate.py
# trans_separate 루트에 있는 .srt 파일들을 basename 폴더로 정렬
# (2.after_trans.py 실행 직전에 호출되어야 함)

import argparse
import shutil
from pathlib import Path
from utils import get_srt_home, get_base_from_path, get_base_dir

def organize_trans_separate(trans_separate_dir: Path):
    """trans_separate 루트 아래 .srt 파일을 basename 폴더로 정렬"""
    
    # trans_separate 루트 바로 아래의 .srt 파일만 찾기 (재귀 없음)
    root_srt_files = list(trans_separate_dir.glob("*.srt"))
    
    if not root_srt_files:
        print("[INFO] trans_separate 루트에 정렬할 파일이 없습니다.")
        return True
    
    print(f"[정렬 시작] {len(root_srt_files)}개 파일을 찾았습니다.\n")
    
    moved_count = 0
    failed_files = []
    
    for srt_file in root_srt_files:
        try:
            # basename 추출 (파일명에서 언어 코드와 chunk 번호 제거)
            base = get_base_from_path(srt_file)
            
            # 목표 폴더 경로
            target_dir = get_base_dir(trans_separate_dir, base)
            target_file = target_dir / srt_file.name
            
            # 같은 파일명이 이미 목표 폴더에 있으면 스킵
            if target_file.exists():
                print(f"[SKIP] {srt_file.name}")
                print(f"       → trans_separate/{base}/{srt_file.name} 파일이 이미 존재합니다.\n")
                continue
            
            # 파일 이동
            shutil.move(str(srt_file), str(target_file))
            print(f"[MOVE] {srt_file.name}")
            print(f"       → trans_separate/{base}/{srt_file.name}\n")
            moved_count += 1
            
        except Exception as e:
            print(f"[ERROR] {srt_file.name} - {e}\n")
            failed_files.append(srt_file.name)
    
    print("="*70)
    print(f"[정렬 완료] 이동: {moved_count}개, 실패: {len(failed_files)}개")
    if failed_files:
        print(f"실패 파일:")
        for f in failed_files:
            print(f"  - {f}")
    print("="*70)
    
    return len(failed_files) == 0

def main():
    parser = argparse.ArgumentParser(
        description="trans_separate 루트의 .srt 파일을 basename 폴더로 정렬"
    )
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    trans_separate_dir = srt_home_path / 'trans_separate'
    
    print(f"SRT_HOME     : {srt_home_path}")
    print(f"trans_separate: {trans_separate_dir}\n")
    
    if not trans_separate_dir.exists():
        print(f"오류: {trans_separate_dir} 폴더가 존재하지 않습니다.")
        return False
    
    return organize_trans_separate(trans_separate_dir)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
