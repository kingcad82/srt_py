# translate_srt.py (새 파일: 테스트용 단일 SRT 번역)
import argparse
from pathlib import Path
from transformers import pipeline
from utils import parse_srt_blocks, get_srt_home

def translate_text(text, src_lang='ja', tgt_lang='ko'):
    """텍스트를 일본어 -> 한국어로 번역 (Helsinki-NLP 모델 사용)."""
    translator = pipeline('translation', model='Helsinki-NLP/opus-mt-ja-ko')
    return translator(text)[0]['translation_text']

def translate_srt_file(file_path, output_dir=None):
    if output_dir is None:
        output_dir = file_path.parent
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = parse_srt_blocks(content)
        translated_blocks = []
        for block in blocks:
            lines = block.splitlines()
            if len(lines) < 3:
                translated_blocks.append(block)
                continue
            number = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:]).strip()
            translated_text = translate_text(text)
            translated_blocks.append(f"{number}\n{timestamp}\n{translated_text}\n")
        
        output_path = output_dir / (file_path.stem + '_ko.srt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(translated_blocks).rstrip() + '\n\n')
        
        print(f"번역 완료: {output_path} (ja -> ko)")
        return True
    except Exception as e:
        print(f"오류: {file_path} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="단일 SRT 파일을 일본어 -> 한국어로 번역 (테스트용). 출력: 원본.stem_ko.srt")
    parser.add_argument('-f', '--file', required=True, help="번역할 SRT 파일 경로")
    parser.add_argument('-o', '--output', help="출력 디렉토리 (기본: 입력 디렉토리)")
    parser.add_argument('-s', '--srt_home', help="SRT_HOME 경로 (기본: Windows V:/srt_home, Linux /home/srt_home)")
    args = parser.parse_args()
    
    srt_home_path = Path(args.srt_home) if args.srt_home else get_srt_home()
    file_path = Path(args.file)
    output_dir = Path(args.output) if args.output else None
    
    if not file_path.exists():
        print(f"오류: {file_path} 존재하지 않음.")
        return
    
    translate_srt_file(file_path, output_dir)

if __name__ == "__main__":
    main()