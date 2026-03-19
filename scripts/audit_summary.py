#!/usr/bin/env python3
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from runtime_paths import REAL_EVENTS_AUDIT_FILE as AUDIT_FILE, ensure_runtime_data_dir  # noqa: E402


def load_audit() -> dict:
    ensure_runtime_data_dir()
    if not AUDIT_FILE.exists():
        raise FileNotFoundError(f"audit file not found: {AUDIT_FILE}")
    return json.loads(AUDIT_FILE.read_text(encoding="utf-8"))


def top_drop_reasons(by_source: dict) -> list[tuple[str, int]]:
    totals: dict[str, int] = {}
    for source_data in by_source.values():
        for reason, count in (source_data.get("drop_counts") or {}).items():
            totals[reason] = totals.get(reason, 0) + int(count)
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))


def render_human_summary(payload: dict) -> str:
    by_source = payload.get("by_source") or {}
    kept_total = sum(int(source.get("kept_count", 0)) for source in by_source.values())
    reasons = top_drop_reasons(by_source)

    lines = [
        "# 抓取审计摘要",
        f"- 生成时间：{payload.get('generated_at', 'unknown')}",
        f"- 来源数：{len(by_source)}",
        f"- 保留事件数：{kept_total}",
    ]

    if reasons:
        lines.append("- 主要丢弃原因：")
        for reason, count in reasons[:5]:
            lines.append(f"  - {reason}: {count}")
    else:
        lines.append("- 主要丢弃原因：暂无")

    for source_id, source_data in by_source.items():
        lines.append("")
        lines.append(f"## {source_data.get('label', source_id)}")
        lines.append(
            f"- topic={source_data.get('topic', 'unknown')} / trust={source_data.get('trust_tier', 'unknown')} / seller_bias={source_data.get('seller_signal_bias', 'unknown')}"
        )
        lines.append(f"- 保留：{source_data.get('kept_count', 0)}")
        drop_counts = source_data.get("drop_counts") or {}
        if drop_counts:
            lines.append("- 丢弃：")
            for reason, count in sorted(drop_counts.items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"  - {reason}: {count}")
        kept_samples = source_data.get("kept_samples") or []
        if kept_samples:
            lines.append("- 保留样例：")
            for sample in kept_samples[:2]:
                lines.append(f"  - {sample.get('title', 'untitled')}")
        dropped_samples = source_data.get("dropped_samples") or {}
        if dropped_samples:
            lines.append("- 丢弃样例：")
            for reason, samples in list(dropped_samples.items())[:2]:
                if samples:
                    lines.append(f"  - {reason}: {samples[0].get('title', 'untitled')}")

    return "\n".join(lines)


def main() -> int:
    try:
        payload = load_audit()
        if "--json" in sys.argv:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(render_human_summary(payload))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
