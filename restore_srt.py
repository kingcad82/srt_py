# restore_srt.py
# 새 버전: base_filename 폴더 구조 완벽 지원
# (origin_separate/{base}/xxx_000.srt → trans_separate/{base}/xxx_000.srt 복원)

import argparse
from pathlib import Path
from utils import (
    parse_srt_blocks,
    clean_trans_text,
    get_srt_home,
    get_base_from_path,
    get_base_dir
)

def restore_srt_file(file_path: Path, origin_separate_dir: Path, trans_separate_dir: Path):
    base = get_base_from_path(file_path)
    
    # origin_separate/{base}/ 파일 (입력)
    origin_file = file_path
    
    # trans_separate/{base}/ 동일 이름 파일
    trans_base_dir = get_base_dir(trans_separate_dir, base)
    trans_file = trans_base_dir / file_path.name
    
    if not trans_file.exists():
        print(f"오류: trans_separate/{base}/{file_path.name} 파일이 없습니다. 중단합니다.")
        return False
    
    if not origin_file.exists():
        print(f"오류: origin_separate/{base}/{file_path.name} 파일이 없습니다. 중단합니다.")
        return False
    
    try:
        origin_content = origin_file.read_text(encoding='utf-8')
        trans_content = trans_file.read_text(encoding='utf-8')
        
        # 1. 번역 노이즈 제거
        cleaned_trans = clean_trans_text(trans_content)
        
        # 2. 원본에서 번호 + 타임스탬프만 추출
        origin_blocks = parse_srt_blocks(origin_content)
        origin_headers = []
        for block in origin_blocks:
            lines = block.splitlines()
            if len(lines) >= 2:
                origin_headers.append((lines[0].strip(), lines[1].strip()))
        
        # 3. 번역본에서 대사만 추출 (빈 대사도 허용)
        trans_blocks = parse_srt_blocks(cleaned_trans)
        trans_texts = []
        for block in trans_blocks:
            lines = block.splitlines()
            text = '\n'.join(lines[2:]).strip() if len(lines) > 2 else ''
            trans_texts.append(text)
        
        # 4. 병합 (원본 헤더 + 번역 대사)
        merged_blocks = []
        for i in range(len(origin_headers)):
            num, time = origin_headers[i]
            text = trans_texts[i] if i < len(trans_texts) else ''
            block = f"{num}\n{time}\n{text}\n"
            merged_blocks.append(block)
        
        # 저장 (trans_separate/{base}/ 에 덮어쓰기)
        output = ''.join(merged_blocks).rstrip() + '\n\n'
        trans_file.write_text(output, encoding='utf-8')
        
        print(f"✅ 복원 완료: trans_separate/{base}/{file_path.name}")
        print(f"   (원본 블록: {len(origin_blocks)}, 번역 블록: {len(trans_blocks)})")
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {file_path.name} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="restore_srt.py 단일 파일 복원 (base 폴더 구조 지원)"
    )
    parser.add_argument('-f', '--file', required=True,
                        help="복원할 파일 (origin_separate/{base}/xxx_000.srt)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_separate_dir = srt_home_path / 'origin_separate'
    trans_separate_dir = srt_home_path / 'trans_separate'
    
    file_path = Path(args.file)
    if not file_path.is_absolute():
        # 상대 경로 → base 폴더에서 자동 찾기
        base = get_base_from_path(file_path)
        file_path = get_base_dir(origin_separate_dir, base) / file_path.name
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"origin_separate: {origin_separate_dir}")
    print(f"trans_separate : {trans_separate_dir}")
    print(f"복원 대상: {file_path}\n")
    
    restore_srt_file(file_path, origin_separate_dir, trans_separate_dir)

if __name__ == "__main__":
    main()