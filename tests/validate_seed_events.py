#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SEED_FILE = SKILL_ROOT / "scripts" / "seed_events.json"
EXAMPLES_DIR = SKILL_ROOT / "examples"


def main() -> int:
    seeds = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    errors = []

    if len(seeds) < 3:
        errors.append("expected at least 3 seed events")

    seen_ids = set()
    for seed in seeds:
        if not seed.get("id"):
            errors.append("seed missing id")
            continue
        if seed["id"] in seen_ids:
            errors.append(f"duplicate seed id: {seed['id']}")
        seen_ids.add(seed["id"])

        example_file = seed.get("example_file")
        if not example_file:
            errors.append(f"seed {seed['id']} missing example_file")
            continue
        if not (EXAMPLES_DIR / example_file).exists():
            errors.append(f"seed {seed['id']} example file not found: {example_file}")

    if errors:
        print("FAIL validate_seed_events")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_seed_events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
