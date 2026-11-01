"""
Heuristic & Entropy Prompt Firewall.
Analyzes text for injection vectors, jailbreak tropes, roleplay bypasses, and suspicious obfuscation.
"""

import math
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SecurityScanResult:
    is_safe: bool
    risk_score: float  # 0.0 (safe) to 1.0 (dangerous)
    detected_threats: List[str]
    entropy: float

    def to_dict(self) -> Dict:
        return asdict(self)


class SentinelFirewall:
    INJECTION_PATTERNS = [
        (r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b", "INSTRUCTION_OVERRIDE"),
        (r"(?i)\byou\s+are\s+now\s+(an\s+unfiltered|in\s+DAN\s+mode|unrestricted)\b", "JAILBREAK_ROLEPLAY"),
        (r"(?i)\bdisregard\s+all\s+(system\s+)?prompts\b", "PROMPT_DISREGARD"),
        (r"(?i)\b(system\s+override|admin\s+mode\s+enabled)\b", "PRIVILEGE_ESCALATION"),
        (r"(?i)<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\]", "SPECIAL_TOKEN_INJECTION"),
        (r"(?i)\b(print|reveal|show|output|leak|share)\s+(your\s+)?((?:initial|system|underlying|original)\s+)+(instructions|prompt|rules)\b", "SYSTEM_PROMPT_EXTRACTION"),
        (r"(?i)\breveal\s+(the\s+)?secret\s+key\b", "CREDENTIAL_HARVESTING"),
    ]

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calculates Shannon entropy of text to detect base64 or encrypted payloads."""
        if not text:
            return 0.0
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        return -sum([p * math.log(p) / math.log(2.0) for p in prob])

    def scan_prompt(self, text: str) -> SecurityScanResult:
        threats: List[str] = []
        score: float = 0.0

        # 1. Pattern checks
        for regex, threat_id in self.INJECTION_PATTERNS:
            if re.search(regex, text):
                threats.append(threat_id)
                score += 0.45

        # 2. Entropy check on long words (detecting raw base64 or hex blobs)
        words = text.split()
        high_entropy_words = []
        for word in words:
            if len(word) > 40:
                ent = self.calculate_entropy(word)
                if ent > 4.6:  # Typical english text is 3.5 - 4.2; base64/hex is > 4.8
                    high_entropy_words.append(word[:12] + "...")

        if high_entropy_words:
            threats.append(f"OBFUSCATED_PAYLOAD({len(high_entropy_words)} tokens)")
            score += 0.35

        overall_entropy = round(self.calculate_entropy(text), 2)
        final_score = min(1.0, round(score, 2))
        is_safe = final_score < 0.40

        return SecurityScanResult(
            is_safe=is_safe,
            risk_score=final_score,
            detected_threats=threats,
            entropy=overall_entropy
        )
