'''
Utilities for reading text files with BOM-aware UTF-8/UTF-16/UTF-32 support
and robust fallbacks to preserve text and positions.
'''
from typing import List, Optional
def read_text_file(path: str) -> str:
    """
    Try reading text with several encodings, returning decoded string.
    Tries common UTF encodings (with/without BOM), then Windows and Latin-1.
    As a final fallback, reads binary and decodes using UTF-16 (replace) and,
    if that appears incorrect (e.g., lots of NULs), UTF-8 (replace).
    Raises the last exception from text-mode attempts if all fallbacks fail.
    """
    encodings: List[str] = [
        # UTF-8 variants first
        "utf-8",
        "utf-8-sig",
        # UTF-16/32 (BOM-aware generic first, then explicit endianness)
        "utf-16",
        "utf-16-le",
        "utf-16-be",
        "utf-32",
        "utf-32-le",
        "utf-32-be",
        # Common single-byte encodings on Windows/Western Europe
        "cp1252",
        "latin-1",
    ]
    last_exc: Optional[Exception] = None
    # First pass: try opening in text mode with explicit encodings
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except Exception as e:
            last_exc = e
            continue
    # Final fallback: binary read and decode heuristically
    try:
        with open(path, "rb") as f:
            data = f.read()
    except Exception:
        if last_exc:
            raise last_exc
        raise
    # BOM sniffing for reliability
    try:
        if data.startswith(b"\x00\x00\xfe\xff"):  # UTF-32 BE BOM
            return data.decode("utf-32-be")
        if data.startswith(b"\xff\xfe\x00\x00"):  # UTF-32 LE BOM
            return data.decode("utf-32-le")
        if data.startswith(b"\xfe\xff"):  # UTF-16 BE BOM
            return data.decode("utf-16-be")
        if data.startswith(b"\xff\xfe"):  # UTF-16 LE BOM
            return data.decode("utf-16-le")
        if data.startswith(b"\xef\xbb\xbf"):  # UTF-8 BOM
            return data.decode("utf-8-sig")
    except Exception:
        # Ignore and continue to generic fallbacks
        pass
    # Try UTF-16 with replacement; if it looks like mis-decoded ASCII (many NULs),
    # prefer UTF-8 with replacement (common for unknown text files).
    try:
        s = data.decode("utf-16", errors="replace")
        if s:
            nul_ratio = s.count("\x00") / max(1, len(s))
            if nul_ratio <= 0.2:
                return s
    except Exception:
        pass
    # Robust last resort: UTF-8 with replacement never raises and preserves structure
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        if last_exc:
            raise last_exc
        raise