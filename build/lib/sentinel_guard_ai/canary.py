"""
Invisible Canary Watermark Engine.
Embeds and detects invisible zero-width Unicode signatures to identify prompt leakage and system exfiltration.
"""

import hashlib
from typing import Optional, Tuple


class CanaryEngine:
    # Zero-width spaces and joiners used for binary encoding
    ZERO_WIDTH_0 = "\u200B"  # Zero-width space
    ZERO_WIDTH_1 = "\u200C"  # Zero-width non-joiner
    MARKER_START = "\u200D\u200E"  # Distinct start delimiter
    MARKER_END = "\u200E\u200D"    # Distinct end delimiter

    @classmethod
    def generate_token(cls, secret_key: str, tag: str = "sys") -> str:
        """Derives a short deterministic token hash."""
        digest = hashlib.sha256(f"{secret_key}:{tag}".encode("utf-8")).hexdigest()[:8]
        return f"{tag}:{digest}"

    @classmethod
    def embed_watermark(cls, text: str, token: str) -> str:
        """Converts token into invisible zero-width characters and attaches to text."""
        # Convert string to binary bits
        bits = "".join(f"{ord(c):08b}" for c in token)
        encoded_bits = "".join(cls.ZERO_WIDTH_1 if b == "1" else cls.ZERO_WIDTH_0 for b in bits)
        hidden_payload = f"{cls.MARKER_START}{encoded_bits}{cls.MARKER_END}"
        
        # Inject at the first newline or at the start
        if "\n" in text:
            idx = text.find("\n")
            return text[:idx] + hidden_payload + text[idx:]
        return hidden_payload + text

    @classmethod
    def detect_watermark(cls, text: str) -> Optional[str]:
        """Scans arbitrary text for embedded zero-width watermarks."""
        start_idx = text.find(cls.MARKER_START)
        end_idx = text.find(cls.MARKER_END)

        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            return None

        payload_bits = text[start_idx + len(cls.MARKER_START):end_idx]
        bit_str = []
        for ch in payload_bits:
            if ch == cls.ZERO_WIDTH_1:
                bit_str.append("1")
            elif ch == cls.ZERO_WIDTH_0:
                bit_str.append("0")

        bits_joined = "".join(bit_str)
        if len(bits_joined) % 8 != 0:
            return None

        # Decode characters
        chars = []
        for i in range(0, len(bits_joined), 8):
            byte = bits_joined[i:i+8]
            chars.append(chr(int(byte, 2)))

        return "".join(chars)
