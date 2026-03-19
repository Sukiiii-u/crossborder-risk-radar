#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "network_config.py"

spec = importlib.util.spec_from_file_location("network_config", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main() -> int:
    errors: list[str] = []
    config = module.load_network_config()
    proxies = module.proxy_mapping(config)

    if not config.get("http_proxy"):
        errors.append("fetch_network.json should define http_proxy")
    if not config.get("https_proxy"):
        errors.append("fetch_network.json should define https_proxy")
    if proxies.get("http") != config.get("http_proxy"):
        errors.append("http proxy mapping mismatch")
    if proxies.get("https") != config.get("https_proxy"):
        errors.append("https proxy mapping mismatch")

    if errors:
        print("FAIL validate_fetch_network_config")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_fetch_network_config")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
