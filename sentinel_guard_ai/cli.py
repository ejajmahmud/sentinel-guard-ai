"""
CLI Interface for Sentinel Guard AI.
"""

import argparse
import json
import sys
from .firewall import SentinelFirewall
from .canary import CanaryEngine


def main():
    parser = argparse.ArgumentParser(
        prog="sentinel",
        description="Zero-latency prompt firewall, jailbreak detector, and canary watermarking for AI agents"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: scan
    scan_p = subparsers.add_parser("scan", help="Scan text or prompt for injection vectors")
    scan_p.add_argument("text", help="Text string or prompt to evaluate")

    # Subcommand: watermark
    wm_p = subparsers.add_parser("watermark", help="Embed an invisible canary token into a system prompt")
    wm_p.add_argument("prompt", help="System prompt text")
    wm_p.add_argument("--key", default="secret-key-123", help="Secret key for signature")
    wm_p.add_argument("--tag", default="agent-01", help="Identifier tag")

    # Subcommand: inspect-leak
    leak_p = subparsers.add_parser("inspect-leak", help="Scan model response for leaked canary watermarks")
    leak_p.add_argument("text", help="Text to scan for canary leaks")

    args = parser.parse_args()

    if args.command == "scan":
        firewall = SentinelFirewall()
        res = firewall.scan_prompt(args.text)
        print("=== Sentinel Guard AI Scan ===")
        print(f"Status   : {'[PASSED] SAFE' if res.is_safe else '[BLOCKED] THREAT DETECTED'}")
        print(f"Risk     : {res.risk_score} / 1.0")
        print(f"Entropy  : {res.entropy}")
        print(f"Threats  : {', '.join(res.detected_threats) if res.detected_threats else 'None'}")
        if not res.is_safe:
            sys.exit(1)

    elif args.command == "watermark":
        token = CanaryEngine.generate_token(args.key, args.tag)
        watermarked = CanaryEngine.embed_watermark(args.prompt, token)
        print(f"Generated Canary Token: {token}")
        print("--- Watermarked Text (Invisible to humans, preserved in tokens) ---")
        print(watermarked)

    elif args.command == "inspect-leak":
        detected = CanaryEngine.detect_watermark(args.text)
        if detected:
            print(f"[ALERT] Canary Leak Confirmed! Extracted Token: {detected}")
            sys.exit(2)
        else:
            print("[CLEAN] No canary token detected in target text.")


if __name__ == "__main__":
    main()
