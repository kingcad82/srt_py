# separate_srt.py
# 새 버전: chunk_size=50 + base_filename 폴더 구조 지원

import argparse
from pathlib import Path
from utils import parse_srt_blocks, get_srt_home, get_base_dir, get_base_from_path

def separate_srt_file(file_path: Path, separated_dir: Path, chunk_size: int = 100):
    """SRT 파일을 chunk_size(기본 50)개 블록으로 나누어 base 폴더에 저장"""
    separated_base_dir = get_base_dir(separated_dir, get_base_from_path(file_path))
    
    try:
        content = file_path.read_text(encoding='utf-8')
        blocks = parse_srt_blocks(content)
        total_blocks = len(blocks)
        
        print(f"처리 중: {file_path.name} → 총 {total_blocks}개 블록")
        
        if total_blocks == 0:
            print(f"경고: {file_path}에 자막 블록이 없습니다.")
            return 0
        
        chunk_count = 1
        for i in range(0, total_blocks, chunk_size):
            chunk_blocks = blocks[i:i + chunk_size]
            
            # chunk 파일명: base.lang_000.srt 형태
            chunk_filename = f"{file_path.stem}_{chunk_count:03d}{file_path.suffix}"
            dest_path = separated_base_dir / chunk_filename
            
            output = ''.join(chunk_blocks).rstrip() + '\n\n'
            dest_path.write_text(output, encoding='utf-8')
            
            print(f"  → 생성됨: {chunk_filename} ({len(chunk_blocks)} 블록, 범위: {i+1}~{i+len(chunk_blocks)})")
            chunk_count += 1
        
        print(f"완료: {chunk_count}개 chunk 생성 (폴더: {get_base_from_path(file_path)}/)\n")
        return chunk_count
    except Exception as e:
        print(f"오류 발생: {file_path} - {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(
        description="단일 SRT 파일을 50개 블록 chunk로 나누어 origin_separate/{base}/ 에 저장합니다."
    )
    parser.add_argument('-f', '--file', required=True, 
                        help="분할할 SRT 파일 경로")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    parser.add_argument('-c', '--chunk-size', type=int, default=100, 
                        help="한 chunk당 블록 수 (기본: 100)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    separated_dir = srt_home_path / 'origin_separate'
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"오류: {file_path} 파일이 존재하지 않습니다.")
        return
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"분할 대상: {file_path}")
    print(f"chunk 크기: {args.chunk_size}개\n")
    
    chunks = separate_srt_file(file_path, separated_dir, args.chunk_size)
    print(f"총 {chunks}개의 chunk 파일이 생성되었습니다.")

if __name__ == "__main__":
    main()