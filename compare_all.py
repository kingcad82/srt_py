# compare_all.py
# 새 버전: base_filename 폴더 구조 + OK 시 srt 이동 및 관련 폴더 전체 삭제

import argparse
import shutil
from pathlib import Path
from utils import get_srt_home, get_base_from_path, find_mp4_path
from compare_srt import compare_srt_file

def delete_related_files(base_filename: str, srt_home_path: Path):
    """base 폴더 전체 삭제 (origin, origin_separate, trans_separate, trans)"""
    dirs_to_clean = ['origin', 'origin_separate', 'trans_separate', 'trans']
    deleted_count = 0
    for dname in dirs_to_clean:
        target_dir = srt_home_path / dname / base_filename
        if target_dir.exists():
            shutil.rmtree(target_dir)
            print(f"🗑️  삭제 완료: {target_dir} (전체 폴더)")
            deleted_count += 1
    return deleted_count

def compare_all_files(target_path: Path, origin_dir: Path, trans_dir: Path, srt_home_path: Path):
    # 모든 base_filename 추출
    base_filenames = set()
    for file in origin_dir.rglob("*.srt"):
        base = get_base_from_path(file)
        base_filenames.add(base)
    
    ok_count = 0
    failed_bases = []
    
    for base in sorted(base_filenames):
        print(f"\n🔍 비교 중: {base}")
        
        if compare_srt_file(base, origin_dir, trans_dir):
            # OK → mp4 찾기
            mp4_path = find_mp4_path(base, target_path)
            if mp4_path:
                trans_base_dir = trans_dir / base
                srt_files = list(trans_base_dir.glob("*.srt"))
                if srt_files:
                    srt_file = srt_files[0]
                    new_srt_path = mp4_path.parent / f"{base}.srt"
                    
                    if new_srt_path.exists():
                        new_srt_path.unlink()
                    
                    shutil.move(str(srt_file), str(new_srt_path))
                    print(f"✅ SRT 이동 완료: {new_srt_path}")
                    
                    # 관련 폴더 전체 삭제
                    delete_related_files(base, srt_home_path)
                    ok_count += 1
                else:
                    print(f"⚠️  trans/{base}에 SRT 파일 없음")
            else:
                print(f"⚠️  MP4 파일을 찾지 못했습니다: {base}")
                ok_count += 1  # 비교는 성공했으므로 카운트
        else:
            failed_bases.append(base)
            print(f"❌ 비교 실패: {base}")
    
    print(f"\n{'='*60}")
    print(f"🎉 compare_all 완료!")
    print(f"성공: {ok_count}개")
    if failed_bases:
        print(f"실패: {len(failed_bases)}개 → {failed_bases}")

def main():
    parser = argparse.ArgumentParser(
        description="모든 base_filename을 비교 → OK 시 SRT를 MP4 폴더로 이동하고 관련 폴더 삭제"
    )
    parser.add_argument('-t', '--target', help="MP4 검색 경로 (기본: V:/ 또는 /home)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    target_path = Path(args.target) if args.target else (Path('V:/') if os.name == 'nt' else Path('/home'))
    
    origin_dir = srt_home_path / 'origin'
    trans_dir = srt_home_path / 'trans'
    
    print(f"SRT_HOME: {srt_home_path}")
    print(f"MP4 검색 경로: {target_path}\n")
    
    if not origin_dir.exists():
        print(f"오류: {origin_dir} 폴더가 없습니다.")
        return
    
    compare_all_files(target_path, origin_dir, trans_dir, srt_home_path)

if __name__ == "__main__":
    main()