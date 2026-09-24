from __future__ import annotations

import hashlib
import inspect
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

TARGET_WORDS: int = getattr(settings, "AUDIO_CHUNK_TARGET_WORDS", 300)
OVERLAP_WORDS: int = getattr(settings, "AUDIO_CHUNK_OVERLAP_WORDS", 50)
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
        self._target_words: int = (
            target_words
            if target_words is not None
            else getattr(settings, "AUDIO_CHUNK_TARGET_WORDS", TARGET_WORDS)
        )
        self._overlap_words: int = (
            overlap_words
            if overlap_words is not None
            else getattr(settings, "AUDIO_CHUNK_OVERLAP_WORDS", OVERLAP_WORDS)
        )

        if self._overlap_words >= self._target_words:
            raise ValueError(
                f"overlap_words ({self._overlap_words}) must be strictly less than "
                f"target_words ({self._target_words})"
            )

        resolved_retries: int = (
            max_retries
            if max_retries is not None
            else getattr(settings, "WHISPER_MAX_RETRIES", 3)
        )
        if resolved_retries < 1:
            raise ValueError("max_retries must be at least 1")
        self._max_retries: int = resolved_retries

        self._model_size: str = self._resolve_model_size(model_size)
        self._device: str = self._resolve_device(device)
        self._compute_type: str = self._resolve_compute_type(compute_type)

        configured_vad: Dict[str, Any] = (
            getattr(settings, "WHISPER_VAD_PARAMETERS", {}) or {}
        )
        self._vad_parameters: Dict[str, Any] = {
            **DEFAULT_VAD_PARAMETERS,
            **configured_vad,
            **(vad_parameters or {}),
        }

        self._progress_callback: Optional[Callable[..., None]] = progress_callback
        self._closed: bool = False

        logger.info(
            "Initializing AudioIngestor (model=%s, device=%s, compute_type=%s, target_words=%d, overlap_words=%d)",
            self._model_size,
            self._device,
            self._compute_type,
            self._target_words,
            self._overlap_words,
        )
        self._model: WhisperModel = WhisperModel(
            self._model_size,
            device=self._device,
            compute_type=self._compute_type,
        )

    @staticmethod
    def _resolve_model_size(override: Optional[str]) -> str:
        if override and str(override).strip():
            return str(override).strip()
        for attr in ("WHISPER_MODEL_SIZE", "WHISPER_MODEL", "AUDIO_MODEL"):
            val = getattr(settings, attr, None)
            if val and str(val).strip():
                return str(val).strip()
        return "base"

    @staticmethod
    def _resolve_device(override: Optional[str]) -> str:
        raw = override or getattr(settings, "WHISPER_DEVICE", None) or "cpu"
        device = str(raw).strip().lower()
        if device not in VALID_DEVICES:
            logger.warning(
                "Invalid device '%s', falling back to 'cpu'. Valid devices: %s",
                device,
                sorted(VALID_DEVICES),
            )
            return "cpu"
        return device

    @staticmethod
    def _resolve_compute_type(override: Optional[str]) -> str:
        raw = override or getattr(settings, "WHISPER_COMPUTE_TYPE", None) or "int8"
        compute_type = str(raw).strip().lower()
        if compute_type not in VALID_COMPUTE_TYPES:
            logger.warning(
                "Invalid compute_type '%s', falling back to 'int8'. Valid types: %s",
                compute_type,
                sorted(VALID_COMPUTE_TYPES),
            )
            return "int8"
        return compute_type

    @staticmethod
    def _sanitize_stem(stem: str) -> str:
        return re.sub(r"[^\w\-]", "_", stem)

    @staticmethod
    def _compute_file_hash(file_name: str, file_size: int) -> str:
        return hashlib.sha256(
            f"{file_name}_{file_size}".encode("utf-8")
        ).hexdigest()[:16]

    @staticmethod
    def _count_words(text: str) -> int:
        return len(_WORD_PATTERN.findall(text))

    def _validate_file(self, path: Path) -> int:
        if not path.exists():
            raise AudioProcessingError(f"Audio file not found: {path}")
        if not path.is_file():
            raise AudioProcessingError(f"Path is not a regular file: {path}")

        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise AudioProcessingError(
                f"Unsupported audio format '{suffix}'. Supported formats: {sorted(SUPPORTED_EXTENSIONS)}"
            )

        try:
            file_size = path.stat().st_size
        except OSError as exc:
            raise AudioProcessingError(
                f"Cannot access file metadata for {path}: {exc}"
            ) from exc

        if file_size == 0:
            raise AudioProcessingError(f"Audio file is empty (0 bytes): {path}")

        if file_size > MAX_FILE_SIZE_BYTES:
            raise AudioProcessingError(
                f"Audio file exceeds 2 GB limit: {file_size / (1024 ** 3):.2f} GB"
            )

        return file_size

    def _prepare_file(
        self,
        file_path: Union[str, Path],
    ) -> Tuple[Path, int, str, str]:
        resolved = Path(file_path)
        file_size = self._validate_file(resolved)

        stem = self._sanitize_stem(resolved.stem)
        suffix = resolved.suffix.lstrip(".")
        safe_stem = f"{stem}_{suffix}" if suffix else stem
        file_hash = self._compute_file_hash(resolved.name, file_size)

        return resolved, file_size, safe_stem, file_hash

    @staticmethod
    def _split_segment(
        seg: OverlapSegment, words_to_keep: int
    ) -> tuple[Optional[OverlapSegment], Optional[OverlapSegment]]:
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
            if dropped == words_to_drop:
                trimmed.append(seg)
            elif dropped + seg.word_count <= words_to_drop:
                dropped += seg.word_count
            else:
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

    def _format_chunk_id(
        self,
        safe_stem: str,
        file_hash: str,
        start_s: float,
        chunk_index: int,
    ) -> str:
        timestamp = f"{start_s:.2f}".replace(".", "p")
        return f"{safe_stem}_h{file_hash}_t{timestamp}_c{chunk_index:03d}"

    def _build_chunk(
        self,
        buffer: List[OverlapSegment],
        safe_stem: str,
        file_hash: str,
        idx: int,
        file_path: Path,
        start_s: Optional[float] = None,
        end_s: Optional[float] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Chunk:
        text = " ".join(s.text for s in buffer)
        start_val = round(
            start_s if start_s is not None else (buffer[0].start if buffer else 0.0),
            2,
        )
        end_val = round(
            end_s if end_s is not None else (buffer[-1].end if buffer else 0.0),
            2,
        )

        chunk_id = self._format_chunk_id(safe_stem, file_hash, start_val, idx)

        emb_model = getattr(
            settings,
            "DEFAULT_TEXT_EMBEDDING_MODEL",
            getattr(settings, "EMBEDDING_MODEL", None),
        )

        metadata: Dict[str, Any] = {
            "source": str(file_path),
            "source_type": "audio",
            "modality": "audio",
            "start": start_val,
            "end": end_val,
            "start_time": start_val,
            "end_time": end_val,
            "start_s": start_val,
            "end_s": end_val,
            "index": idx,
            "chunk_index": idx,
            "hash": file_hash,
            "file_hash": file_hash,
        }

        chunk_kwargs: Dict[str, Any] = {
            "chunk_id": chunk_id,
            "text": text,
            "source": str(file_path),
            "modality": "audio",
            "embedding_model": emb_model,
            "start_s": start_val,
            "end_s": end_val,
            "metadata": metadata,
        }

        try:
            sig = inspect.signature(Chunk)
            if any(
                p.kind == inspect.Parameter.VAR_KEYWORD
                for p in sig.parameters.values()
            ):
                return Chunk(**chunk_kwargs)
            filtered = {k: v for k, v in chunk_kwargs.items() if k in sig.parameters}
            return Chunk(**filtered)
        except Exception:
            return Chunk(chunk_id=chunk_id, text=text, metadata=metadata)

    _create_chunk = _build_chunk

    def _report_progress(self, current: float, total: float) -> None:
        if not self._progress_callback:
            return
        try:
            sig = inspect.signature(self._progress_callback)
            if len(sig.parameters) >= 2:
                self._progress_callback(current, total)
            else:
                self._progress_callback(
                    min(1.0, current / total) if total > 0 else 1.0
                )
        except Exception:
            logger.debug("Progress callback execution failed", exc_info=True)

    def _transcribe_with_retry(self, file_path: Path) -> Iterator[AudioSegment]:
        last_yielded_start: float = -1.0
        last_err: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                segments, info = self._model.transcribe(
                    str(file_path),
                    vad_filter=True,
                    vad_parameters=self._vad_parameters,
                )
                duration: float = getattr(info, "duration", 0.0) or 0.0

                if hasattr(info, "language") and info.language:
                    logger.debug(
                        "Detected language '%s' (prob=%.2f) for %s",
                        info.language,
                        getattr(info, "language_probability", 0.0),
                        file_path.name,
                    )

                for segment in segments:
                    if segment.start <= last_yielded_start + 1e-4:
                        continue
                    last_yielded_start = segment.start
                    if duration > 0:
                        self._report_progress(segment.end, duration)
                    yield segment

                if duration > 0:
                    self._report_progress(duration, duration)
                return

            except Exception as exc:
                last_err = exc
                if attempt < self._max_retries - 1:
                    backoff = 2.0 ** attempt
                    logger.warning(
                        "Transcription attempt %d/%d failed for '%s': %s. Retrying in %.0fs...",
                        attempt + 1,
                        self._max_retries,
                        file_path.name,
                        exc,
                        backoff,
                    )
                    time.sleep(backoff)
                else:
                    logger.error(
                        "All %d transcription attempts failed for '%s'",
                        self._max_retries,
                        file_path.name,
                    )

        raise AudioProcessingError(
            f"Transcription failed for {file_path.name} after {self._max_retries} attempts: {last_err}"
        ) from last_err

    def _create_chunks_from_segments(
        self,
        segments: Iterator[AudioSegment],
        safe_stem: str,
        file_path: Path,
        file_hash: str,
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
                    if current_words == self._target_words:
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

                yield self._build_chunk(
                    chunk_segs, safe_stem, file_hash, chunk_idx, file_path
                )
                chunk_idx += 1

                buffer = self._trim_buffer(chunk_segs, self._overlap_words) + remaining_buffer

        if buffer:
            yield self._build_chunk(
                buffer, safe_stem, file_hash, chunk_idx, file_path
            )

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("AudioIngestor has been closed")

    def process_file_streaming(
        self,
        file_path: Union[str, Path],
    ) -> Iterator[Chunk]:
        self._ensure_open()
        resolved, file_size, safe_stem, file_hash = self._prepare_file(file_path)
        logger.info(
            "Starting streaming audio ingestion: %s (%.2f MB)",
            resolved.name,
            file_size / (1024 * 1024),
        )

        try:
            segments = self._transcribe_with_retry(resolved)
            chunk_count = 0
            for chunk in self._create_chunks_from_segments(
                segments, safe_stem, resolved, file_hash
            ):
                yield chunk
                chunk_count += 1

            logger.info(
                "Streaming ingestion complete for %s: generated %d chunks",
                resolved.name,
                chunk_count,
            )
        except AudioProcessingError:
            raise
        except Exception as exc:
            raise AudioProcessingError(
                f"Failed to process {resolved.name}: {exc}"
            ) from exc

    def process_file(
        self,
        file_path: Union[str, Path],
    ) -> List[Chunk]:
        self._ensure_open()
        resolved, file_size, safe_stem, file_hash = self._prepare_file(file_path)
        logger.info(
            "Starting batch audio ingestion: %s (%.2f MB)",
            resolved.name,
            file_size / (1024 * 1024),
        )

        start_time = time.perf_counter()
        try:
            self._report_progress(0.0, 1.0)
            segments = self._transcribe_with_retry(resolved)
            chunks: List[Chunk] = list(
                self._create_chunks_from_segments(
                    segments, safe_stem, resolved, file_hash
                )
            )

            if not chunks:
                logger.warning("No speech detected in audio file: %s", resolved.name)

            elapsed = time.perf_counter() - start_time
            logger.info(
                "Batch audio ingestion complete for %s: generated %d chunks in %.2fs",
                resolved.name,
                len(chunks),
                elapsed,
            )

            self._report_progress(1.0, 1.0)
            return chunks

        except AudioProcessingError:
            raise
        except Exception as exc:
            raise AudioProcessingError(
                f"Failed to process {resolved.name}: {exc}"
            ) from exc

    def close(self) -> None:
        if getattr(self, "_closed", False):
            return
        self._closed = True

        if hasattr(self, "_model"):
            try:
                del self._model
            except Exception:
                pass

        try:
            if logger is not None:
                logger.debug("AudioIngestor closed successfully")
        except Exception:
            pass

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
        self.close()

    def __repr__(self) -> str:
        status = "closed" if self._closed else "open"
        return (
            f"AudioIngestor(model={self._model_size!r}, "
            f"device={self._device!r}, "
            f"compute_type={self._compute_type!r}, "
            f"target_words={self._target_words}, "
            f"overlap_words={self._overlap_words}, "
            f"status={status!r})"
        )