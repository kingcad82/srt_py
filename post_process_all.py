# post_process_all.py (새 파일: 전체 SRT Post-processing)
import argparse
from pathlib import Path
from utils import get_srt_home
from post_process_srt import post_process_srt_file

def post_process_all_files(trans_dir):
    processed_count = 0
    for file in trans_dir.glob('*.srt'):
        if post_process_srt_file(file):
            processed_count += 1
        else:
            print(f"스킵: {file} - 처리 실패")
    
    print(f"총 {processed_count}개의 SRT 파일에 Post-processing 적용됨.")

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/trans의 모든 SRT 파일에 Post-processing 적용.")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    trans_dir = srt_home_path / 'trans'
    
    if not trans_dir.exists():
        print(f"오류: {trans_dir} 존재하지 않음.")
        return
    
    post_process_all_files(trans_dir)

if __name__ == "__main__":
    main()