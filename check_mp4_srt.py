import argparse
from pathlib import Path
import os
from utils import find_mp4_srt_status  # utils.py 함수 import

def main():
    parser = argparse.ArgumentParser(description="현재 볼륨에서 모든 MP4 파일을 검색하고, 같은 경로에 SRT 파일이 있는지 확인합니다. 하위 경로 포함, 휴지통 자동 스킵.")
    parser.add_argument('-t', '--target', help="검색할 대상 경로 (기본: Windows V:/, Linux /home)")
    args = parser.parse_args()
    
    # target 경로 설정
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
    print(f"검색 경로: {target_path}")
    
    find_mp4_srt_status(target_path)

if __name__ == "__main__":
    main()