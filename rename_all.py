# rename_all.py (새 파일: origin 전체 파일 이름 변경)
import argparse
from pathlib import Path
from utils import get_srt_home
from rename_srt import rename_srt_file  # rename_srt.py 함수 import

def rename_all_files(origin_dir, lang):
    renamed_count = 0
    failed_files = []
    for file in origin_dir.glob('*.srt'):
        if rename_srt_file(file, lang, origin_dir):
            renamed_count += 1
        else:
            failed_files.append(file.name)
            print(f"이름 변경 실패: {file.name}")
    
    print(f"총 {renamed_count}개의 SRT 파일 이름이 변경되었습니다.")
    if failed_files:
        print("\n실패한 파일 목록:")
        for failed in failed_files:
            print(f"- {failed}")

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/origin의 모든 SRT 파일 이름을 base_filename.lang.srt로 변경합니다.")
    parser.add_argument('-l', '--lang', required=True, help="언어 코드 (e.g., ja)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_dir = srt_home_path / 'origin'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 디렉토리: {origin_dir}")
    print(f"언어 코드: {args.lang}")
    
    if not origin_dir.exists():
        print(f"오류: {origin_dir}가 존재하지 않습니다.")
        return
    
    rename_all_files(origin_dir, args.lang)

if __name__ == "__main__":
    main()