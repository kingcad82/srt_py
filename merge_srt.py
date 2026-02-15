# merge_srt.py
# 새 버전: base_filename 폴더 구조 지원 + chunk 병합

import argparse
from pathlib import Path
from utils import get_srt_home, get_base_dir, get_base_from_path

def merge_srt_file(base_filename: str, lang: str, origin_separate_dir: Path, trans_separate_dir: Path, trans_dir: Path):
    """base_filename에 해당하는 모든 chunk를 병합"""
    # base 폴더 경로
    origin_base_dir = origin_separate_dir / base_filename
    trans_base_dir = trans_separate_dir / base_filename
    
    origin_chunks = sorted(origin_base_dir.glob("*.srt"))
    trans_chunks = sorted(trans_base_dir.glob("*.srt"))
    
    if len(origin_chunks) == 0:
        print(f"오류: origin_separate/{base_filename}에 chunk 파일이 없습니다.")
        return False
    
    if len(origin_chunks) != len(trans_chunks):
        print(f"오류: chunk 수 불일치 (origin: {len(origin_chunks)}, trans: {len(trans_chunks)})")
        return False
    
    # chunk 번호 검증 (_000, _001 ... 순서)
    for i, (o_chunk, t_chunk) in enumerate(zip(origin_chunks, trans_chunks)):
        expected = f"_{i:03d}.srt"
        if not (o_chunk.name.endswith(expected) and t_chunk.name.endswith(expected)):
            print(f"오류: chunk 번호 불일치 ({o_chunk.name})")
            return False
    
    # 출력 경로: trans/{base}/{base}.srt
    trans_base_dir_out = get_base_dir(trans_dir, base_filename)
    output_path = trans_base_dir_out / f"{base_filename}.srt"
    
    try:
        merged_content = []
        for trans_chunk in trans_chunks:
            content = trans_chunk.read_text(encoding='utf-8').rstrip()
            merged_content.append(content)
        
        final_output = '\n\n'.join(merged_content) + '\n\n'
        output_path.write_text(final_output, encoding='utf-8')
        
        print(f"✅ 병합 완료: {output_path} ({len(trans_chunks)} chunk)")
        return True
    except Exception as e:
        print(f"❌ 병합 오류: {base_filename} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="base_filename의 chunk들을 하나로 병합합니다. (trans/{base}/base.srt)"
    )
    parser.add_argument('-f', '--file', required=True,
                        help="base_filename (e.g. SONE-013)")
    parser.add_argument('-l', '--lang', help="언어 코드 (선택, 자동 감지)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    origin_separate_dir = srt_home_path / 'origin_separate'
    trans_separate_dir = srt_home_path / 'trans_separate'
    trans_dir = srt_home_path / 'trans'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"base_filename: {args.file}")
    print(f"출력: trans/{args.file}/{args.file}.srt\n")
    
    merge_srt_file(args.file, args.lang, origin_separate_dir, trans_separate_dir, trans_dir)

if __name__ == "__main__":
    main()