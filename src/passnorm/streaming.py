"""Line-at-a-time normalization for large password lists.

Breach corpora and export dumps used to test a strength scorer can run into
the hundreds of millions of lines. `iter_normalize` and `iter_normalize_file`
never hold more than one line in memory at a time - they lean on the fact
that iterating a file object in Python already pulls lines lazily off the
underlying buffered reader, so callers get the same behavior whether the
source is a 10-line list or a 10 GB one.
"""

from typing import Iterable, Iterator, Union

from .core import normalize

Line = Union[str, bytes]


def iter_normalize(source: Iterable[Line]) -> Iterator[str]:
    """Yield normalized, non-empty passwords from an iterable of lines.

    `source` can be an open file object, a socket's makefile(), or any
    iterator that produces one line per item, as str or bytes. Bytes are
    decoded as UTF-8 with lossy replacement rather than raising, since a
    single malformed line in a multi-gigabyte dump should not abort the
    whole run.
    """
    for raw_line in source:
        if isinstance(raw_line, bytes):
            raw_line = raw_line.decode("utf-8", errors="replace")
        candidate = normalize(raw_line)
        if candidate:
            yield candidate


def iter_normalize_file(path: str, encoding: str = "utf-8") -> Iterator[str]:
    """Stream normalized passwords from a file on disk, one line at a time."""
    with open(path, "r", encoding=encoding, errors="replace", newline="") as handle:
        yield from iter_normalize(handle)
