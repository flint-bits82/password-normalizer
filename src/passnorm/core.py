"""Normalization of a single password string."""

import unicodedata

# Format characters (category Cf) include zero-width joiners and directional
# marks that render invisibly but still count toward length and character-set
# checks in a naive strength scorer. Control characters (Cc) are almost never
# something a user meant to type into a password field; they show up from
# copy-paste artifacts or broken exports. Both get stripped so two passwords
# that look identical on screen normalize to the same string.
_STRIP_CATEGORIES = ("Cc", "Cf")


def normalize(raw: str) -> str:
    """Return a canonical form of a password string.

    This does not change what the password "means" for authentication
    purposes - it exists so that strength analysis and display logic see a
    consistent representation instead of being thrown off by BOMs, trailing
    line-ending bytes left over from a file read, or Unicode code points that
    render the same but are different bytes (e.g. full-width digits vs
    ASCII digits).
    """
    if not isinstance(raw, str):
        raise TypeError(f"expected str, got {type(raw).__name__}")

    text = raw.rstrip("\r\n")
    text = text.lstrip("﻿")
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) not in _STRIP_CATEGORIES)
    return text
