#!/usr/bin/env python3
import importlib.util
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "publish_guard.py"


def load_module():
    spec = importlib.util.spec_from_file_location("publish_guard", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    errors: list[str] = []

    with tempfile.TemporaryDirectory() as runtime_tmp:
        runtime_root = Path(runtime_tmp)
        data_dir = runtime_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        source_status = {
            "generated_at": "2026-03-13T00:00:00Z",
            "by_source": {
                "amazon-seller-forums-news-content": {
                    "status": "verified",
                    "source_layer": "official-content",
                },
                "tiktok-shop-newsroom-content": {
                    "status": "broken",
                    "source_layer": "official-content",
                },
            },
        }
        (data_dir / "source_status.json").write_text(json.dumps(source_status, ensure_ascii=False, indent=2), encoding="utf-8")

        original_runtime = os.environ.get("CROSSBORDER_RADAR_RUNTIME_DIR")
        os.environ["CROSSBORDER_RADAR_RUNTIME_DIR"] = str(runtime_root)
        try:
            module = load_module()
            brief = {
                "overview": {
                    "headline": "通用雷达先盯 policy：File SAFE-T claims with these 7 tips",
                    "top_risk": {"event_title": "File SAFE-T claims with these 7 tips"},
                },
                "fulfillment_actions": [
                    {
                        "actions": [
                            "紧盯 File SAFE-T claims with these 7 tips 的正式细则和执行时间",
                        ]
                    }
                ],
                "events": [
                    {
                        "event_title": "File SAFE-T claims with these 7 tips",
                        "event_summary": "English summary for forum event",
                        "event_type": "policy",
                        "source_id": "amazon-seller-forums-news-content",
                        "source_layer": "official-content",
                        "source_label": "Amazon Seller Forums - News and Announcements Content",
                        "source_display_zh": "Amazon 卖家论坛公告更新",
                        "raw_event_title": "File SAFE-T claims with these 7 tips",
                    },
                    {
                        "event_title": "TikTok seller update changes fulfillment checks",
                        "event_summary": "English summary for tiktok update",
                        "event_type": "policy",
                        "source_id": "tiktok-shop-newsroom-content",
                        "source_layer": "official-content",
                        "source_label": "TikTok Shop Newsroom / Seller Updates Content",
                        "source_display_zh": "TikTok Shop 卖家规则更新",
                        "raw_event_title": "TikTok seller update changes fulfillment checks",
                    },
                ],
            }
            prepared = module.prepare_brief_for_publish(brief)
        finally:
            if original_runtime is None:
                os.environ.pop("CROSSBORDER_RADAR_RUNTIME_DIR", None)
            else:
                os.environ["CROSSBORDER_RADAR_RUNTIME_DIR"] = original_runtime

    events = prepared.get("events", [])
    if len(events) != 1:
        errors.append(f"expected only verified official-content events to remain, got {len(events)}")
    else:
        title = events[0].get("event_title")
        summary = events[0].get("event_summary")
        if title != "Amazon 发布 SAFE-T 索赔提交流程与要点":
            errors.append(f"expected official-content title to be synthesized into an actionable chinese title, got {title!r}")
        if "这条政策变化可能影响税费、清关或平台经营规则" not in summary:
            errors.append("expected official-content summary to be localized before publish")

    headline = prepared.get("overview", {}).get("headline", "")
    if "Amazon 发布 SAFE-T 索赔提交流程与要点" not in headline:
        errors.append("expected overview headline to be rewritten with published chinese title")
    if "File SAFE-T claims with these 7 tips" in json.dumps(prepared, ensure_ascii=False):
        errors.append("expected published brief to stop leaking raw english title after replacement")

    if errors:
        print("FAIL validate_publish_guard")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_publish_guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
