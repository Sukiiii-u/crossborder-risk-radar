#!/usr/bin/env python3
import email.utils
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
MORNING_BRIEF = SCRIPTS_DIR / "morning_brief.py"
TODAY_RADAR = SCRIPTS_DIR / "today_radar.py"
RUN_RADAR = SCRIPTS_DIR / "run_radar.py"


def _iso(dt: datetime) -> str:
    """将 datetime 格式化为 ISO 8601 字符串。"""
    return dt.isoformat()


def _rfc2822(dt: datetime) -> str:
    """将 datetime 格式化为 RFC 2822 字符串（published_at 使用的格式）。"""
    return email.utils.format_datetime(dt)


def _build_real_payload() -> dict:
    """动态生成测试 fixture，时间戳基于当前时间，确保 inspect_real_events_snapshot 判定为 fresh。"""
    now = datetime.now(timezone.utc)
    base = now - timedelta(hours=1)

    return {
        "generated_at": _iso(base),
        "event_count": 3,
        "events": [
            {
                "source_id": "reuters",
                "source_label": "Reuters",
                "source_topic": "tariff",
                "title": "EU weighs low-value parcel fee for imported packages",
                "zh_title": "欧盟拟评估进口低货值包裹附加费用",
                "zh_summary": "欧盟正在评估低货值包裹附加费用，直邮卖家的税后到手价和毛利都会承压。",
                "content": "EU officials are weighing a low-value parcel fee and tariff changes that could raise landed costs for direct-mail cross-border sellers shipping into the European Union.",
                "url": "https://example.com/reuters-eu-parcel-fee",
                "published_at": _rfc2822(base),
                "fetched_at": _iso(base + timedelta(seconds=1)),
            },
            {
                "source_id": "freightwaves",
                "source_label": "FreightWaves",
                "source_topic": "logistics",
                "title": "Northern Europe congestion delays seller replenishment",
                "zh_title": "北欧拥堵拖慢卖家补货节奏",
                "zh_summary": "北欧港口拥堵正在推迟补货和交付，卖家的库存与时效风险上升。",
                "content": "Port congestion across Northern Europe is delaying replenishment and raising delivery-time risk for cross-border sellers relying on imported inventory.",
                "url": "https://example.com/freightwaves-congestion",
                "published_at": _rfc2822(base + timedelta(minutes=30)),
                "fetched_at": _iso(base + timedelta(minutes=30, seconds=1)),
            },
            {
                "source_id": "commission",
                "source_label": "European Commission",
                "source_topic": "environment",
                "title": "EU packaging compliance timeline moves forward",
                "zh_title": "欧盟包装合规时间线继续推进",
                "zh_summary": "欧盟包装合规推进后，材料、标签与包装成本都需要重新核查。",
                "content": "European Commission officials advanced packaging compliance timelines that may raise packaging and materials costs for sellers shipping consumer goods into the EU.",
                "url": "https://example.com/eu-packaging-timeline",
                "published_at": _rfc2822(base + timedelta(hours=1)),
                "fetched_at": _iso(base + timedelta(hours=1, seconds=1)),
            },
            {
                "source_id": "amazon-seller-forums-news-content",
                "source_label": "Amazon Seller Forums - News and Announcements Content",
                "source_topic": "policy",
                "source_platforms": ["Amazon"],
                "source_trust_tier": "platform-official",
                "source_seller_signal_bias": "high",
                "source_priority": "P0",
                "source_type": "platform-official",
                "source_layer": "official-content",
                "source_display_zh": "Amazon 卖家论坛公告更新",
                "title": "Update to seller-fulfilled refund process by January 26, 2026",
                "zh_title": "Amazon 调整卖家自发货退款处理流程",
                "zh_summary": "Amazon 调整卖家自发货退款处理时限和自动退款触发规则，卖家需要重新评估售后与退款响应流程。",
                "content": "Effective January 26, 2026, the Fulfilled by Merchant refund process will be updated to improve your return management experience and give you more time to assess returns.",
                "url": "https://example.com/amazon-fbm-refund-update",
                "published_at": _rfc2822(base + timedelta(hours=1, minutes=10)),
                "fetched_at": _iso(base + timedelta(hours=1, minutes=10, seconds=1)),
            },
            {
                "source_id": "generic-b2b",
                "source_label": "B2B Enterprise News",
                "source_topic": "logistics",
                "title": "How Costco and B2B importers are rethinking oil-driven delivery costs",
                "content": "Costco and other enterprise B2B importers are rethinking oil-driven delivery costs and quarterly planning amid global shipping volatility.",
                "url": "https://example.com/b2b-oil-costco",
                "published_at": _rfc2822(base + timedelta(hours=1, minutes=30)),
                "fetched_at": _iso(base + timedelta(hours=1, minutes=30, seconds=1)),
            },
            {
                "source_id": "independent-site-regulators-cbp-ecommerce",
                "source_label": "CBP Newsroom",
                "source_topic": "policy",
                "title": "Bogus watches intercepted by CBP officers in Cincinnati",
                "content": "CBP officers seized counterfeit watches in an enforcement action at the airport.",
                "url": "https://example.com/cbp-counterfeit-watches",
                "published_at": _rfc2822(base + timedelta(hours=1, minutes=40)),
                "fetched_at": _iso(base + timedelta(hours=1, minutes=40, seconds=1)),
            },
            {
                "source_id": "freightwaves",
                "source_label": "FreightWaves",
                "source_topic": "logistics",
                "title": "Descartes reports record quarter; announces acquisition",
                "content": "The logistics software company reported record quarter results and announced an acquisition with investor commentary.",
                "url": "https://example.com/descartes-record-quarter",
                "published_at": _rfc2822(base + timedelta(hours=1, minutes=45)),
                "fetched_at": _iso(base + timedelta(hours=1, minutes=45, seconds=1)),
            },
        ],
        "failures": [],
    }


