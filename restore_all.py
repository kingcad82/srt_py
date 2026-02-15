# restore_all.py
# 새 버전: base_filename 폴더 구조 전체 지원

import argparse
from pathlib import Path
from utils import get_srt_home
from restore_srt import restore_srt_file   # 단일 restore 함수 import

def restore_all_files(origin_separate_dir: Path, trans_separate_dir: Path):
    processed_count = 0
    skipped_files = []
    
    # origin_separate 아래 모든 base 폴더의 chunk 파일 검색
    for file in origin_separate_dir.rglob("*.srt"):
        base = get_base_from_path(file)  # utils에서 import 필요
        
        trans_file = trans_separate_dir / base / file.name
        
        if not trans_file.exists():
            skipped_files.append(str(file))
            print(f"스킵됨: {file.name} → trans_separate/{base}/에 해당 파일 없음")
            continue
        
        if restore_srt_file(file, origin_separate_dir, trans_separate_dir):
            processed_count += 1
        else:
            print(f"처리 실패: {file.name}")
    
    print(f"\n=== restore_all 완료 ===")
    print(f"성공: {processed_count}개 파일")
    if skipped_files:
        print(f"스킵: {len(skipped_files)}개")
        print("스킵된 파일 목록:")
        for f in skipped_files:
            print(f"  - {f}")

def main():
    parser = argparse.ArgumentParser(
        description="SRT_HOME/origin_separate 아래 모든 base 폴더의 chunk 파일을 restore합니다."
    )
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_separate_dir = srt_home_path / 'origin_separate'
    trans_separate_dir = srt_home_path / 'trans_separate'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"origin_separate: {origin_separate_dir}")
    print(f"trans_separate : {trans_separate_dir}\n")
    
    if not origin_separate_dir.exists():
        print(f"오류: {origin_separate_dir} 폴더가 존재하지 않습니다.")
        return
    
    restore_all_files(origin_separate_dir, trans_separate_dir)

if __name__ == "__main__":
    main()