import argparse
import shutil
import os
from pathlib import Path
from utils import get_srt_home, get_base_filename, is_trash_path, find_mp4_path  # 공통 utils import
from compare_srt import compare_srt_file  # compare_srt.py의 함수 import (직접 호출)

def delete_related_files(base_filename, srt_home_path):
    dirs_to_clean = [
        srt_home_path / 'origin',
        srt_home_path / 'origin_separate',
        srt_home_path / 'trans_separate',
        srt_home_path / 'trans'
    ]
    deleted_count = 0
    for dir_path in dirs_to_clean:
        for file in dir_path.glob(f"{base_filename}*.srt"):
            try:
                file.unlink()
                print(f"삭제됨: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"삭제 실패: {file} - {e}")
    return deleted_count

def compare_all_files(target_path, origin_dir, trans_dir, srt_home_path):
    # unique base_filename 추출
    base_filenames = set()
    for file in origin_dir.glob('*.srt'):
        base = get_base_filename(file.stem)  # e.g., HMN-520.ja → HMN-520
        base_filenames.add(base)
    
    ok_count = 0
    failed_bases = []
    for base in sorted(base_filenames):
        if compare_srt_file(base, origin_dir, trans_dir):
            # OK 시 mp4 원래 경로 찾기
            mp4_path = find_mp4_path(base, target_path)
            if mp4_path:
                # srt 파일 찾기 (trans/base_filename*.srt, 첫 매치)
                srt_files = list(trans_dir.glob(f"{base}*.srt"))
                if srt_files:
                    srt_file = srt_files[0]
                    # 새 srt 이름: mp4와 동일 (확장자 .srt)
                    new_srt_name = mp4_path.stem + '.srt'
                    dest_srt_path = mp4_path.parent / new_srt_name
                    try:
                        shutil.move(str(srt_file), str(dest_srt_path))
                        print(f"srt 이동 및 이름 변경: {srt_file} -> {dest_srt_path}")
                        # 이동 성공 시 관련 파일 삭제
                        delete_related_files(base, srt_home_path)
                    except Exception as e:
                        print(f"srt 이동 실패: {srt_file} - {e}")
                else:
                    print(f"경고: {base} srt 파일 없음")
            else:
                print(f"경고: {base} mp4 파일 없음")
            ok_count += 1
        else:
            failed_bases.append(base)
            print(f"비교 실패: {base}")
    
    print(f"총 {ok_count}개의 base_filename이 OK되었습니다.")
    if failed_bases:
        print("\n실패한 base_filename 목록:")
        for failed in failed_bases:
            print(f"- {failed}")

def main():
    parser = argparse.ArgumentParser(description="SRT_HOME/origin의 모든 base_filename을 대상으로 compare_srt.py를 실행합니다. OK 시 srt를 mp4 경로로 이동/이름 변경 후 관련 파일 삭제.")
    parser.add_argument('-t', '--target', help="mp4 검색 대상 경로 (기본: Windows V:/, Linux /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    
    # target 경로 설정
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
    origin_dir = srt_home_path / 'origin'
    trans_dir = srt_home_path / 'trans'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"원본 디렉토리: {origin_dir}")
    print(f"번역 디렉토리: {trans_dir}")
    print(f"mp4 검색 경로: {target_path}")
    
    if not origin_dir.exists():
        print(f"오류: {origin_dir}가 존재하지 않습니다.")
        return
    
    compare_all_files(target_path, origin_dir, trans_dir, srt_home_path)

if __name__ == "__main__":
    main()