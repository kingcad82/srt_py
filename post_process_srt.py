# post_process_srt.py (origin으로 변경)
# post_process_srt.py (새 파일: 단일 SRT Post-processing)
import argparse
from pathlib import Path
from utils import parse_srt_blocks, apply_post_process, get_srt_home

def post_process_srt_file(file_path, output_dir=None):
    if output_dir is None:
        output_dir = file_path.parent
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = parse_srt_blocks(content)
        processed_blocks = [apply_post_process(block) for block in blocks]
        
        output_path = output_dir / file_path.name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(processed_blocks).rstrip() + '\n\n')
        
        print(f"Post-processing 완료: {output_path}")
        return True
    except Exception as e:
        print(f"오류: {file_path} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SRT 파일에 Post-processing 적용: 마침표 추가, 긴 줄 분할, 짧은 시간 수정. 출력은 같은 디렉토리 또는 지정.")
    parser.add_argument('-f', '--file', required=True, help="처리할 SRT 파일 경로")
    parser.add_argument('-o', '--output', help="출력 디렉토리 (기본: 입력 파일 디렉토리)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    file_path = Path(args.file)
    output_dir = Path(args.output) if args.output else None
    
    if not file_path.exists():
        print(f"오류: {file_path} 존재하지 않음.")
        return
    
    post_process_srt_file(file_path, output_dir)

if __name__ == "__main__":
    main()