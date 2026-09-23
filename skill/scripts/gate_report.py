#!/usr/bin/env python3
"""Aggregate supplied rule checks; does not execute tests or prove evidence authenticity."""
import argparse
import json
import sys
from pathlib import Path

STATUSES = {"PASS", "FAIL", "NOT_APPLICABLE", "UNKNOWN"}


def summarize(data):
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    required = data.get("required_rules")
    checks = data.get("checks")
    if not isinstance(required, list) or not required or any(
        not isinstance(x, str) or not x.strip() for x in required
    ) or len(set(required)) != len(required):
        raise ValueError("required_rules must contain unique nonempty rule IDs")
    if not isinstance(checks, list):
        raise ValueError("checks must be an array")
    indexed = {}
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("each check must be an object")
        rule = check.get("rule_id")
        if not isinstance(rule, str) or not rule.strip() or rule in indexed:
            raise ValueError("check rule_id must be nonempty and unique")
        status = check.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError("invalid check status")
        key = "evidence" if status in {"PASS", "FAIL"} else "reason"
        if not isinstance(check.get(key), str) or not check[key].strip():
            raise ValueError(f"{rule}: {status} requires nonempty {key}")
        indexed[rule] = check
    extra = sorted(set(indexed) - set(required))
    if extra:
        raise ValueError("checks outside required_rules: " + ", ".join(extra))
    if data.get("exceptions"):
        raise ValueError("exceptions require human review; automatic waiver is unsupported")
    rows = [indexed.get(rule, {"rule_id": rule, "status": "UNKNOWN", "reason": "missing check"})
            for rule in required]
    failed = [r["rule_id"] for r in rows if r["status"] == "FAIL"]
    unknown = [r["rule_id"] for r in rows if r["status"] == "UNKNOWN"]
    applicable = [r for r in rows if r["status"] != "NOT_APPLICABLE"]
    gate = "NOT_READY" if failed else "BLOCKED" if unknown or not applicable else "READY"
    return {"gate": gate, "failed_rules": failed, "unknown_rules": unknown,
            "checks": rows,
            "scope": "supplied rule set only; not overall task or release approval",
            "evidence_authenticity": "not_verified",
            "note": "all rules not applicable is insufficient for automatic readiness" if not applicable else ""}


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a supplied required rule set. Does not run tests or verify evidence. "
                    "Exit: 0 READY, 1 NOT_READY, 2 BLOCKED, 3 invalid input.",
        epilog='Input: {"required_rules":["UT-14"],"checks":[{"rule_id":"UT-14",'
               '"status":"PASS","evidence":"actual command/log location"}]}. '
               'UNKNOWN and NOT_APPLICABLE require reason; PASS and FAIL require evidence. '
               'Missing checks become UNKNOWN. Exceptions are not automatically approved.')
    parser.add_argument("input", type=Path, help="UTF-8 JSON file containing required_rules and checks")
    args = parser.parse_args()
    try:
        # Reject duplicate JSON keys instead of silently trusting the last value.
        def unique_pairs(pairs):
            obj = {}
            for key, value in pairs:
                if key in obj:
                    raise ValueError("duplicate JSON key: " + key)
                obj[key] = value
            return obj
        data = json.loads(args.input.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
        result = summarize(data)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"gate": "INVALID", "error": str(exc)}, ensure_ascii=False))
        return 3
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"READY": 0, "NOT_READY": 1, "BLOCKED": 2}[result["gate"]]


if __name__ == "__main__":
    sys.exit(main())
