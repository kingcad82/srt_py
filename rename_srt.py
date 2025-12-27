# rename_srt.py (새 파일: 단일 파일 이름 변경)
import argparse
from pathlib import Path
from utils import get_base_filename, get_srt_home

def rename_srt_file(file_path, lang, origin_dir):
    if not file_path.exists():
        print(f"오류: {file_path}가 존재하지 않습니다.")
        return False
    
    base = get_base_filename(file_path.stem)
    new_filename = f"{base}.{lang}.srt"
    new_path = origin_dir / new_filename
    
    if new_path.exists():
        print(f"경고: {new_path}가 이미 존재합니다. 덮어쓰기.")
    
    try:
        file_path.rename(new_path)
        print(f"이름 변경: {file_path} -> {new_path}")
        return True
    except Exception as e:
        print(f"오류: 이름 변경 실패 - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/origin의 지정 SRT 파일 이름을 base_filename.lang.srt로 변경합니다.")
    parser.add_argument('-f', '--file', required=True, help="변경할 SRT 파일 경로 또는 이름 (e.g., HMN-520.random.srt)")
    parser.add_argument('-l', '--lang', required=True, help="언어 코드 (e.g., ja)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_dir = srt_home_path / 'origin'
    
    file_path = origin_dir / Path(args.file).name if not Path(args.file).is_absolute() else Path(args.file)
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 디렉토리: {origin_dir}")
    print(f"입력 파일: {file_path}")
    print(f"언어 코드: {args.lang}")
    
    rename_srt_file(file_path, args.lang, origin_dir)

if __name__ == "__main__":
    main()