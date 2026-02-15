# separate_all.py
# 새 버전: base_filename 폴더 구조 전체 지원 (rglob + chunk=50)

import argparse
from pathlib import Path
from utils import get_srt_home
from separate_srt import separate_srt_file   # 단일 chunk 함수 import

def separate_all_files(origin_parent: Path, separated_dir: Path, chunk_size: int = 50):
    processed_count = 0
    total_chunks = 0
    
    # origin 아래 모든 base 폴더의 .srt 파일 검색
    for file in origin_parent.rglob("*.srt"):
        chunks = separate_srt_file(file, separated_dir, chunk_size)
        if chunks > 0:
            processed_count += 1
            total_chunks += chunks
        else:
            print(f"스킵됨: {file}")
    
    print(f"\n=== separate_all 완료 ===")
    print(f"처리된 원본 파일: {processed_count}개")
    print(f"생성된 총 chunk: {total_chunks}개")

def main():
    parser = argparse.ArgumentParser(
        description="SRT_HOME/origin 아래 모든 base 폴더의 SRT 파일을 50개 블록 chunk로 나누어 origin_separate/{base}/ 에 저장합니다."
    )
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    parser.add_argument('-c', '--chunk-size', type=int, default=50, 
                        help="한 chunk당 블록 수 (기본: 50)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_parent = srt_home_path / 'origin'
    separated_dir = srt_home_path / 'origin_separate'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 디렉토리: {origin_parent} (하위 base 폴더 모두)")
    print(f"chunk 크기: {args.chunk_size}개\n")
    
    if not origin_parent.exists():
        print(f"오류: {origin_parent} 폴더가 존재하지 않습니다.")
        return
    
    separate_all_files(origin_parent, separated_dir, args.chunk_size)

if __name__ == "__main__":
    main()