# passnorm

A password almost never arrives clean. It gets copy-pasted out of a
spreadsheet with a trailing tab, exported from a CSV with a stray BOM at the
front of the file, or typed on a phone keyboard that silently substitutes a
full-width digit for an ASCII one. If you feed that straight into a strength
scorer, you get inconsistent results for what is, to the user, the same
password - and if you're comparing entries in a breach list, near-duplicates
that should collapse into one row don't.

`passnorm` is the normalization step that goes in front of that kind of
analysis. It does not score anything. It takes messy input and returns a
canonical string:

- strips a leading UTF-8 BOM
- strips trailing `\r` / `\n` left over from file reads
- applies Unicode NFKC normalization so visually-identical characters compare
  equal
- drops control and invisible format characters (zero-width joiners,
  directional marks) that inflate length without being visible

## Usage

Normalizing a single value:

```python
from passnorm import normalize

normalize("hunter2\r\n")        # "hunter2"
normalize("﻿hunter2")      # "hunter2"
normalize("hunter​2")      # "hunter2"  (zero-width space removed)
```

Streaming a large file without loading it into memory:

```python
from passnorm import iter_normalize_file

for password in iter_normalize_file("breach-corpus.txt"):
    ...  # hand each one to a scorer, one at a time
```

`iter_normalize_file` opens the file and reads it line by line - it holds one
line in memory at a time, so a 10 GB corpus and a 10-line test fixture behave
the same way. If you already have an open file, socket, or other line
iterator, use `iter_normalize` directly:

```python
from passnorm import iter_normalize

with open("breach-corpus.txt", encoding="utf-8", newline="") as f:
    for password in iter_normalize(f):
        ...
```

## Status

Early skeleton. Normalization rules and streaming entry points work; there
is no CLI and no strength scoring yet (that's a separate concern this
library feeds into).

## License

MIT, see LICENSE.
