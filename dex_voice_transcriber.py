import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

from faster_whisper import WhisperModel
from pathlib import Path
import shutil
import time
from datetime import datetime

BASE_DIR = Path(__file__).parent

INCOMING = BASE_DIR / "dex_voice_incoming"
TRANSCRIPTS = BASE_DIR / "dex_voice_transcripts"
PROCESSED = BASE_DIR / "dex_voice_processed"
LOGS = BASE_DIR / "dex_voice_logs"

SUPPORTED_EXTENSIONS = [".mp4", ".mkv", ".mp3", ".m4a", ".wav", ".aac", ".flac", ".ogg"]

LANGUAGE = "en"

for folder in [INCOMING, TRANSCRIPTS, PROCESSED, LOGS]:
    folder.mkdir(parents=True, exist_ok=True)

print("Loading Whisper...")
model = WhisperModel("small", device="cpu", compute_type="int8")
print("Whisper loaded.")


def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def transcribe_file(file_path):
    print(f"\nProcessing: {file_path.name}")

    segments, info = model.transcribe(
        str(file_path),
        language=LANGUAGE,
        beam_size=5
    )

    transcript_lines = []
    clean_text_lines = []

    for segment in segments:
        start = format_timestamp(segment.start)
        end = format_timestamp(segment.end)
        text = segment.text.strip()

        transcript_lines.append(f"[{start} - {end}] {text}")
        clean_text_lines.append(text)

    full_transcript = "\n".join(transcript_lines)
    clean_transcript = " ".join(clean_text_lines)

    output_base = file_path.stem

    timestamped_txt = TRANSCRIPTS / f"{output_base}_timestamped.txt"
    clean_txt = TRANSCRIPTS / f"{output_base}_clean.txt"

    with open(timestamped_txt, "w", encoding="utf-8") as f:
        f.write(full_transcript)

    with open(clean_txt, "w", encoding="utf-8") as f:
        f.write(clean_transcript)

    shutil.move(str(file_path), PROCESSED / file_path.name)

    with open(LOGS / "dex_voice_log.txt", "a", encoding="utf-8") as log:
        log.write(
            f"{datetime.now()} | processed | {file_path.name} | "
            f"language={LANGUAGE} | "
            f"duration={getattr(info, 'duration', 'unknown')}\n"
        )

    print(f"Done: {file_path.name}")
    print(f"Transcript saved: {timestamped_txt.name}")
    print(f"Clean text saved: {clean_txt.name}")


def main():
    print("\nDex Voice Transcriber started.")
    print("Waiting for files in dex_voice_incoming/\n")

    while True:
        files = [
            f for f in INCOMING.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        for file_path in files:
            try:
                transcribe_file(file_path)
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

                with open(LOGS / "dex_voice_errors.txt", "a", encoding="utf-8") as log:
                    log.write(f"{datetime.now()} | error | {file_path.name} | {e}\n")

        time.sleep(5)


if __name__ == "__main__":
    main()