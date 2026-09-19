import hashlib
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Union

from faster_whisper import WhisperModel

try:
    from src.core.schemas import Chunk
    from src.core.config import settings
except ImportError as e:
    raise ImportError(
        f"Failed to import required dependencies: {e}. "
        "Ensure src.core.schemas and src.core.config are available."
    ) from e

logger = logging.getLogger(__name__)

TARGET_WORDS = 75
OVERLAP_WORDS = 20
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024 * 1024
SUPPORTED_AUDIO_EXTENSIONS = {
    '.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.opus', '.mpeg',
    '.mp4', '.webm', '.wma', '.mka', '.3gp', '.amr'
}
DEFAULT_VAD_PARAMETERS = {'min_silence_duration_ms': 500, 'speech_pad_ms': 200}
VALID_DEVICES = ['cpu', 'cuda', 'auto']
VALID_COMPUTE_TYPES = ['int8', 'float16', 'float32', 'int8_float16', 'int8_float32']
WORD_PATTERN = re.compile(r'\b\w+\b')


class AudioProcessingError(Exception):
    pass


@dataclass
class OverlapSegment:
    text: str
    start: float
    end: float


class AudioIngestor:
    def __init__(
        self,
        vad_parameters: Optional[Dict] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
        max_retries: int = 3,
    ):
        if OVERLAP_WORDS >= TARGET_WORDS:
            raise ValueError(f"OVERLAP_WORDS ({OVERLAP_WORDS}) must be less than TARGET_WORDS ({TARGET_WORDS})")
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        self.vad_parameters = {**DEFAULT_VAD_PARAMETERS, **(vad_parameters or {})}
        self.progress_callback = progress_callback
        self.max_retries = max_retries
        self._closed = False

        self._load_configuration()

        logger.info(f"Loading faster-whisper model '{self.model_size}' on {self.device}")
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    def _load_configuration(self) -> None:
        self.model_size = self._get_config_with_fallback('WHISPER_MODEL', 'AUDIO_MODEL', default='base')
        self.device = self._get_config_with_validation('WHISPER_DEVICE', 'cpu', VALID_DEVICES)
        self.compute_type = self._get_config_with_validation('WHISPER_COMPUTE_TYPE', 'int8', VALID_COMPUTE_TYPES)

    def _get_config_with_fallback(self, *keys: str, default: str) -> str:
        for key in keys:
            value = getattr(settings, key, None)
            if value and isinstance(value, str) and value.strip():
                return value.strip()
        return default

    def _get_config_with_validation(self, key: str, default: str, valid_values: List[str]) -> str:
        value = getattr(settings, key, default)
        if value not in valid_values:
            logger.warning(f"Invalid value '{value}' for {key}, using default '{default}'")
            return default
        return value

    @staticmethod
    def _sanitize_stem(stem: str) -> str:
        return re.sub(r'[^\w\-]', '_', stem)

    @staticmethod
    def _compute_deterministic_hash(value: str) -> str:
        return hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]

    @staticmethod
    def _count_words(text: str) -> int:
        return len(WORD_PATTERN.findall(text))

    def _create_chunk(
        self,
        buffer: list,
        safe_stem: str,
        chunk_index: int,
        file_path: Path,
        start_s: float,
        end_s: float
    ) -> Chunk:
        combined_text = " ".join(s.text.strip() for s in buffer)
        file_hash = self._compute_deterministic_hash(file_path.name)
        chunk_id = f"{safe_stem}_h{file_hash}_t{start_s:.2f}_c{chunk_index:03d}".replace('.', 'p')
        source_prefix = getattr(settings, 'AUDIO_SOURCE_PREFIX', 'data/audio/')
        source_prefix = source_prefix.rstrip('/') + '/'

        return Chunk(
            chunk_id=chunk_id,
            source=f"{source_prefix}{file_path.name}",
            modality="audio",
            text=combined_text,
            embedding_model=getattr(settings, 'TEXT_EMBEDDING_MODEL', 'default'),
            start_s=start_s,
            end_s=end_s,
        )

    def _validate_file(self, file_path: Path) -> None:
        if not file_path.exists():
            raise AudioProcessingError(f"Audio file not found: {file_path}")
        if not file_path.is_file():
            raise AudioProcessingError(f"Path is not a file: {file_path}")
        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_AUDIO_EXTENSIONS:
            raise AudioProcessingError(
                f"Unsupported audio format: {suffix}. "
                f"Supported: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}"
            )
        try:
            file_size = file_path.stat().st_size
            if file_size == 0:
                raise AudioProcessingError(f"Audio file is empty: {file_path}")
            if file_size > MAX_FILE_SIZE_BYTES:
                raise AudioProcessingError(f"Audio file too large: {file_size / (1024**3):.1f}GB")
        except OSError as e:
            raise AudioProcessingError(f"Cannot access file {file_path}: {e}") from e

    def _transcribe_with_retry(self, file_path: Path) -> Iterator:
        last_error = None

        for attempt in range(self.max_retries):
            try:
                segments, info = self.model.transcribe(
                    str(file_path),
                    vad_filter=True,
                    vad_parameters=self.vad_parameters
                )

                if hasattr(info, 'language') and info.language:
                    logger.debug(f"Detected language: {info.language}")

                segment_list = list(segments)
                return iter(segment_list)

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Transcription attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} transcription attempts failed for {file_path.name}")

        raise AudioProcessingError(f"Transcription failed for {file_path.name}: {last_error}") from last_error

    def _create_chunks_from_segments(
        self,
        segments: Iterator,
        safe_stem: str,
        file_path: Path
    ) -> Iterator[Chunk]:
        buffer = []
        buffer_word_count = 0
        chunk_index = 1
        has_new_content = False

        for segment in segments:
            if not segment.text or segment.text.isspace():
                continue

            buffer.append(segment)
            has_new_content = True
            segment_words = self._count_words(segment.text)
            buffer_word_count += segment_words

            if buffer_word_count >= TARGET_WORDS:
                start_s = buffer[0].start
                end_s = buffer[-1].end

                yield self._create_chunk(buffer, safe_stem, chunk_index, file_path, start_s, end_s)
                chunk_index += 1

                max_trims = len(buffer) * 2
                trims = 0
                while len(buffer) > 1 and trims < max_trims:
                    overlap_words = self._count_words(" ".join(s.text.strip() for s in buffer[1:]))
                    if overlap_words <= OVERLAP_WORDS:
                        break
                    removed_words = self._count_words(buffer[0].text.strip())
                    buffer.pop(0)
                    buffer_word_count -= removed_words
                    trims += 1

                if len(buffer) == 1 and buffer_word_count > TARGET_WORDS * 1.5:
                    first_segment = buffer[0]
                    words = first_segment.text.split()
                    overlap_text = " ".join(words[-OVERLAP_WORDS:])
                    buffer[0] = OverlapSegment(overlap_text, first_segment.start, first_segment.end)
                    buffer_word_count = len(words[-OVERLAP_WORDS:])

                has_new_content = False

        if buffer and has_new_content:
            start_s = buffer[0].start
            end_s = buffer[-1].end
            yield self._create_chunk(buffer, safe_stem, chunk_index, file_path, start_s, end_s)

    def process_file(self, file_path: Union[str, Path]) -> List[Chunk]:
        if self._closed:
            raise RuntimeError("AudioIngestor has been closed")

        file_path = Path(file_path)
        self._validate_file(file_path)

        logger.info(f"Processing: {file_path.name}")

        try:
            if self.progress_callback:
                self.progress_callback(0.0)

            segments = self._transcribe_with_retry(file_path)

            suffix = file_path.suffix.lstrip('.')
            safe_stem = self._sanitize_stem(file_path.stem)
            if suffix:
                safe_stem = f"{safe_stem}_{suffix}"

            chunk_list = list(self._create_chunks_from_segments(segments, safe_stem, file_path))

            if not chunk_list:
                logger.warning(f"No speech chunks detected in {file_path.name}")

            logger.info(f"Generated {len(chunk_list)} chunks for {file_path.name}")

            if self.progress_callback:
                self.progress_callback(1.0)

            return chunk_list

        except AudioProcessingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path.name}: {e}")
            raise AudioProcessingError(f"Failed to process {file_path.name}: {e}") from e

    def process_file_streaming(self, file_path: Union[str, Path]) -> Iterator[Chunk]:
        if self._closed:
            raise RuntimeError("AudioIngestor has been closed")

        file_path = Path(file_path)
        self._validate_file(file_path)

        logger.info(f"Processing (streaming): {file_path.name}")

        try:
            segments = self._transcribe_with_retry(file_path)

            suffix = file_path.suffix.lstrip('.')
            safe_stem = self._sanitize_stem(file_path.stem)
            if suffix:
                safe_stem = f"{safe_stem}_{suffix}"

            chunk_count = 0
            for chunk in self._create_chunks_from_segments(segments, safe_stem, file_path):
                yield chunk
                chunk_count += 1

            logger.info(f"Generated {chunk_count} chunks (streaming) for {file_path.name}")

        except AudioProcessingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path.name}: {e}")
            raise AudioProcessingError(f"Failed to process {file_path.name}: {e}") from e

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            if hasattr(self, 'model'):
                del self.model
            logger.debug("AudioIngestor closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def __del__(self):
        if not self._closed:
            self.close()

    def __repr__(self) -> str:
        return f"AudioIngestor(model={self.model_size}, device={self.device}, compute_type={self.compute_type})"