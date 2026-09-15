import logging
from pathlib import Path
from typing import List
from faster_whisper import WhisperModel
from src.core.schemas import Chunk
 
logger = logging.getLogger(__name__)
 
DEFAULT_TEXT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
 
 
class AudioIngestor:
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
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
            vad_parameters=dict(min_silence_duration_ms=500)
        )
 
        chunks = []
        for i, segment in enumerate(segments, start=1):
            text = segment.text.strip()
            if not text:
                continue
 
            start_s = round(segment.start, 2)
            end_s = round(segment.end, 2)
            chunk_id = f"{file_path.stem}__t{int(start_s)}__c{i:03d}"
 
            chunk = Chunk(
                chunk_id=chunk_id,
                source=f"data/audio/{file_path.name}",
                modality="audio",
                text=text,
                embedding_model=DEFAULT_TEXT_EMBEDDING_MODEL,
                start_s=start_s,
                end_s=end_s
            )
            chunks.append(chunk)
 
        logger.info(f"Extracted {len(chunks)} audio chunks from {file_path.name}")
        return chunks
