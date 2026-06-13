#!/usr/bin/env python3
"""Generate replay runtime profiles with fresh identifier fields."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from headlessba.modules.runtime.runtime_profile_generator import (  # noqa: E402
    generate_android_runtime_profile,
)
from headlessba.modules.runtime.android_mobile_profile import (  # noqa: E402
    generate_android_mobile_profile,
    save_android_mobile_profile,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Android replay profile inputs for main.py.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers(dest="kind", required=True)

    android = sub.add_parser("android", help="Generate an Android runtime pull directory")
    android.add_argument("--out", type=Path, required=True, help="Output directory consumed by main.py --android-runtime-dir")
    android.add_argument("--seed", default="", help="Optional deterministic seed")
    android.add_argument("--base-android-runtime-dir", type=Path, default=None, help="Base runtime pull; defaults to latest pull")
    android.add_argument("--region", default="", help="Override region; defaults to base profile")
    android.add_argument("--country", default="", help="Override country; defaults to base profile")
    android.add_argument("--locale", default="", help="Override locale; defaults to base profile")
    android.add_argument("--client-version", default="", help="Override client version; defaults to base profile")
    android.add_argument("--app-version-code", type=int, default=None, help="Override app version code; defaults to base profile")
    android.add_argument("--device-model", default="", help="Override Android device model; defaults to base profile")
    android.add_argument("--android-os-version", default="", help="Override Android OS version; defaults to base profile")
    android.add_argument("--density", default="", help="Override UA density; defaults to base profile UA")
    android.add_argument("--resolution", default="", help="Override UA resolution; defaults to base profile UA")
    android.add_argument("--service-id", default="2079")
    android.add_argument("--client-id", default="", help="Override TOYSDK client id; defaults to base profile")
    android.add_argument("--package-name", default="", help="Override package name; defaults to base profile")
    android.add_argument("--language", default="", help="Override game option language; defaults to base profile")
    android.add_argument("--voice-language", default="", help="Override voice language; defaults to base profile")

    mobile = sub.add_parser("android-mobile", help="Generate a persistent synthetic Android mobile profile JSON")
    mobile.add_argument("--out", type=Path, required=True, help="Output JSON path")
    mobile.add_argument("--seed", default="", help="Optional deterministic seed")
    mobile.add_argument("--country", default="TW")
    mobile.add_argument("--locale", default="zh-TW")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.kind == "android":
        result = generate_android_runtime_profile(
            args.out,
            seed=args.seed,
            base_runtime_dir=args.base_android_runtime_dir,
            region=args.region,
            country=args.country,
            locale=args.locale,
            client_version=args.client_version,
            app_version_code=args.app_version_code,
            device_model=args.device_model,
            android_os_version=args.android_os_version,
            density=args.density,
            resolution=args.resolution,
            service_id=args.service_id,
            client_id=args.client_id,
            package_name=args.package_name,
            language=args.language,
            voice_language=args.voice_language,
        )
    elif args.kind == "android-mobile":
        profile = generate_android_mobile_profile(seed=args.seed, country=args.country, locale=args.locale)
        save_android_mobile_profile(args.out, profile)
        print(json.dumps({"kind": "android-mobile", "path": str(Path(args.out).expanduser().resolve()), "summary": profile.to_dict()}, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
