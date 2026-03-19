#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "analyze_event.py"

spec = importlib.util.spec_from_file_location("analyze_event", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def assert_true(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors = []

    region = module.detect_region(
        "European Commission updates sustainability rules for imported packaging and customs clearance workflows."
    )
    assert_true(region == "EU", f"expected EU region, got {region}", errors)

    keep, reason, confidence = module.classify_relevance(
        "Trade Information Notice: New Carnet Data Elements for ACE Portal trade users and manifest transmission updates."
    )
    assert_true(keep is False, "ACE/carnet maintenance notice should not be relevant", errors)
    assert_true("maintenance" in reason.lower() or "seller-operational" in reason.lower(), "maintenance notice reason should explain low seller relevance", errors)
    assert_true(confidence == "low", "maintenance notice confidence should stay low", errors)

    keep, reason, confidence = module.classify_relevance(
        "EU de minimis parcel fee change may raise tax cost and pricing pressure for cross-border sellers."
    )
    assert_true(keep is True, "EU de minimis parcel fee should remain relevant", errors)
    assert_true(confidence in {"medium", "low"}, "relevant tariff notice should retain operational confidence", errors)

    keep, reason, confidence = module.classify_relevance(
        "FedEx introduces reusable shipping boxes for B2B shipments to improve handling efficiency between facilities."
    )
    assert_true(keep is False, "corporate reusable packaging story should not be treated as seller-relevant radar signal", errors)
    assert_true("packaging" in reason.lower() or "enterprise" in reason.lower(), "corporate packaging rejection should explain why it is not seller-operational", errors)

    keep, reason, confidence = module.classify_relevance(
        "Sellers say Amazon charged ad fees throughout Thursday's outage, raising cost and checkout risk for marketplace merchants."
    )
    assert_true(keep is True, "seller fee outage should remain relevant", errors)

    keep, reason, confidence = module.classify_relevance(
        "Congress wants to put driverless 80,000-pound heavy-duty trucks on the road for small carriers."
    )
    assert_true(keep is False, "heavy-duty trucking headline should not match tariff duty keywords by substring", errors)

    if errors:
        print("FAIL validate_analyze_event")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_analyze_event")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
