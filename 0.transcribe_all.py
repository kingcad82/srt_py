# 0.transcribe_all.py (수정: 모델 기본 large-v3로 변경, subprocess cmd에 -m 전달)
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
    # 목록 읽기
    with open(list_path, 'r', encoding='utf-8') as f:
        videos = [line.strip() for line in f.readlines() if line.strip()]
    
    # 중복 제거하면서 원래 순서 유지 (dict.fromkeys)
    unique_videos = list(dict.fromkeys(videos))
    
    for video in unique_videos:
        cmd = ['python', 'transcribe_srt.py', '-v', video, '-m', model_name, '-l', language]
        if output_dir:
            cmd.extend(['-o', output_dir])
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"경고: {result.stderr}")
            
            # 성공 시 목록 파일에서 해당 video의 모든 발생 제거
            with open(list_path, 'r', encoding='utf-8') as f:
                remaining = [line.strip() for line in f.readlines() if line.strip() != video]
            with open(list_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(remaining))
            print(f"목록 업데이트: {video} 제거됨")
        except subprocess.CalledProcessError as e:
            print(f"추출 실패: {video} - {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            # 실패 시 유지 (이미 목록에 있음)
    
    # 최종 남은 개수 출력
    with open(list_path, 'r', encoding='utf-8') as f:
        remaining_count = len([line for line in f if line.strip()])
    print(f"처리 완료: 남은 대상 {remaining_count}개.")

def main():
    parser = argparse.ArgumentParser(description="대상 폴더에서 비디오 검색 후 SRT 추출 (Whisper 사용). SRT 파일 없는 비디오 대상.")
    parser.add_argument('-t', '--target', help="검색 대상 경로 (기본: Windows V:/al/av, Linux /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    parser.add_argument('-m', '--model', default='large-v3', help="Whisper 모델 (기본: large-v3)")
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