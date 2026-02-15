# rename_srt.py
# 새 버전: base_filename 폴더 구조 지원 (origin/{base}/ 안에 rename)

import argparse
from pathlib import Path
from utils import get_base_filename, get_base_dir, get_srt_home

def rename_srt_file(file_path: Path, lang: str, origin_parent: Path):
    if not file_path.exists():
        print(f"오류: {file_path}가 존재하지 않습니다.")
        return False
    
    # base_filename 추출
    base = get_base_filename(file_path.stem)
    
    # 새 파일명: base.lang.srt
    new_filename = f"{base}.{lang}.srt"
    
    # base 폴더 생성 및 새 경로
    base_dir = get_base_dir(origin_parent, base)
    new_path = base_dir / new_filename
    
    if new_path.exists():
        print(f"경고: {new_path}가 이미 존재합니다. 덮어쓰기합니다.")
    
    try:
        file_path.rename(new_path)
        print(f"이름 변경 완료: {file_path.name} → {new_filename}  (폴더: {base}/)")
        return True
    except Exception as e:
        print(f"오류: 이름 변경 실패 - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="단일 SRT 파일을 base_filename.lang.srt로 변경합니다. (base 폴더 구조 지원)"
    )
    parser.add_argument('-f', '--file', required=True, 
                        help="변경할 SRT 파일 경로 또는 이름 (e.g. HMN-520.random.srt)")
    parser.add_argument('-l', '--lang', required=True, 
                        help="언어 코드 (e.g. ja)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본값 사용)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_parent = srt_home_path / 'origin'
    
    # 파일 경로 처리 (상대경로면 origin 아래에서 찾음)
    file_path = Path(args.file)
    if not file_path.is_absolute():
        # base를 미리 추출해서 해당 폴더에서 찾기
        temp_base = get_base_filename(file_path.stem)
        base_dir = origin_parent / temp_base
        file_path = base_dir / file_path.name
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"대상 파일: {file_path}")
    print(f"언어 코드: {args.lang}")
    
    rename_srt_file(file_path, args.lang, origin_parent)

if __name__ == "__main__":
    main()