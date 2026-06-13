#!/usr/bin/env python3
"""Compare two BA login artifact sets and report whether they converge in-game."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.auth.equivalence import compare_login_artifact_sources, load_login_artifact_source, write_report


DEFAULT_OUTPUT = ROOT / "analysis_reports" / "login_equivalence" / "report.json"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two BA login artifact directories/JSON files and check whether they converge at the main-game surface.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("left", help="Left artifact directory or toy_login_summary.json path")
    parser.add_argument("right", help="Right artifact directory or toy_login_summary.json path")
    parser.add_argument("--left-label", default="", help="Optional label for the left source")
    parser.add_argument("--right-label", default="", help="Optional label for the right source")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Write JSON report here")
    parser.add_argument(
        "--strict-token-values",
        action="store_true",
        help="Compare exact token strings instead of token kind/presence/length only",
    )
    parser.add_argument(
        "--strict-environment",
        action="store_true",
        help="Treat device identifiers and ad-id/idfv values as strict equality fields",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    left = load_login_artifact_source(args.left, label=args.left_label)
    right = load_login_artifact_source(args.right, label=args.right_label)
    report = compare_login_artifact_sources(
        left,
        right,
        strict_token_values=args.strict_token_values,
        strict_environment=args.strict_environment,
    )
    write_report(args.output, report)
    print_summary(report, output_path=args.output)
    return 0


def print_summary(report: dict, *, output_path: Path) -> None:
    summary = report["summary"]
    print(f"[*] report: {output_path}")
    print(f"[*] same_account_identity: {summary['same_account_identity']}")
    print(f"[*] pre_game_token_surface_match: {summary['pre_game_token_surface_match']}")
    print(f"[*] derived_credentials_match: {summary['derived_credentials_match']}")
    print(f"[*] game_request_core_match: {summary['game_request_core_match']}")
    print(f"[*] game_response_core_match: {summary['game_response_core_match']}")
    print(f"[*] game_surface_core_match: {summary['game_surface_core_match']}")
    print(f"[*] converges_in_game: {summary['converges_in_game']}")


if __name__ == "__main__":
    raise SystemExit(main())
