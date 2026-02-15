# utils.py
# 새 버전: base_filename별 하위 폴더 구조 지원 (2026년 2월 업데이트)

import os
import re
from pathlib import Path
import platform
import codecs
from datetime import timedelta

def get_base_filename(filename):
    """SRT 파일의 base_filename을 반환합니다. chunk 번호 전에 첫 .까지의 문자열."""
    without_chunk = filename.split('_')[0]
    base = without_chunk.split('.')[0]
    return base

def get_base_dir(parent_dir: Path, base_filename: str) -> Path:
    """base_filename으로 하위 폴더를 만들고 반환 (새 구조 핵심 함수)"""
    base_path = parent_dir / base_filename
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path

def get_base_from_path(file_path: Path) -> str:
    """파일 경로에서 base_filename 추출"""
    return get_base_filename(file_path.stem)

def has_korean(text):
    """텍스트에 한국어가 있는지 확인 (100바이트 이상 한글 기준)"""
    hangul_chars = re.findall(r'[\uAC00-\uD7A3]', text)
    combined_hangul = ''.join(hangul_chars)
    byte_length = len(combined_hangul.encode('utf-8'))
    return byte_length >= 100

def is_trash_path(path):
    """경로가 휴지통 관련인지 확인"""
    lower_path = str(path).lower()
    return 'recycle' in lower_path or 'trash' in lower_path

def is_srt_home_path(path, srt_home):
    """경로가 SRT_HOME 내부인지 확인"""
    try:
        return path.resolve().is_relative_to(srt_home.resolve())
    except ValueError:
        return False

def parse_srt_blocks(content):
    """SRT 내용을 블록으로 파싱"""
    blocks = []
    current_block = []
    time_pattern = r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$'
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r'^\d+$', stripped) and current_block:
            if any(re.match(time_pattern, l.strip()) for l in current_block[1:]):
                blocks.append('\n'.join(current_block) + '\n')
            current_block = [line]
        else:
            current_block.append(line)
    if current_block and any(re.match(time_pattern, l.strip()) for l in current_block[1:]):
        blocks.append('\n'.join(current_block) + '\n')
    return blocks

def get_srt_home(default_windows='X:/srt_home', default_linux='/home/srt_home'):
    """SRT_HOME 경로 반환"""
    if platform.system() == 'Windows':
        return Path(default_windows)
    else:
        return Path(default_linux)

def clean_trans_text(text):
    """번역 텍스트에서 노이즈 제거"""
    patterns = [r'animate-gaussian', r'Markdown', r'text', r'srt', r'plain', r'assistant:\s*', r'다음 내용을 참조하세요:\s*']
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text

def sniff_encoding(path: Path) -> str:
    """파일 인코딩 추정"""
    for enc in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
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

def find_mp4_path(base, target_path):
    """base_filename에 해당하는 mp4 경로 찾기"""
    video_extensions = {'.mp4', '.mkv', '.avi'}
    for root, dirs, files in os.walk(target_path, topdown=True):
        dirs[:] = [d for d in dirs if not is_trash_path(Path(root) / d)]
        if is_trash_path(Path(root)):
            continue
        for file in files:
            video_path = Path(root) / file
            if video_path.suffix.lower() in video_extensions and video_path.stem == base:
                return video_path
    return None

def find_mp4_srt_status(target_path):
    """mp4와 srt 상태 확인"""
    # 기존 함수 그대로...
    pass  # 필요하면 이전 버전 복사

def parse_timestamp(ts_str):
    hours, minutes, seconds = map(int, ts_str.replace(',', ':').split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds / 1000)

def format_timestamp(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def add_period_if_missing(text, period_char='.'):
    punctuation = r'[.?!。？！]'
    if not re.search(punctuation + r'\s*$', text.strip()):
        return text.rstrip() + period_char
    return text

def split_long_lines(text, max_length=40):
    lines = []
    current = ''
    for word in text.split():
        if len(current) + len(word) + 1 > max_length:
            lines.append(current.strip())
            current = word
        else:
            current += ' ' + word
    if current:
        lines.append(current.strip())
    return '\n'.join(lines)

def fix_short_duration(start_td, end_td, min_duration=1.5):
    duration = (end_td - start_td).total_seconds()
    if duration < min_duration:
        return start_td, start_td + timedelta(seconds=min_duration)
    return start_td, end_td

def apply_post_process(block):
    """단일 SRT 블록에 Post-processing 적용"""
    lines = block.splitlines()
    if len(lines) < 3:
        return block
    number = lines[0].strip()
    timestamp = lines[1].strip()
    text = '\n'.join(lines[2:]).strip()
    
    text = add_period_if_missing(text)
    text = split_long_lines(text)
    
    start_str, end_str = timestamp.split(' --> ')
    start_td = parse_timestamp(start_str)
    end_td = parse_timestamp(end_str)
    start_td, end_td = fix_short_duration(start_td, end_td)
    new_timestamp = f"{format_timestamp(start_td)} --> {format_timestamp(end_td)}"
    
    return f"{number}\n{new_timestamp}\n{text}\n"

# get_unique_path 등 기타 함수도 필요하면 추가