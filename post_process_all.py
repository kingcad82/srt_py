# post_process_all.py
# 새 버전: base_filename 폴더 구조 전체 지원 (rglob 사용)

import argparse
from pathlib import Path
from utils import get_srt_home
from post_process_srt import post_process_srt_file   # 단일 처리 함수 import

def post_process_all_files(origin_parent: Path):
    processed_count = 0
    total_files = 0
    
    # origin 아래 모든 base 폴더의 .srt 파일을 재귀적으로 검색
    for file in origin_parent.rglob("*.srt"):
        total_files += 1
        if post_process_srt_file(file):
            processed_count += 1
        else:
            print(f"스킵됨: {file}")
    
    print(f"\nPost-processing 완료!")
    print(f"총 검색된 파일: {total_files}개")
    print(f"처리된 파일: {processed_count}개")

def main():
    parser = argparse.ArgumentParser(
        description="SRT_HOME/origin 아래 모든 base 폴더의 SRT 파일에 Post-processing을 적용합니다."
    )
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본값 사용)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_parent = srt_home_path / 'origin'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"대상 디렉토리: {origin_parent} (하위 base 폴더 모두 포함)\n")
    
    if not origin_parent.exists():
        print(f"오류: {origin_parent} 폴더가 존재하지 않습니다.")
        return
    
    post_process_all_files(origin_parent)

if __name__ == "__main__":
    main()