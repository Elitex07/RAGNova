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
    word_count: int


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
                f"overlap_words ({self._overlap_words}) must be less than "
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

        configured_vad: Dict[str, Any] = getattr(
            settings, "WHISPER_VAD_PARAMETERS", {}
        ) or {}
        self._vad_parameters: Dict[str, Any] = {
            **DEFAULT_VAD_PARAMETERS,
            **configured_vad,
            **(vad_parameters or {}),
        }

        self._progress_callback: Optional[Callable[..., None]] = progress_callback
        self._closed: bool = False

        logger.info(
            "Loading faster-whisper model '%s' on %s (%s)",
            self._model_size,
            self._device,
            self._compute_type,
        )
        self._model: WhisperModel = WhisperModel(
            self._model_size,
            device=self._device,
            compute_type=self._compute_type,
        )

    @staticmethod
    def _resolve_model_size(override: Optional[str]) -> str:
        if override and isinstance(override, str) and override.strip():
            return override.strip()
        for attr in ("WHISPER_MODEL_SIZE", "WHISPER_MODEL", "AUDIO_MODEL"):
            value = getattr(settings, attr, None)
            if value and isinstance(value, str) and value.strip():
                return value.strip()
        return "base"

    @staticmethod
    def _resolve_device(override: Optional[str]) -> str:
        if override and isinstance(override, str) and override.strip():
            device = override.strip().lower()
        else:
            raw = None
            for attr in ("WHISPER_DEVICE", "AUDIO_DEVICE"):
                val = getattr(settings, attr, None)
                if val and isinstance(val, str) and val.strip():
                    raw = val.strip()
                    break
            device = (raw or "cpu").lower()

        if device not in VALID_DEVICES:
            logger.warning(
                "Invalid device '%s', falling back to 'cpu'. Valid: %s",
                device,
                sorted(VALID_DEVICES),
            )
            return "cpu"
        return device

    @staticmethod
    def _resolve_compute_type(override: Optional[str]) -> str:
        if override and isinstance(override, str) and override.strip():
            compute_type = override.strip().lower()
        else:
            raw = None
            for attr in ("WHISPER_COMPUTE_TYPE", "AUDIO_COMPUTE_TYPE"):
                val = getattr(settings, attr, None)
                if val and isinstance(val, str) and val.strip():
                    raw = val.strip()
                    break
            compute_type = (raw or "int8").lower()

        if compute_type not in VALID_COMPUTE_TYPES:
            logger.warning(
                "Invalid compute_type '%s', falling back to 'int8'. Valid: %s",
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

    @classmethod
    def _trim_buffer(
        cls,
        buffer: List[OverlapSegment],
        overlap_words: int = OVERLAP_WORDS,
    ) -> List[OverlapSegment]:
        if overlap_words <= 0:
            return []

        total_words: int = sum(seg.word_count for seg in buffer)
        idx: int = 0
        while (
            idx < len(buffer) - 1
            and (total_words - buffer[idx].word_count) >= overlap_words
        ):
            total_words -= buffer[idx].word_count
            idx += 1
        trimmed: List[OverlapSegment] = list(buffer[idx:])

        if len(trimmed) == 1 and trimmed[0].word_count > overlap_words:
            sole: OverlapSegment = trimmed[0]
            matches = list(_WORD_PATTERN.finditer(sole.text))
            if len(matches) > overlap_words:
                slice_start = matches[-overlap_words].start()
                overlap_text = sole.text[slice_start:].strip()
                trimmed[0] = OverlapSegment(
                    text=overlap_text,
                    start=sole.start,
                    end=sole.end,
                    word_count=len(matches[-overlap_words:]),
                )

        return trimmed

    @staticmethod
    def _format_chunk_id(
        safe_stem: str,
        file_hash: str,
        start: float,
        chunk_index: int,
    ) -> str:
        timestamp: str = f"{start:.2f}".replace(".", "p")
        return f"{safe_stem}_h{file_hash}_t{timestamp}_c{chunk_index:03d}"

    def _validate_file(self, file_path: Path) -> int:
        if not file_path.exists():
            raise AudioProcessingError(f"Audio file not found: {file_path}")
        if not file_path.is_file():
            raise AudioProcessingError(f"Path is not a file: {file_path}")
        suffix: str = file_path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise AudioProcessingError(
                f"Unsupported audio format '{suffix}'. "
                f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
            )
        try:
            file_size: int = file_path.stat().st_size
        except OSError as exc:
            raise AudioProcessingError(
                f"Cannot access file {file_path}: {exc}"
            ) from exc
        if file_size == 0:
            raise AudioProcessingError(f"Audio file is empty: {file_path}")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise AudioProcessingError(
                f"Audio file exceeds 2 GB limit: "
                f"{file_size / (1024 ** 3):.1f} GB"
            )
        return file_size

    def _build_chunk(
        self,
        buffer: List[OverlapSegment],
        safe_stem: str,
        file_hash: str,
        chunk_index: int,
        file_path: Path,
    ) -> Chunk:
        combined_text: str = " ".join(seg.text for seg in buffer)
        start_time: float = round(buffer[0].start, 2)
        end_time: float = round(buffer[-1].end, 2)
        chunk_id: str = self._format_chunk_id(
            safe_stem, file_hash, start_time, chunk_index
        )
        metadata: Dict[str, Any] = {
            "source": str(file_path),
            "source_type": "audio",
            "start_time": start_time,
            "end_time": end_time,
            "chunk_index": chunk_index,
            "file_hash": file_hash,
        }
        embedding_model = (
            getattr(settings, "DEFAULT_TEXT_EMBEDDING_MODEL", None)
            or getattr(settings, "EMBEDDING_MODEL", None)
        )

        chunk_kwargs: Dict[str, Any] = {
            "chunk_id": chunk_id,
            "text": combined_text,
            "source": str(file_path),
            "modality": "audio",
            "embedding_model": embedding_model,
            "start_s": start_time,
            "end_s": end_time,
            "start_time": start_time,
            "end_time": end_time,
            "chunk_index": chunk_index,
            "file_hash": file_hash,
            "metadata": metadata,
        }

        try:
            sig = inspect.signature(Chunk)
            has_var_keyword = any(
                p.kind == inspect.Parameter.VAR_KEYWORD
                for p in sig.parameters.values()
            )
            if has_var_keyword:
                return Chunk(**chunk_kwargs)
            filtered = {k: v for k, v in chunk_kwargs.items() if k in sig.parameters}
            return Chunk(**filtered)
        except (ValueError, TypeError):
            try:
                return Chunk(
                    chunk_id=chunk_id,
                    text=combined_text,
                    metadata=metadata,
                )
            except TypeError:
                return Chunk(
                    chunk_id=chunk_id,
                    source=str(file_path),
                    modality="audio",
                    text=combined_text,
                    embedding_model=embedding_model,
                    start_s=start_time,
                    end_s=end_time,
                )

    def _report_progress(self, current: float, total: float) -> None:
        if not self._progress_callback:
            return
        try:
            sig = inspect.signature(self._progress_callback)
            num_params = len([
                p for p in sig.parameters.values()
                if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ])
            if num_params >= 2:
                self._progress_callback(current, total)
            else:
                ratio = min(1.0, max(0.0, current / total)) if total > 0 else 1.0
                self._progress_callback(ratio)
        except Exception:
            try:
                ratio = min(1.0, max(0.0, current / total)) if total > 0 else 1.0
                self._progress_callback(ratio)
            except Exception:
                logger.debug("Progress callback execution failed", exc_info=True)

    def _transcribe_with_retry(self, file_path: Path) -> Iterator[AudioSegment]:
        last_yielded_start: float = -1.0
        last_error: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                segments, info = self._model.transcribe(
                    str(file_path),
                    vad_filter=True,
                    vad_parameters=self._vad_parameters,
                )

                if hasattr(info, "language") and info.language:
                    logger.debug(
                        "Detected language: %s (prob=%.2f)",
                        info.language,
                        getattr(info, "language_probability", 0.0),
                    )

                total_duration: float = getattr(info, "duration", 0.0) or 0.0

                for segment in segments:
                    if segment.start <= last_yielded_start:
                        continue
                    last_yielded_start = segment.start
                    if total_duration > 0:
                        self._report_progress(segment.end, total_duration)
                    yield segment

                if total_duration > 0:
                    self._report_progress(total_duration, total_duration)
                return

            except Exception as exc:
                last_error = exc
                if attempt < self._max_retries - 1:
                    backoff: float = 2.0 ** attempt
                    logger.warning(
                        "Transcription attempt %d/%d failed for '%s': %s. "
                        "Retrying in %.0fs",
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
            f"Transcription failed after {self._max_retries} attempts "
            f"for {file_path.name}: {last_error}"
        ) from last_error

    def _create_chunks_from_segments(
        self,
        segments: Iterator[AudioSegment],
        safe_stem: str,
        file_path: Path,
        file_hash: str,
    ) -> Iterator[Chunk]:
        buffer: List[OverlapSegment] = []
        chunk_index: int = 0
        has_new_content: bool = False

        for segment in segments:
            text = segment.text.strip() if segment.text else ""
            if not text:
                continue

            word_count: int = self._count_words(text)
            if word_count == 0:
                continue

            buffer.append(
                OverlapSegment(
                    text=text,
                    start=segment.start,
                    end=segment.end,
                    word_count=word_count,
                )
            )
            has_new_content = True

            total_words: int = sum(s.word_count for s in buffer)
            if total_words >= self._target_words:
                yield self._build_chunk(
                    buffer, safe_stem, file_hash, chunk_index, file_path
                )
                chunk_index += 1
                buffer = self._trim_buffer(buffer, self._overlap_words)
                has_new_content = False

        if buffer and has_new_content:
            yield self._build_chunk(
                buffer, safe_stem, file_hash, chunk_index, file_path
            )

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("AudioIngestor has been closed")

    def _prepare_file(
        self, file_path: Union[str, Path]
    ) -> tuple[Path, int, str, str]:
        resolved: Path = Path(file_path)
        file_size: int = self._validate_file(resolved)
        safe_stem: str = self._sanitize_stem(resolved.stem)
        suffix: str = resolved.suffix.lstrip(".")
        if suffix:
            safe_stem = f"{safe_stem}_{suffix}"
        file_hash: str = self._compute_file_hash(resolved.name, file_size)
        return resolved, file_size, safe_stem, file_hash

    def process_file_streaming(
        self, file_path: Union[str, Path]
    ) -> Iterator[Chunk]:
        self._ensure_open()
        resolved, file_size, safe_stem, file_hash = self._prepare_file(file_path)
        logger.info("Processing (streaming): %s", resolved.name)

        try:
            segments: Iterator[AudioSegment] = self._transcribe_with_retry(
                resolved
            )
            chunk_count: int = 0
            for chunk in self._create_chunks_from_segments(
                segments, safe_stem, resolved, file_hash
            ):
                yield chunk
                chunk_count += 1

            logger.info(
                "Generated %d chunks (streaming) for %s",
                chunk_count,
                resolved.name,
            )
        except AudioProcessingError:
            raise
        except Exception as exc:
            raise AudioProcessingError(
                f"Failed to process {resolved.name}: {exc}"
            ) from exc

    def process_file(self, file_path: Union[str, Path]) -> List[Chunk]:
        self._ensure_open()
        resolved, file_size, safe_stem, file_hash = self._prepare_file(file_path)
        logger.info("Processing: %s", resolved.name)

        try:
            self._report_progress(0.0, 1.0)

            segments: Iterator[AudioSegment] = self._transcribe_with_retry(
                resolved
            )

            chunks: List[Chunk] = list(
                self._create_chunks_from_segments(
                    segments, safe_stem, resolved, file_hash
                )
            )

            if not chunks:
                logger.warning(
                    "No speech chunks detected in %s", resolved.name
                )

            logger.info(
                "Generated %d chunks for %s", len(chunks), resolved.name
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
        if getattr(self, "_model", None) is not None:
            try:
                del self._model
            except Exception:
                pass
        try:
            if logger is not None:
                logger.debug("AudioIngestor closed")
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
        if getattr(self, "_closed", True):
            return
        self.close()

    def __repr__(self) -> str:
        status: str = "closed" if self._closed else "open"
        return (
            f"AudioIngestor(model={self._model_size!r}, "
            f"device={self._device!r}, "
            f"compute_type={self._compute_type!r}, "
            f"target_words={self._target_words}, "
            f"overlap_words={self._overlap_words}, "
            f"status={status!r})"
        )