import argparse
from pathlib import Path
import os
from utils import parse_srt_blocks, get_srt_home  # 공통 utils import

def separate_srt_file(file_path, separated_dir, chunk_size=800):
    separated_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = parse_srt_blocks(content)
        total_blocks = len(blocks)
        print(f"처리 중: {file_path} - 총 {total_blocks}개의 자막 블록")
        
        if total_blocks == 0:
            print(f"경고: {file_path}에 자막 블록이 없습니다.")
            return 0
        
        chunk_count = 0
        for i in range(0, total_blocks, chunk_size):
            chunk_blocks = blocks[i:i + chunk_size]
            # 새로운 SRT 내용: 자막 번호를 원본 그대로 유지 (재시작 안 함)
            new_content = []
            for block in chunk_blocks:
                new_content.append(block)  # 원본 블록 그대로 추가 (번호 변경 없음)
            
            chunk_filename = f"{file_path.stem}_{chunk_count:03d}{file_path.suffix}"
            dest_path = separated_dir / chunk_filename
            # write: ''.join 후 rstrip()으로 불필요 공백 제거, 끝에 '\n\n'으로 빈 라인 추가
            output = ''.join(new_content).rstrip() + '\n\n'
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"생성됨: {dest_path} - {len(chunk_blocks)}개 블록, 번호 범위: {i+1} ~ {i+len(chunk_blocks)}")
            chunk_count += 1
        
        return chunk_count
    except Exception as e:
        print(f"오류 발생: {file_path} - {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="지정된 SRT 파일을 800개 자막 블록 chunk로 나누어 SRT_HOME/origin_separate에 저장합니다. 자막 번호 원본 유지, 빈 라인 유지.")
    parser.add_argument('-f', '--file', required=True, help="처리할 SRT 파일 경로 (필수)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    separated_dir = srt_home_path / 'origin_separate'
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"오류: 파일 {file_path}가 존재하지 않습니다.")
        return
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"분할 디렉토리: {separated_dir}")
    print(f"입력 파일: {file_path}")
    
    chunks = separate_srt_file(file_path, separated_dir)
    print(f"총 {chunks}개의 chunk가 생성되었습니다.")

if __name__ == "__main__":
    main()