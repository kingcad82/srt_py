# rename_all.py
# 새 버전: base_filename 폴더 구조 전체 지원 (origin/{base}/ 안의 모든 파일 rename)

import argparse
from pathlib import Path
from utils import get_srt_home
from rename_srt import rename_srt_file   # 단일 rename 함수 import

def rename_all_files(origin_parent: Path, lang: str):
    renamed_count = 0
    failed_files = []
    
    # 하위 base 폴더까지 모두 검색 (rglob)
    for file in origin_parent.rglob("*.srt"):
        if rename_srt_file(file, lang, origin_parent):
            renamed_count += 1
        else:
            failed_files.append(file.name)
            print(f"이름 변경 실패: {file}")
    
    print(f"\n총 {renamed_count}개의 SRT 파일 이름이 변경되었습니다.")
    if failed_files:
        print("\n실패한 파일 목록:")
        for failed in failed_files:
            print(f"  - {failed}")

def main():
    parser = argparse.ArgumentParser(
        description="SRT_HOME/origin 아래 모든 base 폴더의 SRT 파일을 base.lang.srt로 변경합니다."
    )
    parser.add_argument('-l', '--lang', required=True, 
                        help="언어 코드 (e.g. ja) - 필수")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_parent = srt_home_path / 'origin'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"대상 디렉토리: {origin_parent} (하위 base 폴더 포함)")
    print(f"언어 코드: {args.lang}\n")
    
    if not origin_parent.exists():
        print(f"오류: {origin_parent} 폴더가 존재하지 않습니다.")
        return
    
    rename_all_files(origin_parent, args.lang)

if __name__ == "__main__":
    main()