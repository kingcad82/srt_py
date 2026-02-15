# compare_srt.py
# 새 버전: base_filename 폴더 구조 지원

import argparse
from pathlib import Path
from utils import parse_srt_blocks, get_srt_home, get_base_from_path, get_base_dir

def compare_srt_file(base_filename: str, origin_dir: Path, trans_dir: Path):
    """base_filename의 원본과 trans 파일 비교"""
    # origin/{base}/
    origin_base_dir = origin_dir / base_filename
    origin_files = sorted(origin_base_dir.glob("*.srt"))
    
    # trans/{base}/
    trans_base_dir = trans_dir / base_filename
    trans_files = sorted(trans_base_dir.glob("*.srt"))
    
    if not origin_files:
        print(f"오류: origin/{base_filename}에 파일이 없습니다.")
        return False
    if not trans_files:
        print(f"오류: trans/{base_filename}에 파일이 없습니다.")
        return False
    
    origin_file = origin_files[0]   # 보통 1개
    trans_file = trans_files[0]
    
    if len(origin_files) > 1 or len(trans_files) > 1:
        print(f"경고: {base_filename}에 여러 파일이 있습니다. 첫 번째 파일 사용.")
    
    try:
        origin_content = origin_file.read_text(encoding='utf-8')
        trans_content = trans_file.read_text(encoding='utf-8')
        
        origin_blocks = parse_srt_blocks(origin_content)
        trans_blocks = parse_srt_blocks(trans_content)
        
        # 1. 총 블록 수 비교
        if len(origin_blocks) != len(trans_blocks):
            print(f"[X] 블록 수 불일치: 원본 {len(origin_blocks)} vs 번역 {len(trans_blocks)}")
            return False
        
        # 2. 번호 + 타임스탬프 + 빈 대사 검사
        mismatch = False
        for i in range(len(origin_blocks)):
            o_lines = origin_blocks[i].splitlines()
            t_lines = trans_blocks[i].splitlines()
            
            # 번호 비교
            if o_lines[0].strip() != t_lines[0].strip():
                print(f"[X] 블록 {i+1}: 번호 불일치")
                mismatch = True
            # 타임스탬프 비교
            if o_lines[1].strip() != t_lines[1].strip():
                print(f"[X] 블록 {i+1}: 타임스탬프 불일치")
                mismatch = True
            # 빈 대사 확인
            trans_text = '\n'.join(t_lines[2:]).strip()
            if not trans_text:
                print(f"[!] 블록 {i+1}: 번역 대사가 비어있습니다!")
                mismatch = True
        
        if mismatch:
            print(f"[X] {base_filename} 비교 실패")
            return False
        else:
            print(f"[O] {base_filename} 비교 완료 (총 {len(origin_blocks)} 블록, 완벽 일치)")
            return True
            
    except Exception as e:
        print(f"오류 발생: {base_filename} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="origin/{base}와 trans/{base}의 SRT를 비교합니다."
    )
    parser.add_argument('-f', '--file', required=True,
                        help="base_filename (e.g. SONE-013)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_dir = srt_home_path / 'origin'
    trans_dir = srt_home_path / 'trans'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"비교 대상: {args.file}\n")
    
    compare_srt_file(args.file, origin_dir, trans_dir)

if __name__ == "__main__":
    main()