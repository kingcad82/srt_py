import os
import re
from pathlib import Path
import platform
import codecs

def get_base_filename(filename):
    """SRT 파일의 base_filename을 반환합니다. chunk 번호 전에 첫 .까지의 문자열."""
    without_chunk = filename.split('_')[0]
    base = without_chunk.split('.')[0]
    return base

def has_korean(text):
    hangul_chars = re.findall(r'[\uAC00-\uD7A3]', text)
    combined_hangul = ''.join(hangul_chars)
    byte_length = len(combined_hangul.encode('utf-8'))
    return byte_length >= 100

def is_trash_path(path):
    lower_path = str(path).lower()
    return 'recycle' in lower_path or 'trash' in lower_path

def is_srt_home_path(path, srt_home):
    try:
        return path.resolve().is_relative_to(srt_home.resolve())
    except ValueError:
        return False

def parse_srt_blocks(content):
    blocks = []
    current_block = []
    time_pattern = r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$'
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            current_block.append(line)
        else:
            if current_block and re.match(r'^\d+$', current_block[0].strip()) and any(re.match(time_pattern, l.strip()) for l in current_block[1:]):
                blocks.append('\n'.join(current_block) + '\n')
            current_block = []
    if current_block and re.match(r'^\d+$', current_block[0].strip()) and any(re.match(time_pattern, l.strip()) for l in current_block[1:]):
        blocks.append('\n'.join(current_block) + '\n')
    return blocks

def get_srt_home(default_windows='V:/srt_home', default_linux='/home/srt_home'):
    if platform.system() == 'Windows':
        return Path(default_windows)
    else:
        return Path(default_linux)

def clean_trans_text(text):
    patterns = [r'text', r'srt', r'assistant:\s*', r'다음 내용을 참조하세요:\s*']
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    lines = [line.strip() for line in text.splitlines() if line.strip() or (lines and lines[-1].strip())]
    return '\n'.join(lines) + '\n'  # 마지막 빈 라인 유지

def sniff_encoding(path: Path) -> str:
    with path.open("rb") as f:
        head = f.read(4)
    if head.startswith(UTF8_BOM):
        return "utf-8-sig"
    if head.startswith(UTF16_LE_BOM) or head.startswith(UTF16_BE_BOM):
        return "utf-16"
    for enc in ("utf-8", "cp949", "euc-kr", "utf-16", "latin-1"):
        try:
            path.read_text(encoding=enc)
            return enc
        except Exception:
            continue
    return "latin-1"

def read_text_preserve_encoding(path: Path) -> tuple[str, str]:
    enc = sniff_encoding(path)
    text = path.read_text(encoding=enc)
    return text, enc

def write_text_with_encoding(path: Path, text: str, enc: str) -> None:
    path.write_text(text, encoding=enc)

def load_patterns(pfile: Path) -> list[str]:
    raw, _ = read_text_preserve_encoding(pfile)
    pats: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        pats.append(s)
    return pats

def build_regex_for_pattern(pat: str, min_repeat: int) -> re.Pattern:
    esc = re.escape(pat)
    nmin = max(1, min_repeat - 1)
    rx = rf"(?P<pre>\s*)({esc})(?:[^\S\r\n]*{esc}){{{nmin},}}(?P<post>\s*)"
    return re.compile(rx)

def compress_repeats(text: str, patterns: list[str], min_repeat: int, keep_repeat: int, keep_space: bool) -> str:
    joiner = " " if keep_space else ""
    for p in patterns:
        rep = joiner.join([p] * keep_repeat)
        rx = build_regex_for_pattern(p, min_repeat)
        text = rx.sub(lambda m: f"{m.group('pre')}{rep}{m.group('post')}", text)
    return text

def find_mp4_path(base_filename, target_path):
    """target_path에서 base_filename으로 시작하는 .mp4 파일 경로 찾기."""
    for root, dirs, files in os.walk(target_path, topdown=True):
        dirs[:] = [d for d in dirs if not is_trash_path(Path(root) / d)]
        if is_trash_path(Path(root)):
            continue
        for file in files:
            if file.startswith(base_filename) and file.lower().endswith('.mp4'):
                return Path(root) / file
    return None

def find_mp4_srt_status(target_path):
    """target_path에서 모든 MP4 파일을 검색하고, SRT 파일 유무 확인. (하위 경로 포함, 휴지통 스킵)"""
    mp4_without_srt = []
    total_mp4 = 0
    for root, dirs, files in os.walk(target_path, topdown=True):
        # 휴지통 디렉토리 스킵
        dirs[:] = [d for d in dirs if not is_trash_path(Path(root) / d)]
        if is_trash_path(Path(root)):
            continue
        
        for file in files:
            if file.lower().endswith('.mp4'):
                mp4_path = Path(root) / file
                srt_path = mp4_path.with_suffix('.srt')
                total_mp4 += 1
                if srt_path.exists():
                    print(f"OK: {mp4_path} - SRT 존재 ({srt_path})")
                else:
                    print(f"경고: {mp4_path} - SRT 없음")
                    mp4_without_srt.append(str(mp4_path))
    
    print(f"\n요약: 총 MP4 파일 {total_mp4}개")
    if mp4_without_srt:
        print("SRT 없는 MP4 목록:")
        for missing in mp4_without_srt:
            print(f"- {missing}")
    else:
        print("모든 MP4에 SRT 파일이 있습니다. OK")