# restore_srt.py (수정: 노이즈 제거, 원본 헤더 추출, 번역 대사 추출, 병합 명확화)
import argparse
from pathlib import Path
from utils import parse_srt_blocks, clean_trans_text, get_srt_home  # 공통 utils import

def restore_srt_file(file_path, origin_separate_dir, trans_separate_dir):
    trans_file = trans_separate_dir / file_path.name
    if not trans_file.exists():
        print(f"오류: {trans_file}가 존재하지 않습니다. 중단합니다.")
        return False
    
    origin_file = origin_separate_dir / file_path.name
    if not origin_file.exists():
        print(f"오류: 원본 chunk {origin_file}가 없어 중단합니다.")
        return False
    
    try:
        with open(origin_file, 'r', encoding='utf-8') as f:
            origin_content = f.read()
        
        with open(trans_file, 'r', encoding='utf-8') as f:
            trans_content = f.read()
        
        # 1. 번역도구가 만든 노이즈 제거
        cleaned_trans = clean_trans_text(trans_content)
        
        # 2. 원본에서 자막번호와 타임스탬프 추출
        origin_blocks = parse_srt_blocks(origin_content)
        origin_headers = []
        for block in origin_blocks:
            lines = block.splitlines()
            if len(lines) >= 2:
                origin_headers.append((lines[0].strip(), lines[1].strip()))
        
        # 3. 번역본에서 번역된 대사 추출
        trans_blocks = parse_srt_blocks(cleaned_trans)
        trans_texts = []
        for block in trans_blocks:
            lines = block.splitlines()
            if len(lines) > 2:
                text = '\n'.join(lines[2:]).strip()  # 다중 라인 유지, 끝 공백만 제거
            else:
                text = ''
            trans_texts.append(text)
        
        # 4. 2,3번 병합: 원본 길이 기준
        merged_blocks = []
        for i in range(len(origin_headers)):
            header_num, header_time = origin_headers[i]
            text = trans_texts[i] if i < len(trans_texts) else ''
            block = f"{header_num}\n{header_time}\n{text}\n"
            merged_blocks.append(block)
        
        # 저장: 마지막 빈 라인 유지
        output = '\n'.join(merged_blocks).rstrip() + '\n\n'
        with open(trans_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"복원 완료: {trans_file} (원본 블록: {len(origin_blocks)}, 번역 블록: {len(trans_blocks)}, 병합 블록: {len(merged_blocks)})")
        return True
    except Exception as e:
        print(f"오류 발생: {trans_file} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/trans_separate의 파일을 복원합니다. 불필요 문구 제거 후 원본 번호/타임스탬프와 번역 대사(빈 포함) 병합.")
    parser.add_argument('-f', '--file', required=True, help="복원할 파일 경로 (이름만으로도 가능, e.g., HMN-520.ja_000.srt)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    origin_separate_dir = srt_home_path / 'origin_separate'
    trans_separate_dir = srt_home_path / 'trans_separate'
    
    file_path = Path(args.file)
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 분할 디렉토리: {origin_separate_dir}")
    print(f"번역 분할 디렉토리: {trans_separate_dir}")
    print(f"입력 파일: {file_path}")
    
    restore_srt_file(file_path, origin_separate_dir, trans_separate_dir)

if __name__ == "__main__":
    main()