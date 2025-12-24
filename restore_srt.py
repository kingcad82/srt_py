import argparse
from pathlib import Path
from utils import parse_srt_blocks, clean_trans_text, get_srt_home  # 공통 utils import

def restore_srt_file(file_path, origin_separate_dir, trans_separate_dir):
    # trans_separate에서 파일 찾기
    trans_file = trans_separate_dir / file_path.name
    if not trans_file.exists():
        print(f"오류: {trans_file}가 존재하지 않습니다. 중단합니다.")
        return False
    
    # 원본 chunk 파일 찾기 (origin_separate의 같은 이름 파일)
    origin_file = origin_separate_dir / file_path.name
    if not origin_file.exists():
        print(f"경고: 원본 chunk {origin_file}가 없어 비교 스킵, 번역 파일만 처리합니다.")
    
    try:
        with open(trans_file, 'r', encoding='utf-8') as f:
            trans_content = f.read()
        
        # 클린 텍스트: 불필요 문구 제거, 빈 라인 정리
        cleaned_content = clean_trans_text(trans_content)
        
        # 블록 파싱: 번역 파일
        trans_blocks = parse_srt_blocks(cleaned_content)
        
        # 원본 블록 파싱 (비교용)
        if origin_file.exists():
            with open(origin_file, 'r', encoding='utf-8') as f:
                origin_content = f.read()
            origin_blocks = parse_srt_blocks(origin_content)
        
            # 비교 & 교체: 번호/타임스탬프 불일치 시 원본 번호/타임스탬프만 반영 (대사는 유지)
            for i in range(min(len(trans_blocks), len(origin_blocks))):
                trans_lines = trans_blocks[i].splitlines()
                origin_lines = origin_blocks[i].splitlines()
                if len(trans_lines) < 3 or len(origin_lines) < 3:
                    continue
                # 번호와 타임스탬프 비교
                if trans_lines[0] != origin_lines[0] or trans_lines[1].strip() != origin_lines[1].strip():
                    # 불일치: 번호와 타임스탬프 원본으로 교체 (대사: 번역 유지)
                    trans_blocks[i] = '\n'.join([origin_lines[0], origin_lines[1]] + trans_lines[2:]) + '\n'
                    print(f"블록 {i+1}: 불일치 - 번호/타임스탬프 원본 반영")
        
        # 수정된 내용 저장 (trans_separate에 덮어쓰기)
        output = ''.join(trans_blocks).rstrip() + '\n\n'  # 마지막 빈 라인 유지
        with open(trans_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"복원 완료: {trans_file}")
        return True
    except Exception as e:
        print(f"오류 발생: {trans_file} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/trans_separate의 파일을 복원합니다. 불필요 문구 제거, 원본 chunk 비교 후 번호/타임스탬프 교체 (대사 유지).")
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