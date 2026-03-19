#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "fetch_policy_watch.py"
OUTPUT = SKILL_ROOT / "runtime" / "data" / "policy_watch.json"


def main() -> int:
    errors: list[str] = []
    original_output = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        eu = tmp / "eu.html"
        cbp = tmp / "cbp.html"
        cfg = tmp / "policy_watch_sources.json"
        eu.write_text(
            """
            <html><head>
            <title>E-commerce: the 150 EUR customs duty exemption threshold to be removed in 2028</title>
            <meta name="description" content="The 150 EUR customs duty exemption threshold will be removed for e-commerce parcels." />
            </head><body><time>2026-03-01</time>parcel customs duty exemption 150 EUR e-commerce</body></html>
            """,
            encoding="utf-8",
        )
        cbp.write_text(
            """
            <html><head>
            <title>CBP proposes new data requirements for low-value shipments</title>
            <meta property="og:description" content="Section 321 and Entry Type 86 shipments face new data requirements." />
            </head><body><div>Release Date</div><div>Mar 01, 2026</div>section 321 entry type 86 de minimis low-value shipments</body></html>
            """,
            encoding="utf-8",
        )
        cfg.write_text(
            json.dumps(
                [
                    {
                        "id": "eu-test",
                        "title": "EU test",
                        "url": eu.resolve().as_uri(),
                        "source_name": "European Commission",
                        "source_type": "regulator-official",
                        "platforms": ["TikTok"],
                        "regions": ["EU"],
                        "event_type": "tariff",
                        "risk_level": "high",
                        "max_age_days": 365,
                        "match_any_keywords": ["150 eur", "customs duty"],
                        "action": "复核欧盟税费"
                    },
                    {
                        "id": "cbp-test",
                        "title": "CBP test",
                        "url": cbp.resolve().as_uri(),
                        "source_name": "CBP",
                        "source_type": "regulator-official",
                        "platforms": ["TikTok"],
                        "regions": ["US"],
                        "event_type": "customs",
                        "risk_level": "high",
                        "max_age_days": 365,
                        "match_any_keywords": ["section 321", "entry type 86"],
                        "action": "复核美国清关资料"
                    }
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        env = dict(**os.environ, POLICY_WATCH_CONFIG_FILE=str(cfg))
        proc = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False, env=env)
        stream = proc.stdout if proc.stdout.strip() else proc.stderr
        try:
            payload = json.loads(stream)
        except json.JSONDecodeError as exc:
            print("FAIL validate_fetch_policy_watch")
            print(f"- invalid json output: {exc}")
            return 1

        if payload.get("item_count") != 2:
            errors.append(f"expected 2 policy watch items, got {payload.get('item_count')}")
        if not isinstance(payload.get("items"), list):
            errors.append("output should include items list")
        if not OUTPUT.exists():
            errors.append("fetch_policy_watch should write runtime/data/policy_watch.json")
        else:
            stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
            if len(stored.get("items", [])) != 2:
                errors.append("policy_watch.json should persist both policy items")

        previous_payload = {"generated_at": "2026-03-13T00:00:00Z", "item_count": 1, "items": [{"id": "existing-policy"}], "failures": []}
        OUTPUT.write_text(json.dumps(previous_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        broken_cfg = tmp / "policy_watch_broken.json"
        broken_cfg.write_text(
            json.dumps(
                [
                    {
                        "id": "broken",
                        "title": "Broken",
                        "url": "https://127.0.0.1.invalid.example/policy",
                        "source_name": "Broken Source",
                        "source_type": "regulator-official",
                        "platforms": ["TikTok"],
                        "regions": ["EU"],
                        "event_type": "tariff",
                        "risk_level": "high",
                        "max_age_days": 365,
                        "match_any_keywords": ["parcel"],
                        "action": "noop"
                    }
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        broken_env = dict(**os.environ, POLICY_WATCH_CONFIG_FILE=str(broken_cfg))
        broken_proc = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False, env=broken_env)
        broken_stream = broken_proc.stdout if broken_proc.stdout.strip() else broken_proc.stderr
        broken_payload = json.loads(broken_stream)
        if not broken_payload.get("preserved_previous_snapshot"):
            errors.append("policy watch should preserve previous snapshot when all sources fail")
        preserved = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if preserved.get("items", [{}])[0].get("id") != "existing-policy":
            errors.append("policy watch should not overwrite previous snapshot on total failure")

    if original_output is None:
        OUTPUT.unlink(missing_ok=True)
    else:
        OUTPUT.write_text(original_output, encoding="utf-8")

    if errors:
        print("FAIL validate_fetch_policy_watch")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_fetch_policy_watch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
