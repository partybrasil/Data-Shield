"""
Shannon entropy analysis for Data-Shield.

Provides file-level and block-level entropy computation used in Layer 4
of the pattern engine to flag high-entropy blobs that may be secrets or
encrypted data.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Generator

from loguru import logger

from datashield.core.exceptions import EntropyError

# Default entropy thresholds (bits per byte, max = 8.0)
DEFAULT_THRESHOLD    = 7.2   # above this → HIGH_ENTROPY_BLOB
BASE64_THRESHOLD     = 6.0   # base64-encoded secrets typically 5.8-6.4
BLOCK_SIZE           = 1024  # bytes per sliding-window block
SLIDING_STEP         = 256   # step for sliding-window analysis
MAX_BYTES_TO_ANALYSE = 512 * 1024  # 512 KB max read per file


def _shannon_entropy(data: bytes) -> float:
    """Compute Shannon entropy of a byte sequence.

    Args:
        data: Raw bytes to measure.

    Returns:
        Entropy in bits per byte (0.0 – 8.0).  Returns 0.0 for empty input.
    """
    if not data:
        return 0.0
    length = len(data)
    freq: dict[int, int] = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    return -sum(
        (count / length) * math.log2(count / length)
        for count in freq.values()
    )


def file_entropy(path: Path, max_bytes: int = MAX_BYTES_TO_ANALYSE) -> float:
    """Compute Shannon entropy for the first *max_bytes* of a file.

    Args:
        path:      Path to the file.
        max_bytes: Maximum bytes to read. Defaults to 512 KB.

    Returns:
        Entropy in bits per byte.

    Raises:
        EntropyError: If the file cannot be read.
    """
    try:
        with path.open("rb") as fh:
            data = fh.read(max_bytes)
        return _shannon_entropy(data)
    except (OSError, PermissionError) as exc:
        raise EntropyError(f"Cannot read {path}: {exc}") from exc


def block_entropies(
    path: Path,
    block_size: int = BLOCK_SIZE,
    step: int = SLIDING_STEP,
    max_bytes: int = MAX_BYTES_TO_ANALYSE,
) -> Generator[tuple[int, float], None, None]:
    """Yield (offset, entropy) pairs using a sliding window over the file.

    This allows detection of high-entropy *sections* inside otherwise
    low-entropy files (e.g. a private key embedded in an XML config).

    Args:
        path:       Path to the file.
        block_size: Window size in bytes.
        step:       Step between windows in bytes.
        max_bytes:  Maximum bytes to read.

    Yields:
        Tuples of ``(byte_offset, entropy_value)``.

    Raises:
        EntropyError: If the file cannot be read.
    """
    try:
        with path.open("rb") as fh:
            data = fh.read(max_bytes)
    except (OSError, PermissionError) as exc:
        raise EntropyError(f"Cannot read {path}: {exc}") from exc

    offset = 0
    while offset + block_size <= len(data):
        block = data[offset : offset + block_size]
        yield offset, _shannon_entropy(block)
        offset += step


def is_high_entropy(
    path: Path,
    threshold: float = DEFAULT_THRESHOLD,
) -> tuple[bool, float]:
    """Determine whether a file has suspiciously high entropy.

    Args:
        path:      Path to the file.
        threshold: Bits/byte threshold above which the file is flagged.

    Returns:
        Tuple of ``(is_high, entropy_value)``.
    """
    try:
        entropy = file_entropy(path)
        return entropy >= threshold, entropy
    except EntropyError:
        return False, 0.0


def has_high_entropy_block(
    path: Path,
    threshold: float = DEFAULT_THRESHOLD,
    block_size: int = BLOCK_SIZE,
    step: int = SLIDING_STEP,
) -> tuple[bool, float, int]:
    """Check if any block within the file exceeds the entropy threshold.

    Args:
        path:       Path to the file.
        threshold:  Entropy threshold.
        block_size: Sliding window block size in bytes.
        step:       Sliding window step in bytes.

    Returns:
        Tuple of ``(found, max_entropy, byte_offset_of_max)``.
    """
    max_entropy = 0.0
    max_offset  = 0
    found       = False

    for offset, entropy in block_entropies(path, block_size, step):
        if entropy > max_entropy:
            max_entropy = entropy
            max_offset  = offset
        if entropy >= threshold:
            found = True

    return found, max_entropy, max_offset


def looks_like_base64_secret(data: bytes) -> bool:
    """Heuristic: does this byte block look like a base64-encoded secret?

    A base64 secret typically has:
    - Only printable ASCII characters in the base64 alphabet
    - Entropy between 5.8 and 6.4 bits/byte
    - Length that is a multiple of 4 (or close)

    Args:
        data: Bytes to evaluate.

    Returns:
        True if the heuristic matches.
    """
    if len(data) < 16:
        return False

    import re
    b64_re = re.compile(rb"^[A-Za-z0-9+/=]{16,}$")
    stripped = data.strip()
    if not b64_re.match(stripped):
        return False

    entropy = _shannon_entropy(stripped)
    return BASE64_THRESHOLD <= entropy <= DEFAULT_THRESHOLD


def classify_entropy(entropy: float) -> str:
    """Return a human-readable classification for an entropy value.

    Args:
        entropy: Bits-per-byte value (0.0 – 8.0).

    Returns:
        One of ``"low"``, ``"medium"``, ``"high"``, or ``"very_high"``.
    """
    if entropy < 3.5:
        return "low"
    if entropy < 6.0:
        return "medium"
    if entropy < DEFAULT_THRESHOLD:
        return "high"
    return "very_high"
