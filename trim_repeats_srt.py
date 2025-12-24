import argparse
from pathlib import Path
import sys
from utils import load_patterns, compress_repeats, read_text_preserve_encoding, write_text_with_encoding, get_srt_home  # 통합 utils import

def process_file(path: Path, patterns: list[str], min_repeat: int, keep_repeat: int, keep_space: bool, dry_run: bool=False) -> tuple[bool, str]:
    original, enc = read_text_preserve_encoding(path)
    modified = compress_repeats(original, patterns, min_repeat, keep_repeat, keep_space)
    if modified != original:
        if not dry_run:
            # 백업 (옵션: 활성화 시 주석 해제)
            # bak = path.with_suffix(path.suffix + ".bak")
            # bak.write_bytes(path.read_bytes())
            write_text_with_encoding(path, modified, enc)
        return True, enc
    return False, enc

def trim_repeats_all(process_dir, patterns_file, min_repeat, keep_repeat, keep_space, dry_run):
    if not patterns_file.exists():
        print(f"오류: 패턴 파일 {patterns_file}가 존재하지 않습니다.")
        return

    patterns = load_patterns(patterns_file)
    print(f"로드된 패턴 수: {len(patterns)} from {patterns_file}")

    if not patterns:
        print("경고: 패턴이 없습니다. 아무 작업도 하지 않습니다.")
        return

    total = 0
    changed = 0
    for srt in process_dir.rglob("*.srt"):  # 수정: rglob으로 하위 경로 재귀 검색
        total += 1
        did_change, enc = process_file(srt, patterns, min_repeat, keep_repeat, keep_space, dry_run=dry_run)
        tag = "UPDATED" if did_change else "SKIP   "
        print(f"[{tag}] {srt} (enc={enc})")
        if did_change:
            changed += 1

    print(f"\n요약: 검색된 파일={total}, 업데이트={changed}, 스킵={total-changed}")

def main():
    parser = argparse.ArgumentParser(description="지정 디렉토리의 SRT 파일에서 반복 패턴을 제거합니다. 기본: SRT_HOME/origin. 패턴은 SRT_HOME/patterns.txt에서 로드. 커스텀 -s 입력 시 입력 경로 직접 사용.")
    parser.add_argument('-s', '--dir', help="처리할 디렉토리 경로 (기본: SRT_HOME/origin, 커스텀 시 입력 경로 직접, 하위 포함)")
    parser.add_argument('-p', '--patterns', help="패턴 파일 경로 (기본: SRT_HOME/patterns.txt)")
    parser.add_argument('-m', '--min', type=int, default=7, help="트리밍 트리거 최소 반복 수 (기본: 7)")
    parser.add_argument('-k', '--keep', type=int, default=3, help="남길 반복 수 (기본: 3)")
    parser.add_argument('--keep-space', action="store_true", help="남긴 반복 사이에 공백 유지 (기본: 없음)")
    parser.add_argument('--dry-run', action="store_true", help="변경 확인만, 실제 수정 안 함")
    args = parser.parse_args()

    if args.min < 2:
        print("오류: --min은 2 이상이어야 합니다.", file=sys.stderr)
        sys.exit(2)
    if args.keep < 1:
        print("오류: --keep은 1 이상이어야 합니다.", file=sys.stderr)
        sys.exit(2)

    srt_home_path = get_srt_home()  # 기본 SRT_HOME
    if args.dir:
        process_dir = Path(args.dir)  # 커스텀: 입력 경로 직접 사용
        patterns_home = srt_home_path  # patterns 기본: SRT_HOME
    else:
        process_dir = srt_home_path / 'origin'  # 기본: SRT_HOME/origin
        patterns_home = srt_home_path  # patterns 기본: SRT_HOME

    patterns_file = Path(args.patterns) if args.patterns else patterns_home / 'patterns.txt'

    print(f"처리 디렉토리: {process_dir} (하위 경로 포함)")
    print(f"패턴 파일: {patterns_file}")

    if not process_dir.exists():
        print(f"오류: {process_dir}가 존재하지 않습니다.")
        sys.exit(1)

    trim_repeats_all(process_dir, patterns_file, args.min, args.keep, args.keep_space, args.dry_run)

if __name__ == "__main__":
    main()