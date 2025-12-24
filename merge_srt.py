import argparse
from pathlib import Path
import os
from utils import get_srt_home  # 공통 utils import

def merge_srt_file(base_filename, lang, origin_separate_dir, trans_separate_dir, trans_dir):
    # lang 지정 시: search_pattern = f"{base_filename}.{lang}_*.srt"
    # lang None 시: search_pattern = f"{base_filename}*_*srt" (자동 *로 언어 코드 매치)
    search_pattern = f"{base_filename}.{lang}_*.srt" if lang else f"{base_filename}*_*.srt"
    # chunk 파일 목록 검색
    origin_chunks = sorted(origin_separate_dir.glob(search_pattern))
    trans_chunks = sorted(trans_separate_dir.glob(search_pattern))
    
    if len(origin_chunks) == 0:
        print(f"오류: {base_filename}에 해당하는 origin_separate chunk 파일이 없습니다. (패턴: {search_pattern})")
        return False
    
    if len(origin_chunks) != len(trans_chunks):
        print(f"오류: chunk 파일 갯수 불일치 (origin: {len(origin_chunks)}, trans: {len(trans_chunks)})")
        return False
    
    # search_base 추출: 첫 파일 stem.split('_')[0]
    search_base = origin_chunks[0].stem.split('_')[0]
    
    # 번호 확인: _000, _001 등 연속 확인
    for i, (origin_chunk, trans_chunk) in enumerate(zip(origin_chunks, trans_chunks)):
        expected_suffix = f"_{i:03d}.srt"
        if origin_chunk.name.endswith(expected_suffix) and trans_chunk.name.endswith(expected_suffix):
            continue
        print(f"오류: chunk 번호 불일치 (예상: {search_base}{expected_suffix}, origin: {origin_chunk.name}, trans: {trans_chunk.name})")
        return False
    
    try:
        output_path = trans_dir / f"{search_base}.srt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        merged_content = []
        for trans_chunk in trans_chunks:
            with open(trans_chunk, 'r', encoding='utf-8') as f:
                content = f.read().rstrip()  # 끝 빈 라인 제거 후 병합
                merged_content.append(content)
        
        final_output = '\n\n'.join(merged_content) + '\n\n'  # chunk 사이 빈 라인 유지
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_output)
        
        print(f"병합 완료: {output_path} (총 chunk: {len(trans_chunks)}, lang: {lang or 'auto'})")
        return True
    except Exception as e:
        print(f"오류 발생: {base_filename} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="base_filename의 chunk 파일들을 병합합니다. origin_separate와 trans_separate 비교 후 SRT_HOME/trans/base_filename.srt로 저장. (언어 코드 자동 매치)")
    parser.add_argument('-f', '--file', required=True, help="base_filename (e.g., HMN-520)")
    parser.add_argument('-l', '--lang', help="언어 코드 (e.g., ja. 기본: 자동)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    origin_separate_dir = srt_home_path / 'origin_separate'
    trans_separate_dir = srt_home_path / 'trans_separate'
    trans_dir = srt_home_path / 'trans'
    
    base_filename = args.file
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 분할 디렉토리: {origin_separate_dir}")
    print(f"번역 분할 디렉토리: {trans_separate_dir}")
    print(f"출력 디렉토리: {trans_dir}")
    print(f"base_filename: {base_filename}")
    print(f"lang: {args.lang or 'auto'}")
    
    merge_srt_file(base_filename, args.lang, origin_separate_dir, trans_separate_dir, trans_dir)

if __name__ == "__main__":
    main()