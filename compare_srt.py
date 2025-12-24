import argparse
from pathlib import Path
from utils import parse_srt_blocks, get_srt_home  # 공통 utils import

def compare_srt_file(base_filename, origin_dir, trans_dir):
    # 원본 파일 자동 검색: f"{base_filename}*.srt" 패턴 (e.g., HMN-520.ja.srt 매치)
    origin_files = sorted(origin_dir.glob(f"{base_filename}*.srt"))
    if not origin_files:
        print(f"오류: {base_filename}으로 시작하는 원본 파일이 없습니다. 중단합니다.")
        return False
    origin_file = origin_files[0]  # 첫 매치 사용 (여러 개 시 경고)
    if len(origin_files) > 1:
        print(f"경고: 여러 원본 파일 매치 ({len(origin_files)}개). 첫 파일 {origin_file} 사용.")
    
    # 번역 파일 자동 검색: 동일 패턴
    trans_files = sorted(trans_dir.glob(f"{base_filename}*.srt"))
    if not trans_files:
        print(f"오류: {base_filename}으로 시작하는 번역 파일이 없습니다. 중단합니다.")
        return False
    trans_file = trans_files[0]  # 첫 매치 사용
    if len(trans_files) > 1:
        print(f"경고: 여러 번역 파일 매치 ({len(trans_files)}개). 첫 파일 {trans_file} 사용.")
    
    try:
        with open(origin_file, 'r', encoding='utf-8') as f:
            origin_content = f.read()
        origin_blocks = parse_srt_blocks(origin_content)
        
        with open(trans_file, 'r', encoding='utf-8') as f:
            trans_content = f.read()
        trans_blocks = parse_srt_blocks(trans_content)
        
        # 총 자막 갯수 비교
        if len(origin_blocks) != len(trans_blocks):
            print(f"총 자막 갯수 불일치: 원본 {len(origin_blocks)}, 번역 {len(trans_blocks)}. 중단합니다.")
            return False
        
        # 각 블록 비교: 번호/타임스탬프 + 빈 대사 확인 (번역 파일에서)
        mismatch_found = False
        for i in range(len(origin_blocks)):
            origin_lines = origin_blocks[i].splitlines()
            trans_lines = trans_blocks[i].splitlines()
            if len(origin_lines) < 2 or len(trans_lines) < 2:
                continue
            # 번호 비교
            if origin_lines[0].strip() != trans_lines[0].strip():
                print(f"불일치: 블록 {i+1} 자막 번호 - 원본 '{origin_lines[0].strip()}', 번역 '{trans_lines[0].strip()}'")
                mismatch_found = True
            # 타임스탬프 비교
            if origin_lines[1].strip() != trans_lines[1].strip():
                print(f"불일치: 블록 {i+1} 타임스탬프 - 원본 '{origin_lines[1].strip()}', 번역 '{trans_lines[1].strip()}'")
                mismatch_found = True
            # 빈 대사 확인 (번역 파일에서, 라인 2부터 모두 빈 문자열인지)
            trans_text = '\n'.join(trans_lines[2:]).strip()
            if not trans_text:
                print(f"경고: 블록 {i+1} 대사가 비어 있습니다. (자막 번호와 타임스탬프만 있음)")
                mismatch_found = True
        
        if mismatch_found:
            print("불일치 또는 빈 대사 부분이 있습니다. 중단합니다.")
            return False
        else:
            print("모두 일치합니다. (빈 대사 없음) OK")
            return True
    except Exception as e:
        print(f"오류 발생: {base_filename} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/origin과 SRT_HOME/trans의 base_filename으로 시작하는 파일을 자동 찾아 비교합니다. 총 자막 갯수, 번호, 타임스탬프, 빈 대사 확인.")
    parser.add_argument('-f', '--file', required=True, help="base_filename (e.g., HMN-520, 언어 코드 자동 감지)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    origin_dir = srt_home_path / 'origin'
    trans_dir = srt_home_path / 'trans'
    
    base_filename = args.file  # e.g., HMN-520
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 디렉토리: {origin_dir}")
    print(f"번역 디렉토리: {trans_dir}")
    print(f"base_filename: {base_filename}")
    
    compare_srt_file(base_filename, origin_dir, trans_dir)

if __name__ == "__main__":
    main()