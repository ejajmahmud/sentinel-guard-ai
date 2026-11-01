"""
Sentinel Guard AI
Fast zero-latency prompt firewall and canary watermarking engine for AI agents.
"""

from .firewall import SentinelFirewall, SecurityScanResult
from .canary import CanaryEngine

__version__ = "0.1.0"
__all__ = ["SentinelFirewall", "SecurityScanResult", "CanaryEngine"]
