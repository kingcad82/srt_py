# 0.transcribe_all.py (개선: process_transcribe_list에서 set()으로 중복 제거)
import argparse
import os
import subprocess
from pathlib import Path
from utils import get_srt_home, is_trash_path, is_srt_home_path

def find_videos_without_srt(target_path, srt_home_path, language='ja', list_file='transcribe_list.txt'):
    video_extensions = {'.mp4', '.mkv', '.avi'}
    transcribe_list = []
    
    for root, dirs, files in os.walk(target_path, topdown=True):
        dirs[:] = [d for d in dirs if not (is_srt_home_path(Path(root) / d, srt_home_path) or is_trash_path(Path(root) / d))]
        
        for file in files:
            video_path = Path(root) / file
            if video_path.suffix.lower() not in video_extensions:
                continue
            
            base = video_path.stem
            srt_path_with_lang = video_path.parent / f"{base}.{language}.srt"
            srt_path_without_lang = video_path.parent / f"{base}.srt"
            
            if srt_path_with_lang.exists() or srt_path_without_lang.exists():
                continue
            
            transcribe_list.append(str(video_path))
    
    list_path = srt_home_path / list_file
    with open(list_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(transcribe_list))
    
    print(f"검색 완료: {len(transcribe_list)}개의 비디오 대상. 목록 저장: {list_path}")
    return list_path

def process_transcribe_list(list_path, model_name, language, output_dir=None):
    with open(list_path, 'r', encoding='utf-8') as f:
        videos = [line.strip() for line in f.readlines() if line.strip()]
    
    unique_videos = list(set(videos))  # 추가: 중복 제거
    
    remaining = []
    for video in unique_videos:
        cmd = ['python', 'transcribe_srt.py', '-v', video, '-m', model_name, '-l', language]
        if output_dir:
            cmd.extend(['-o', output_dir])
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"추출 실패: {video} - {e}")
            remaining.append(video)
    
    with open(list_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(remaining))
    
    print(f"처리 완료: 남은 대상 {len(remaining)}개.")

def main():
    parser = argparse.ArgumentParser(description="대상 폴더에서 비디오 검색 후 SRT 추출 (Whisper 사용). SRT 파일 없는 비디오 대상.")
    parser.add_argument('-t', '--target', help="검색 대상 경로 (기본: Windows V:/al/av, Linux /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    parser.add_argument('-m', '--model', default='large-v3-turbo', help="Whisper 모델 (기본: large-v3-turbo)")
    parser.add_argument('-l', '--language', default='ja', help="언어 코드 (기본: ja)")
    parser.add_argument('-o', '--output', help="출력 디렉토리 (기본: 비디오 동일 경로)")
    parser.add_argument('--list_file', default='transcribe_list.txt', help="목록 파일 이름 (기본: transcribe_list.txt)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    target_path = Path(args.target) if args.target else (Path('V:/al/av') if os.name == 'nt' else Path('/home'))
    
    print(f"transcribe_all.py 시작")
    print(f"target 경로: {target_path}")
    print(f"SRT_HOME: {srt_home_path}")
    
    list_path = find_videos_without_srt(target_path, srt_home_path, args.language, args.list_file)
    process_transcribe_list(list_path, args.model, args.language, args.output)
    
    print("\ntranscribe_all.py 완료")

if __name__ == "__main__":
    main()