from __future__ import annotations

import hashlib
import logging
import re
import time
import types
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    Union,
    runtime_checkable,
)

from faster_whisper import WhisperModel

try:
    from src.core.config import settings
    from src.core.schemas import Chunk
except ImportError as exc:
    raise ImportError(
        f"Failed to import required dependencies: {exc}. "
        "Ensure src.core.schemas and src.core.config are available."
    ) from exc

logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES: int = 3
DEFAULT_DEVICE: str = "cpu"
DEFAULT_COMPUTE_TYPE: str = "int8"
MAX_FILE_SIZE_BYTES: int = 2 * 1024 * 1024 * 1024

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac",
    ".opus", ".mpeg", ".mp4", ".webm", ".wma", ".mka",
    ".3gp", ".amr",
})

DEFAULT_VAD_PARAMETERS: Dict[str, Any] = {
    "min_silence_duration_ms": 500,
    "speech_pad_ms": 200,
}

VALID_DEVICES: frozenset[str] = frozenset({"cpu", "cuda", "auto"})
VALID_COMPUTE_TYPES: frozenset[str] = frozenset({
    "int8", "float16", "float32", "int8_float16", "int8_float32",
})

_WORD_PATTERN: re.Pattern[str] = re.compile(r"\b\w+\b")


class AudioProcessingError(Exception):
    pass


@runtime_checkable
class AudioSegment(Protocol):
    @property
    def text(self) -> str: ...

    @property
    def start(self) -> float: ...

    @property
    def end(self) -> float: ...


@dataclass(frozen=True, slots=True)
class OverlapSegment:
    text: str
    start: float
    end: float
    word_count: int = 0

    def __post_init__(self) -> None:
        if self.word_count <= 0 and self.text:
            object.__setattr__(
                self,
                "word_count",
                len(_WORD_PATTERN.findall(self.text)),
            )


