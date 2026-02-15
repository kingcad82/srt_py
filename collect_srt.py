# collect_srt.py
# 새 버전: base_filename별 하위 폴더로 이동 (origin/SONE-013/...)

import argparse
import shutil
import os
from pathlib import Path
from utils import (
    has_korean, 
    is_trash_path, 
    is_srt_home_path, 
    get_srt_home, 
    get_base_filename,
    get_base_dir
)

def collect_srt_files(target_path, srt_home):
    origin_parent = srt_home / 'origin'
    # origin_parent.mkdir(parents=True, exist_ok=True)  # get_base_dir에서 자동 생성
    
    moved_count = 0
    for root, dirs, files in os.walk(target_path, topdown=True):
        # SRT_HOME과 휴지통 스킵
        dirs[:] = [d for d in dirs if not (is_srt_home_path(Path(root) / d, srt_home) or is_trash_path(Path(root) / d))]
        
        if is_srt_home_path(Path(root), srt_home) or is_trash_path(Path(root)):
            continue
        
        for file in files:
            if file.lower().endswith('.srt'):
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if not has_korean(content):
                        # base_filename 추출 후 해당 폴더 생성
                        base = get_base_filename(file_path.stem)
                        dest_base_dir = get_base_dir(origin_parent, base)
                        dest_path = dest_base_dir / file_path.name
                        
                        shutil.move(str(file_path), str(dest_path))
                        print(f"이동됨: {file_path} → {dest_path}")
                        moved_count += 1
                except Exception as e:
                    print(f"오류 발생: {file_path} - {e}")
    
    print(f"총 {moved_count}개의 외국어 SRT 파일이 base 폴더 구조로 이동되었습니다.")

def main():
    parser = argparse.ArgumentParser(
        description="현재 볼륨에서 SRT 파일을 검색하고, 외국어 자막을 SRT_HOME/origin/{base_filename}/ 폴더로 이동합니다."
    )
    parser.add_argument('-t', '--target', help="검색할 대상 경로 (기본: Windows V:/, Linux /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
    print(f"검색 경로: {target_path}")
    print(f"SRT_HOME: {srt_home_path}")
    print("base_filename 폴더 구조로 이동합니다...\n")
    
    collect_srt_files(target_path, srt_home_path)

if __name__ == "__main__":
    main()