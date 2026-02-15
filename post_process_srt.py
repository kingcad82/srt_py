# post_process_srt.py
# 새 버전: base_filename 폴더 구조 완벽 지원

import argparse
from pathlib import Path
from utils import parse_srt_blocks, apply_post_process, get_srt_home

def post_process_srt_file(file_path: Path, output_dir=None):
    """단일 SRT 파일에 Post-processing 적용 (마침표, 긴 줄 분할, 짧은 시간 수정)"""
    if output_dir is None:
        output_dir = file_path.parent  # base 폴더 안에 그대로 저장
    
    try:
        content = file_path.read_text(encoding='utf-8')
        blocks = parse_srt_blocks(content)
        processed_blocks = [apply_post_process(block) for block in blocks]
        
        output_path = output_dir / file_path.name
        
        output_path.write_text(
            ''.join(processed_blocks).rstrip() + '\n\n',
            encoding='utf-8'
        )
        
        print(f"Post-processing 완료: {output_path}")
        return True
    except Exception as e:
        print(f"오류: {file_path} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="단일 SRT 파일에 Post-processing 적용 (base 폴더 구조 지원)"
    )
    parser.add_argument('-f', '--file', required=True, 
                        help="처리할 SRT 파일 경로")
    parser.add_argument('-o', '--output', help="출력 디렉토리 (기본: 입력 파일과 같은 base 폴더)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    file_path = Path(args.file)
    
    # 상대 경로 처리 (base 폴더 구조 고려)
    if not file_path.is_absolute():
        # origin 아래에서 base 폴더를 찾아서 처리
        from utils import get_base_filename, get_base_dir
        base = get_base_filename(file_path.stem)
        base_dir = get_base_dir(srt_home_path / 'origin', base)
        file_path = base_dir / file_path.name
    
    if not file_path.exists():
        print(f"오류: {file_path} 파일이 존재하지 않습니다.")
        return
    
    output_dir = Path(args.output) if args.output else None
    
    post_process_srt_file(file_path, output_dir)

if __name__ == "__main__":
    main()