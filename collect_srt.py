import argparse
import shutil
import os
from pathlib import Path
from utils import has_korean, is_trash_path, is_srt_home_path, get_srt_home  # 공통 utils import

def collect_srt_files(target_path, srt_home):
    origin_dir = srt_home / 'origin'
    origin_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    for root, dirs, files in os.walk(target_path, topdown=True):
        # SRT_HOME 디렉토리 스킵: dirs 리스트에서 제거하여 하위 탐색 방지
        dirs[:] = [d for d in dirs if not is_srt_home_path(Path(root) / d, srt_home)]
        # 휴지통 디렉토리 스킵
        dirs[:] = [d for d in dirs if not is_trash_path(Path(root) / d)]
        
        # 현재 디렉토리가 SRT_HOME 또는 휴지통 관련이면 스킵
        if is_srt_home_path(Path(root), srt_home) or is_trash_path(Path(root)):
            continue
        
        for file in files:
            if file.lower().endswith('.srt'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if not has_korean(content):
                        # 외국어 자막으로 분류하여 이동
                        dest_path = origin_dir / file
                        shutil.move(str(file_path), str(dest_path))
                        print(f"이동됨: {file_path} -> {dest_path}")
                        moved_count += 1
                except Exception as e:
                    print(f"오류 발생: {file_path} - {e}")
    
    print(f"총 {moved_count}개의 외국어 SRT 파일이 이동되었습니다.")

def main():
    parser = argparse.ArgumentParser(description="현재 볼륨에서 SRT 파일을 검색하고 외국어 자막을 SRT_HOME/origin으로 이동합니다. SRT_HOME 내 파일은 스킵되며, 휴지통은 자동 스킵됩니다.")
    parser.add_argument('-t', '--target', help="검색할 대상 경로 (기본: Windows V:/, Linux /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    # SRT_HOME 설정
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    # target 경로 설정
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
    print(f"검색 경로: {target_path}")
    print(f"SRT_HOME: {srt_home_path}")
    
    collect_srt_files(target_path, srt_home_path)

if __name__ == "__main__":
    main()