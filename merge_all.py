# merge_all.py
# 새 버전: base_filename 폴더 구조 전체 지원

import argparse
from pathlib import Path
from utils import get_srt_home, get_base_from_path
from merge_srt import merge_srt_file   # 단일 merge 함수 import

def merge_all_files(origin_separate_dir: Path, trans_separate_dir: Path, trans_dir: Path):
    # unique base_filename 추출 (모든 chunk에서 base 추출)
    base_filenames = set()
    for file in origin_separate_dir.rglob("*.srt"):
        base = get_base_from_path(file)
        base_filenames.add(base)
    
    processed_count = 0
    failed_bases = []
    
    for base in sorted(base_filenames):
        print(f"병합 처리 중 → {base}")
        if merge_srt_file(base, None, origin_separate_dir, trans_separate_dir, trans_dir):
            processed_count += 1
        else:
            failed_bases.append(base)
            print(f"   → 병합 실패: {base}")
    
    print(f"\n=== merge_all 완료 ===")
    print(f"성공: {processed_count}개 base")
    if failed_bases:
        print(f"실패: {len(failed_bases)}개")
        print("실패 목록:")
        for b in failed_bases:
            print(f"  - {b}")

def main():
    parser = argparse.ArgumentParser(
        description="origin_separate 아래 모든 base_filename을 자동으로 찾아 chunk를 병합합니다. (trans/{base}/base.srt)"
    )
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_separate_dir = srt_home_path / 'origin_separate'
    trans_separate_dir = srt_home_path / 'trans_separate'
    trans_dir = srt_home_path / 'trans'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"origin_separate: {origin_separate_dir}")
    print(f"출력 디렉토리: {trans_dir}\n")
    
    if not origin_separate_dir.exists():
        print(f"오류: {origin_separate_dir} 폴더가 존재하지 않습니다.")
        return
    
    merge_all_files(origin_separate_dir, trans_separate_dir, trans_dir)

if __name__ == "__main__":
    main()