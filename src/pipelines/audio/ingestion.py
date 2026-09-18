import logging
from pathlib import Path
from typing import List
from faster_whisper import WhisperModel

from src.core.schemas import Chunk
from src.core.config import settings

logger = logging.getLogger(__name__)

TARGET_WORDS = 75
OVERLAP_WORDS = 20

class AudioIngestor:
    def __init__(self):
        model_size = getattr(settings, "WHISPER_MODEL", getattr(settings, "AUDIO_MODEL", "base"))
        device = getattr(settings, "WHISPER_DEVICE", "cpu")
        compute_type = getattr(settings, "WHISPER_COMPUTE_TYPE", "int8")

        logger.info(f"Loading faster-whisper model '{model_size}' on {device}")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def process_file(self, file_path: Path) -> List[Chunk]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        logger.info(f"Transcribing: {file_path.name}")

        segments, info = self.model.transcribe(
            str(file_path),
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        chunks = []
        buffer = []
        chunk_index = 1

        for segment in segments:
            if not segment.text.strip():
                continue

            buffer.append(segment)
            
            combined_text = " ".join([s.text.strip() for s in buffer])
            word_count = len(combined_text.split())

            if word_count >= TARGET_WORDS:
                start_s = round(buffer[0].start, 2)
                end_s = round(buffer[-1].end, 2)

                safe_stem = f"{file_path.stem}_{file_path.suffix.replace('.', '')}"
                chunk_id = f"{safe_stem}__t{int(start_s)}__c{chunk_index:03d}"

                chunk = Chunk(
                    chunk_id=chunk_id,
                    source=f"data/audio/{file_path.name}",
                    modality="audio",
                    text=combined_text,
                    embedding_model=settings.TEXT_EMBEDDING_MODEL,
                    start_s=start_s,
                    end_s=end_s,
                )
                chunks.append(chunk)
                chunk_index += 1

                while len(buffer) > 1 and len(" ".join([s.text.strip() for s in buffer]).split()) > OVERLAP_WORDS:
                    buffer.pop(0)

        if buffer:
            combined_text = " ".join([s.text.strip() for s in buffer])
            start_s = round(buffer[0].start, 2)
            end_s = round(buffer[-1].end, 2)
            safe_stem = f"{file_path.stem}_{file_path.suffix.replace('.', '')}"
            chunk_id = f"{safe_stem}__t{int(start_s)}__c{chunk_index:03d}"

            chunk = Chunk(
                chunk_id=chunk_id,
                source=f"data/audio/{file_path.name}",
                modality="audio",
                text=combined_text,
                embedding_model=settings.TEXT_EMBEDDING_MODEL,
                start_s=start_s,
                end_s=end_s,
            )
            chunks.append(chunk)

        logger.info(f"Generated {len(chunks)} overlapping chunks for {file_path.name}")
        return chunks
    