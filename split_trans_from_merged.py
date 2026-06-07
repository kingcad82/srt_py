import argparse
from pathlib import Path
from utils import read_text_preserve_encoding, parse_srt_blocks, get_base_dir


def split_for_base(srt_home: Path, base: str):
    origin_dir = srt_home / 'origin_separate' / base
    trans_merged_dir = srt_home / 'trans' / base
    trans_separate_dir = srt_home / 'trans_separate' / base
    if not origin_dir.exists():
        print(f"[SKIP] origin_separate/{base} not found")
        return
    if not trans_merged_dir.exists():
        print(f"[SKIP] trans/{base} not found")
        return

    # find merged trans file
    merged_files = list(trans_merged_dir.glob('*.srt'))
    if not merged_files:
        print(f"[SKIP] no .srt in trans/{base}")
        return
    merged_file = merged_files[0]

    # read origin chunk files and counts
    origin_chunks = sorted(origin_dir.glob(f"{base}*.srt"))
    if not origin_chunks:
        print(f"[SKIP] no origin chunks for {base}")
        return

    origin_counts = []
    for f in origin_chunks:
        txt, _ = read_text_preserve_encoding(f)
        blocks = parse_srt_blocks(txt)
        origin_counts.append((f.name, len(blocks)))

    merged_text, enc = read_text_preserve_encoding(merged_file)
    merged_blocks = parse_srt_blocks(merged_text)
    total_origin = sum(c for _, c in origin_counts)
    if total_origin != len(merged_blocks):
        print(f"[ERROR] block count mismatch for {base}: origin total={total_origin}, trans merged={len(merged_blocks)}")
        return

    # ensure target dir exists
    get_base_dir(srt_home / 'trans_separate', base)

    # split and write
    idx = 0
    for name, cnt in origin_counts:
        out_path = srt_home / 'trans_separate' / base / name
        chunk_blocks = merged_blocks[idx:idx+cnt]
        idx += cnt
        content = ''.join(chunk_blocks)
        out_path.write_text(content, encoding=enc)
        print(f"WROTE {out_path} ({cnt} blocks)")

    print(f"[OK] split trans/{base} into trans_separate/{base} ({len(origin_counts)} files)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--srt_home', default='X:/srt_home')
    p.add_argument('--base', default=None)
    args = p.parse_args()
    srt_home = Path(args.srt_home)

    bases = [args.base] if args.base else []
    if not bases:
        # find all bases present in trans folder
        for d in (srt_home / 'trans').iterdir():
            if d.is_dir():
                bases.append(d.name)

    for base in bases:
        split_for_base(srt_home, base)


if __name__ == '__main__':
    main()
