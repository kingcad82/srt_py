# utils.py (Post-processing 함수 추가, 기존 내용 유지)
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
        if re.match(r'^\d+$', stripped) and current_block:  # 숫자 라인: 새 블록
            if any(re.match(time_pattern, l.strip()) for l in current_block[1:]):  # 타임스탬프 있는지 확인 (빈 블록 무시)
                blocks.append('\n'.join(current_block) + '\n')
            current_block = [line]
        else:
            current_block.append(line)
    if current_block and any(re.match(time_pattern, l.strip()) for l in current_block[1:]):
        blocks.append('\n'.join(current_block) + '\n')
    return blocks

def get_srt_home(default_windows='V:/srt_home', default_linux='/home/srt_home'):
    if platform.system() == 'Windows':
        return Path(default_windows)
    else:
        return Path(default_linux)

def clean_trans_text(text):
    """번역된 텍스트에서 불필요한 문구만 제거. 빈 라인 유지."""
    patterns = [r'Markdown', r'text', r'srt', r'plain', r'assistant:\s*', r'다음 내용을 참조하세요:\s*']  # 원복: r'text'로 변경 (콜론 제거)
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text

def sniff_encoding(path: Path) -> str:
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

def parse_timestamp(ts_str):
    """SRT 타임스탬프 문자열을 timedelta로 변환."""
    hours, minutes, seconds = map(int, ts_str.replace(',', ':').split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds / 1000)

def format_timestamp(td):
    """timedelta를 SRT 타임스탬프 문자열로 변환."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def add_period_if_missing(text, period_char='.'):  # 한국어는 '.' 또는 '。' 사용 가능
    """문장 끝에 마침표 추가 (이미 punctuation 있으면 스킵)."""
    punctuation = r'[.?!。？！]'
    if not re.search(punctuation + r'\s*$', text.strip()):
        return text.rstrip() + period_char
    return text

def split_long_lines(text, max_length=40):
    """긴 줄 분할 (max_length 초과 시 공백/쉼표에서 분할)."""
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
    """짧은 표시시간 수정 (min_duration 초 미만 시 end 연장)."""
    duration = (end_td - start_td).total_seconds()
    if duration < min_duration:
        return start_td, start_td + timedelta(seconds=min_duration)
    return start_td, end_td

def apply_post_process(block):
    """단일 SRT 블록에 Post-processing 적용."""
    lines = block.splitlines()
    if len(lines) < 3:
        return block
    number = lines[0].strip()
    timestamp = lines[1].strip()
    text = '\n'.join(lines[2:]).strip()
    
    # 적용: 마침표 추가, 긴 줄 분할 (대/소문자 수정은 한국어에 불필요, 스킵)
    text = add_period_if_missing(text)
    text = split_long_lines(text)
    
    # 타임스탬프 파싱 및 짧은 시간 수정
    start_str, end_str = timestamp.split(' --> ')
    start_td = parse_timestamp(start_str)
    end_td = parse_timestamp(end_str)
    start_td, end_td = fix_short_duration(start_td, end_td)
    new_timestamp = f"{format_timestamp(start_td)} --> {format_timestamp(end_td)}"
    
    return f"{number}\n{new_timestamp}\n{text}\n"