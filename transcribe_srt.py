# transcribe_srt.py (수정: hallucination 방지 - condition_on_previous_text=False 추가)
import argparse
import whisper
import time
import subprocess
import os
from pathlib import Path
from whisper.utils import format_timestamp  # 타임스탬프 변환 import
from utils import get_srt_home  # 공통 utils import

def get_video_duration(video_path):
    """FFmpeg로 비디오 재생 시간 추출 (초 단위, 호환성 위해 subprocess 사용)."""
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        print(f"경고: 비디오 길이 추출 실패 - {e}. 기본값 0 사용.")
        return 0.0

def get_video_size(video_path):
    """비디오 파일 크기 추출 (바이트 → MB/GB 변환)."""
    try:
        size_bytes = os.path.getsize(video_path)
        if size_bytes >= 1024 * 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        elif size_bytes >= 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{size_bytes / 1024:.2f} KB"
        return size_str
    except Exception as e:
        print(f"경고: 비디오 크기 추출 실패 - {e}. 기본값 알 수 없음.")
        return "알 수 없음"

def seconds_to_min_sec(seconds):
    """초를 분:초 형식으로 변환 (e.g., 123 → 2:03)."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

def transcribe_srt_from_video(video_path, model_name='large-v3', language='ja', output_dir=None):
    if output_dir is None:
        output_dir = video_path.parent
    else:
        output_dir = Path(output_dir)
    
    base = video_path.stem  # e.g., XRW-106
    output_path = output_dir / f"{base}.{language}.srt"
    
    if output_path.exists():
        print(f"스킵: {output_path} 이미 존재.")
        return True
    
    print(f"추출 시작: {video_path}")
    
    start_time = time.time()  # 추출 시간 측정 시작
    
    try:
        # 모델 로드 (CUDA 자동 사용 if available)
        model = whisper.load_model(model_name)
        
        # 오디오 추출 및 전사 (hallucination 방지: condition_on_previous_text=False)
        result = model.transcribe(str(video_path), language=language, task='transcribe', condition_on_previous_text=False)
        
        # SRT 형식 생성 (블록 끝에 빈 줄 추가)
        srt_content = []
        for i, segment in enumerate(result['segments'], start=1):
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()
            srt_content.append(f"{i}\n{start} --> {end}\n{text}\n\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(srt_content).rstrip())
        
        end_time = time.time()  # 추출 시간 측정 종료
        elapsed_time = end_time - start_time
        
        # 비디오 정보 추출
        video_duration = get_video_duration(video_path)
        video_size = get_video_size(video_path)
        
        # 출력: 재생 시간 (초 → HH:MM:SS), 용량 (MB/GB), 추출 시간 (분:초)
        duration_str = format_timestamp(video_duration) if video_duration > 0 else "알 수 없음"
        print(f"추출 완료: {output_path} (모델: {model_name}, 언어: {language})")
        print(f"영상 재생 시간: {duration_str}")
        print(f"영상 용량: {video_size}")
        print(f"추출 소요 시간: {seconds_to_min_sec(elapsed_time)}")
        
        return True
    except Exception as e:
        print(f"오류: {video_path} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Whisper로 단일 비디오에서 SRT 추출 (large-v3 모델 기본). 출력: video.lang.srt (기본: 동일 경로)")
    parser.add_argument('-v', '--video', required=True, help="입력 비디오 파일 경로 (e.g., MP4)")
    parser.add_argument('-m', '--model', default='large-v3', help="Whisper 모델 (e.g., large-v3)")
    parser.add_argument('-l', '--language', default='ja', help="언어 코드 (e.g., ja)")
    parser.add_argument('-o', '--output', help="출력 디렉토리 (기본: 비디오 동일 경로)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    video_path = Path(args.video)
    
    if not video_path.exists():
        print(f"오류: {video_path} 존재하지 않음.")
        return
    
    transcribe_srt_from_video(video_path, args.model, args.language, args.output)

if __name__ == "__main__":
    main()