class AudioIngestor:
    __slots__ = (
        "_model_size",
        "_device",
        "_compute_type",
        "_vad_parameters",
        "_progress_callback",
        "_max_retries",
        "_target_words",
        "_overlap_words",
        "_model",
        "_closed",
    )

    def __init__(
        self,
        model_size: Optional[str] = None,
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
        vad_parameters: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[..., None]] = None,
        max_retries: Optional[int] = None,
        target_words: Optional[int] = None,
        overlap_words: Optional[int] = None,
    ) -> None:
        self._target_words = target_words if target_words is not None else settings.CHUNK_SIZE_WORDS
        self._overlap_words = overlap_words if overlap_words is not None else settings.CHUNK_OVERLAP_WORDS

        if self._target_words < 1:
            raise ValueError("target_words must be at least 1")
        if self._overlap_words < 0:
            raise ValueError("overlap_words must be non-negative")
        if self._overlap_words >= self._target_words:
            raise ValueError("overlap_words must be strictly less than target_words")

        self._max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        if self._max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        self._model_size = (model_size or getattr(settings, "WHISPER_MODEL_SIZE", "base")).strip()
        self._device = (device or DEFAULT_DEVICE).strip().lower()
        self._compute_type = (compute_type or DEFAULT_COMPUTE_TYPE).strip().lower()

        self._vad_parameters = {
            **DEFAULT_VAD_PARAMETERS,
            **(vad_parameters or {}),
        }

        self._progress_callback = progress_callback
        self._closed = False

        self._model = WhisperModel(
            self._model_size,
            device=self._device,
            compute_type=self._compute_type,
        )

    @staticmethod
    def _sanitize_stem(stem: str) -> str:
        return re.sub(r"[^\w\-]", "_", stem)

    @staticmethod
    def _compute_file_hash(file_name: str, file_size: int) -> str:
        # Distinguishes two different audio files that share a bare stem
        # (e.g. "lecture.mp3" ingested from two different folders) — without
        # this, _format_chunk_id's id depends only on the stem and an
        # integer-second timestamp, so two such files can produce identical
        # chunk_ids whenever a segment happens to start on the same second.
        # Since add_chunks() upserts by id (Chapter 7 §2.3), a collision
        # silently overwrites the earlier file's chunk instead of erroring.
        # Hashing name+size (not the full path) keeps the id reproducible
        # across machines/directories for the SAME logical file, so
        # re-ingesting it still correctly upserts in place rather than
        # minting a new id.
        return hashlib.sha256(f"{file_name}_{file_size}".encode("utf-8")).hexdigest()[:8]

    @staticmethod
    def _count_words(text: str) -> int:
        return len(_WORD_PATTERN.findall(text))

    def _validate_file(self, path: Path) -> int:
        if not path.exists():
            raise AudioProcessingError(f"Audio file not found: {path.as_posix()}")
        if not path.is_file():
            raise AudioProcessingError(f"Path is not a regular file: {path.as_posix()}")

        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise AudioProcessingError(f"Unsupported audio format '{suffix}'")

        file_size = path.stat().st_size
        if file_size == 0:
            raise AudioProcessingError(f"Audio file is empty (0 bytes): {path.as_posix()}")

        if file_size > MAX_FILE_SIZE_BYTES:
            raise AudioProcessingError(f"Audio file exceeds 2 GB limit")

        return file_size

    def _prepare_file(
        self,
        file_path: Union[str, Path],
    ) -> Tuple[Path, int, str, str]:
        resolved = Path(file_path)
        file_size = self._validate_file(resolved)

        stem = self._sanitize_stem(resolved.stem)
        suffix = resolved.suffix.lstrip(".").lower()
        safe_stem = f"{stem}_{suffix}" if suffix else stem
        file_hash = self._compute_file_hash(resolved.name, file_size)

        return resolved, file_size, safe_stem, file_hash

    @staticmethod
    def _split_segment(
        seg: OverlapSegment, words_to_keep: int
    ) -> Tuple[Optional[OverlapSegment], Optional[OverlapSegment]]:
        matches = list(_WORD_PATTERN.finditer(seg.text))

        if words_to_keep >= len(matches):
            return seg, None
        if words_to_keep <= 0:
            return None, seg

        split_pos = matches[words_to_keep - 1].end()
        text1 = seg.text[:split_pos].strip()
        text2 = seg.text[split_pos:].strip()

        duration = seg.end - seg.start
        ratio = split_pos / max(1, len(seg.text))
        mid_time = round(seg.start + (duration * ratio), 2)

        seg1 = OverlapSegment(text1, seg.start, mid_time, words_to_keep)
        seg2 = OverlapSegment(text2, mid_time, seg.end, len(matches) - words_to_keep)

        return seg1, seg2

    @classmethod
    def _trim_buffer(
        cls, buffer: List[OverlapSegment], overlap_target: int
    ) -> List[OverlapSegment]:
        if overlap_target <= 0 or not buffer:
            return []

        total = sum(s.word_count for s in buffer)
        if total <= overlap_target:
            return list(buffer)

        words_to_drop = total - overlap_target
        trimmed: List[OverlapSegment] = []
        dropped = 0

        for seg in buffer:
            if dropped >= words_to_drop:
                trimmed.append(seg)
                continue

            if dropped + seg.word_count <= words_to_drop:
                dropped += seg.word_count
                continue

            needed_drop = words_to_drop - dropped
            words_to_keep = seg.word_count - needed_drop

            matches = list(_WORD_PATTERN.finditer(seg.text))
            split_pos = matches[-words_to_keep].start()

            text = seg.text[split_pos:].strip()
            duration = seg.end - seg.start
            ratio = split_pos / max(1, len(seg.text))
            mid_time = round(seg.start + (duration * ratio), 2)

            trimmed.append(OverlapSegment(text, mid_time, seg.end, words_to_keep))
            dropped += needed_drop

        return trimmed

    @staticmethod
    def _format_chunk_id(safe_stem: str, file_hash: str, start_s: float, chunk_index: int) -> str:
        return f"{safe_stem}_h{file_hash}__t{int(start_s)}__c{chunk_index:03d}"

    def _build_chunk(
        self,
        buffer: List[OverlapSegment],
        safe_stem: str,
        file_hash: str,
        idx: int,
        file_path: Path,
    ) -> Chunk:
        text = " ".join(s.text for s in buffer).strip()
        start_val = round(buffer[0].start, 2)
        end_val = round(buffer[-1].end, 2)

        return Chunk(
            chunk_id=self._format_chunk_id(safe_stem, file_hash, start_val, idx),
            text=text,
            source=file_path.as_posix(),
            modality="audio",
            embedding_model=settings.TEXT_EMBEDDING_MODEL,
            start_s=start_val,
            end_s=end_val,
        )

    def _report_progress(self, current: float, total: float) -> None:
        if not self._progress_callback:
            return
        try:
            self._progress_callback(min(1.0, current / total) if total > 0 else 1.0)
        except Exception:
            # A broken caller-supplied callback must never take down
            # ingestion with it. Without this isolation, an exception here
            # propagates into _transcribe_with_retry's own try/except
            # (this is called from inside that loop), gets treated as a
            # transcription failure, burns every retry, and aborts the
            # whole file for a callback bug that has nothing to do with
            # the actual audio.
            logger.debug("Progress callback raised; ignoring it.", exc_info=True)

    def _transcribe_with_retry(self, file_path: Path) -> Iterator[AudioSegment]:
        for attempt in range(self._max_retries):
            try:
                segments, info = self._model.transcribe(
                    str(file_path),
                    vad_filter=True,
                    vad_parameters=self._vad_parameters,
                )
                duration: float = getattr(info, "duration", 0.0) or 0.0

                for segment in segments:
                    if duration > 0:
                        self._report_progress(segment.end, duration)
                    yield segment

                if duration > 0:
                    self._report_progress(duration, duration)
                return

            except Exception:
                if attempt < self._max_retries - 1:
                    time.sleep(2.0 ** attempt)
                else:
                    raise

    def _create_chunks_from_segments(
        self,
        segments: Iterator[AudioSegment],
        safe_stem: str,
        file_hash: str,
        file_path: Path,
    ) -> Iterator[Chunk]:
        buffer: List[OverlapSegment] = []
        chunk_idx: int = 0

        for segment in segments:
            text = segment.text.strip() if segment.text else ""
            if not text:
                continue

            wcount = self._count_words(text)
            if wcount == 0:
                continue

            buffer.append(OverlapSegment(text, segment.start, segment.end, wcount))

            while sum(s.word_count for s in buffer) >= self._target_words:
                current_words = 0
                chunk_segs: List[OverlapSegment] = []
                remaining_buffer: List[OverlapSegment] = []

                for seg in buffer:
                    if current_words >= self._target_words:
                        remaining_buffer.append(seg)
                        continue

                    if current_words + seg.word_count <= self._target_words:
                        chunk_segs.append(seg)
                        current_words += seg.word_count
                    else:
                        needed = self._target_words - current_words
                        seg1, seg2 = self._split_segment(seg, needed)
                        if seg1:
                            chunk_segs.append(seg1)
                        if seg2:
                            remaining_buffer.append(seg2)
                        current_words += needed

                yield self._build_chunk(chunk_segs, safe_stem, file_hash, chunk_idx, file_path)
                chunk_idx += 1

                overlap = self._trim_buffer(chunk_segs, self._overlap_words)
                buffer = overlap + remaining_buffer

        if buffer:
            yield self._build_chunk(buffer, safe_stem, file_hash, chunk_idx, file_path)

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("AudioIngestor has been closed")

    def process_file_streaming(
        self,
        file_path: Union[str, Path],
    ) -> Iterator[Chunk]:
        self._ensure_open()
        resolved, _, safe_stem, file_hash = self._prepare_file(file_path)

        segments = self._transcribe_with_retry(resolved)
        yield from self._create_chunks_from_segments(segments, safe_stem, file_hash, resolved)

    def process_file(
        self,
        file_path: Union[str, Path],
    ) -> List[Chunk]:
        return list(self.process_file_streaming(file_path))

    def close(self) -> None:
        if getattr(self, "_closed", True):
            return
        self._closed = True
        if hasattr(self, "_model"):
            del self._model

    def __enter__(self) -> AudioIngestor:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def ingest_audio(file: Union[str, Path]) -> List[Chunk]:
    with AudioIngestor() as ingestor:
        return ingestor.process_file(file)