EMPTY_REAL_PAYLOAD = {
    "generated_at": "2026-03-12T06:00:00+00:00",
    "event_count": 0,
    "events": [],
    "failures": []
}


def run_cmd(script: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=False, env=env)


def run_json(script: Path, *args: str, env: dict | None = None) -> dict:
    proc = run_cmd(script, *args, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout)


def run_human(script: Path, *args: str, env: dict | None = None) -> str:
    proc = run_cmd(script, *args, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout


def assert_true(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def looks_like_chinese(value: str | None) -> bool:
    text = str(value or "")
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def validate_real_chain_preferred(errors: list[str], real_events_file: Path, env: dict[str, str]) -> None:
    real_events_file.write_text(json.dumps(_build_real_payload(), ensure_ascii=False, indent=2), encoding="utf-8")

    brief = run_json(MORNING_BRIEF, "tiktok-direct-mail", env=env)
    today_auto = run_json(TODAY_RADAR, "tiktok", "--json", env=env)
    scheduled_auto = run_json(RUN_RADAR, "tiktok", "--format", "json", env=env)
    human_auto = run_human(TODAY_RADAR, "tiktok", env=env)

    for label, payload in {
        "morning_brief": brief,
        "today_radar": today_auto,
        "run_radar": scheduled_auto,
    }.items():
        assert_true(payload.get("event_count", 0) >= 3, f"{label}: expected at least 3 ranked real events, got {payload.get('event_count')}", errors)
        assert_true("最新抓取快照" in payload.get("overall_takeaway", ""), f"{label}: should explicitly prefer latest snapshot", errors)
        top = (payload.get("events") or [{}])[0]
        assert_true(top.get("brief_source_mode") == "real", f"{label}: top event should come from real chain", errors)
        assert_true(looks_like_chinese(top.get("event_title")), f"{label}: top event should render in chinese", errors)
        assert_true(
            top.get("source_label") in {
                "Reuters",
                "Amazon Seller Forums - News and Announcements Content",
                "Amazon Seller News / Announcements Content",
            },
            f"{label}: top event should preserve a high-value source label",
            errors,
        )
        titles = [event.get("event_title") for event in payload.get("events", [])]
        assert_true(
            any(title in titles[:2] for title in ["Amazon 发布 SAFE-T 索赔提交流程与要点", "Amazon 调整卖家自发货退款处理流程"]),
            f"{label}: top two should include actionable official seller-policy events",
            errors,
        )
        assert_true("Amazon 调整卖家自发货退款处理流程" in titles[:2], f"{label}: verified official-content policy should rank ahead of media logistics noise", errors)
        assert_true(
            not any(event.get("event_title") == "How Costco and B2B importers are rethinking oil-driven delivery costs" for event in payload.get("events", [])),
            f"{label}: macro B2B corporate story should be pushed out of top radar events",
            errors,
        )
        assert_true(
            not any(event.get("event_title") == "Bogus watches intercepted by CBP officers in Cincinnati" for event in payload.get("events", [])),
            f"{label}: enforcement seizure story should be pushed out of top radar events",
            errors,
        )
        assert_true(
            not any(event.get("event_title") == "Descartes reports record quarter; announces acquisition" for event in payload.get("events", [])),
            f"{label}: enterprise earnings story should be pushed out of top radar events",
            errors,
        )

    assert_true("## 重点事件" in human_auto, "today_radar human output missing key section", errors)
    assert_true("## 今日先做" in human_auto, "today_radar human output missing action section", errors)
    assert_true("欧盟拟评估进口低货值包裹附加费用" in human_auto, "today_radar human output should show localized real event title", errors)
    assert_true("来源：Reuters" in human_auto, "today_radar human output should preserve real source label instead of generic placeholder", errors)
    assert_true("ranking_reason" not in human_auto and '"event_count"' not in human_auto, "today_radar human output should read like a report, not raw JSON", errors)


def validate_fallback_still_works(errors: list[str], real_events_file: Path, env: dict[str, str]) -> None:
    real_events_file.write_text(json.dumps(EMPTY_REAL_PAYLOAD, ensure_ascii=False, indent=2), encoding="utf-8")

    brief = run_json(MORNING_BRIEF, "amazon-fba", env=env)
    today_auto = run_json(TODAY_RADAR, "amazon", "--json", env=env)
    scheduled_seed = run_json(RUN_RADAR, "amazon", "--source", "seed", "--format", "json", env=env)

    for label, payload in {
        "morning_brief_fallback": brief,
        "today_radar_fallback": today_auto,
        "run_radar_seed": scheduled_seed,
    }.items():
        assert_true(payload.get("event_count", 0) >= 3, f"{label}: fallback should still return a useful radar", errors)
        events = payload.get("events") or []
        assert_true(bool(events), f"{label}: fallback should include ranked events", errors)
        assert_true(all(event.get("brief_source_mode") == "seed" for event in events), f"{label}: fallback should come from seed chain", errors)
        assert_true("最新抓取快照" not in payload.get("overall_takeaway", ""), f"{label}: fallback copy should not pretend it used real events", errors)


def validate_profile_and_fulfillment_differences(errors: list[str], real_events_file: Path, env: dict[str, str]) -> None:
    real_events_file.write_text(json.dumps(EMPTY_REAL_PAYLOAD, ensure_ascii=False, indent=2), encoding="utf-8")

    amazon = run_json(TODAY_RADAR, "amazon", "--json", env=env)
    tiktok = run_json(TODAY_RADAR, "tiktok", "--json", env=env)
    indie = run_json(TODAY_RADAR, "independent-site", "--json", env=env)

    assert_true(amazon.get("overall_takeaway") != tiktok.get("overall_takeaway"), "amazon vs tiktok should not share same takeaway", errors)
    assert_true(tiktok.get("overall_takeaway") != indie.get("overall_takeaway"), "tiktok vs indie should not share same takeaway", errors)
    assert_true(amazon.get("today_actions") != tiktok.get("today_actions"), "amazon vs tiktok should not share same priority actions", errors)
    assert_true(tiktok.get("today_actions") != indie.get("today_actions"), "tiktok vs indie should not share same priority actions", errors)
    assert_true(amazon.get("profile_focus") != tiktok.get("profile_focus"), "amazon vs tiktok should not share same profile focus", errors)
    assert_true("毛利" in tiktok.get("profile_focus", ""), "tiktok profile should emphasize margin sensitivity", errors)
    assert_true("到手价" in indie.get("profile_focus", ""), "independent-site profile should emphasize landed price experience", errors)


def validate_human_readability(errors: list[str], real_events_file: Path, env: dict[str, str]) -> None:
    real_events_file.write_text(json.dumps(EMPTY_REAL_PAYLOAD, ensure_ascii=False, indent=2), encoding="utf-8")

    human = run_human(RUN_RADAR, "tiktok", "--source", "seed", env=env)
    expected_sections = [
        "# 今日跨境风险晨报",
        "履约主视角：",
        "平台修正：",
        "展示标签：",
        "一句话结论：",
        "画像提醒：",
        "头号信号：",
        "## 重点事件",
        "## 优先级解释",
        "## 今日先做",
        "## 继续观察",
        "## 暂缓动作",
        "## 一句话结论",
        "- 适用性分层：",
        "  - 高相关是谁：",
        "  - 中相关是谁：",
        "  - 低相关/观察是谁：",
        "- 各层该做什么：",
        "  - 高相关：",
        "  - 中相关：",
        "  - 低相关/观察：",
    ]
    for section in expected_sections:
        assert_true(section in human, f"human radar missing section: {section}", errors)

    assert_true("{\n" not in human, "human radar should not render as raw JSON block", errors)
    assert_true("impact_dimensions" not in human, "human radar should not leak schema field names", errors)
    assert_true("seller_angle" in human or "对你这种" in human, "human radar should include operator-facing language", errors)


def main() -> int:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as runtime_tmp:
        runtime_root = Path(runtime_tmp)
        real_events_file = runtime_root / "data" / "real_events.json"
        real_events_file.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, CROSSBORDER_RADAR_RUNTIME_DIR=str(runtime_root))

        validate_real_chain_preferred(errors, real_events_file, env)
        validate_fallback_still_works(errors, real_events_file, env)
        validate_profile_and_fulfillment_differences(errors, real_events_file, env)
        validate_human_readability(errors, real_events_file, env)

    if errors:
        print("FAIL validate_product_acceptance")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_product_acceptance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
