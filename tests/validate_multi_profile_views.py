#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
BRIEF_SCRIPT = SKILL_ROOT / "scripts" / "morning_brief.py"
RADAR_SCRIPT = SKILL_ROOT / "scripts" / "today_radar.py"
def run_cmd(script: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=False, env=env)


def main() -> int:
    with tempfile.TemporaryDirectory() as runtime_tmp:
        runtime_root = Path(runtime_tmp)
        real_events = runtime_root / "data" / "real_events.json"
        real_events.parent.mkdir(parents=True, exist_ok=True)
        real_events.write_text(
            json.dumps({"generated_at": "test", "event_count": 0, "events": [], "failures": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        env = dict(os.environ, CROSSBORDER_RADAR_RUNTIME_DIR=str(runtime_root))
        brief = run_cmd(BRIEF_SCRIPT, json.dumps(["amazon-fba", "tiktok-direct-mail"], ensure_ascii=False), env=env)
        human = run_cmd(BRIEF_SCRIPT, json.dumps(["amazon-fba", "tiktok-direct-mail"], ensure_ascii=False), "--human", env=env)
        radar = run_cmd(RADAR_SCRIPT, "--preset", "amazon", "--preset", "tiktok", "--seed-only", "--json", env=env)

    errors = []

    if brief.returncode != 0:
        errors.append(f"brief json command failed: {brief.stderr.strip() or brief.stdout.strip()}")
        data = {}
    else:
        data = json.loads(brief.stdout)
        if data.get("brief_type") != "morning_radar_multi_view":
            errors.append("multi profile input should return morning_radar_multi_view")
        if data.get("view_count") != 2:
            errors.append("expected exactly 2 views")
        if len(data.get("views", [])) != 2:
            errors.append("views length mismatch")
        else:
            first, second = data["views"]
            if first.get("profile_preset") != "amazon-fba":
                errors.append("first view should stay amazon-fba")
            if second.get("profile_preset") != "tiktok-direct-mail":
                errors.append("second view should stay tiktok-direct-mail")
            if first.get("profile_label") == second.get("profile_label"):
                errors.append("views should keep separate labels")
            if first.get("overall_takeaway") == second.get("overall_takeaway"):
                errors.append("views should keep separate takeaways instead of being overwritten")
            if first.get("today_actions", [None])[0] == second.get("today_actions", [None])[0]:
                errors.append("views should keep separate priority actions")

    if human.returncode != 0:
        errors.append(f"brief human command failed: {human.stderr.strip() or human.stdout.strip()}")
    else:
        output = human.stdout
        if "## 多画像视角总览" not in output:
            errors.append("human output missing multi-view summary heading")
        if "## 画像视角 1｜本地履约-平台主导（平台修正：Amazon / 市场：德国站）" not in output:
            errors.append("human output missing first fulfillment-first view heading")
        if "## 画像视角 2｜跨境直发（平台修正：TikTok Shop / 市场：欧盟低客单）" not in output:
            errors.append("human output missing second fulfillment-first view heading")
        first_summary = output.find("## 多画像视角总览")
        first_view = output.find("## 画像视角 1｜本地履约-平台主导（平台修正：Amazon / 市场：德国站）")
        second_view = output.find("## 画像视角 2｜跨境直发（平台修正：TikTok Shop / 市场：欧盟低客单）")
        if min(first_summary, first_view, second_view) == -1 or not (first_summary < first_view < second_view):
            errors.append("multi-view sections should render in summary -> view1 -> view2 order")
        if output.count("### 总览判断") < 2 or output.count("### 分履约动作") < 2:
            errors.append("each view should keep its own layered sections")

    if radar.returncode != 0:
        errors.append(f"today_radar multi preset command failed: {radar.stderr.strip() or radar.stdout.strip()}")
    else:
        radar_data = json.loads(radar.stdout)
        if radar_data.get("brief_type") != "morning_radar_multi_view":
            errors.append("today_radar repeated --preset should return multi-view brief")
        if [view.get("profile_preset") for view in radar_data.get("views", [])] != ["amazon-fba", "tiktok-direct-mail"]:
            errors.append("today_radar should preserve each preset as its own view")

    if errors:
        print("FAIL validate_multi_profile_views")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_multi_profile_views")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
