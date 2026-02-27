#!/usr/bin/env python3
"""Terraforming Mars gameplay learning dataset helper.

Commands:
- init-summary: create a new summary JSON from template
- append: validate and append one summary to JSONL dataset, then regenerate rollup
- rollup: regenerate rollup from existing dataset
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

DATASET_DEFAULT = Path("agent-prompts/codex_from_gameplay/game-learning-dataset.jsonl")
ROLLUP_DEFAULT = Path("agent-prompts/codex_from_gameplay/game-learning-rollup.md")
SUMMARY_TEMPLATE_DEFAULT = Path("agent-prompts/codex_from_gameplay/game-summary-template.json")

CATEGORIES = ("tr", "milestones", "awards", "greenery", "city", "card_vp")
STRATEGIES = {"rush", "hybrid", "engine"}
CONFIDENCE = {"low", "med", "high"}


class ValidationError(ValueError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValidationError(f"Expected JSON object in {path}")
    return data


def _read_dataset(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"Invalid JSONL at {path}:{lineno}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValidationError(f"Expected object at {path}:{lineno}")
            records.append(row)
    return records


def _write_dataset(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=True, sort_keys=True) + "\n")


def _infer_game_id(game_url: str) -> str:
    parsed = urlparse(game_url)
    query = parse_qs(parsed.query)
    if "id" in query and query["id"]:
        return query["id"][0]
    # Fallback to path tail if there is no query id.
    tail = parsed.path.rstrip("/").split("/")[-1]
    return tail or "unknown"


def _require(record: dict[str, Any], key: str) -> Any:
    if key not in record:
        raise ValidationError(f"Missing required key: {key}")
    return record[key]


def _validate_int(value: Any, label: str) -> int:
    if not isinstance(value, int):
        raise ValidationError(f"{label} must be an int")
    return value


def _validate_record(record: dict[str, Any]) -> None:
    for key in (
        "game_date",
        "game_url",
        "game_id",
        "planned_strategy",
        "finish_generation",
        "score",
        "breakdown",
        "mistake_tags",
        "rule_updates",
        "counterfactuals",
    ):
        _require(record, key)

    if not isinstance(record["game_date"], str) or not record["game_date"]:
        raise ValidationError("game_date must be a non-empty string")
    if not isinstance(record["game_url"], str) or not record["game_url"]:
        raise ValidationError("game_url must be a non-empty string")
    if not isinstance(record["game_id"], str) or not record["game_id"]:
        raise ValidationError("game_id must be a non-empty string")

    strategy = record["planned_strategy"]
    if strategy not in STRATEGIES:
        raise ValidationError(f"planned_strategy must be one of {sorted(STRATEGIES)}")

    finish_generation = _validate_int(record["finish_generation"], "finish_generation")
    if finish_generation < 1 or finish_generation > 20:
        raise ValidationError("finish_generation must be between 1 and 20")

    pivot_generation = record.get("pivot_generation", 0)
    _validate_int(pivot_generation, "pivot_generation")

    score = record["score"]
    if not isinstance(score, dict):
        raise ValidationError("score must be an object")
    self_score = _validate_int(_require(score, "self"), "score.self")
    opp_score = _validate_int(_require(score, "opponent"), "score.opponent")

    breakdown = record["breakdown"]
    if not isinstance(breakdown, dict):
        raise ValidationError("breakdown must be an object")

    for side in ("self", "opponent"):
        side_breakdown = _require(breakdown, side)
        if not isinstance(side_breakdown, dict):
            raise ValidationError(f"breakdown.{side} must be an object")
        for cat in CATEGORIES:
            _validate_int(_require(side_breakdown, cat), f"breakdown.{side}.{cat}")

    self_total = sum(breakdown["self"][cat] for cat in CATEGORIES)
    opp_total = sum(breakdown["opponent"][cat] for cat in CATEGORIES)
    if self_total != self_score:
        raise ValidationError(
            f"score.self ({self_score}) does not match breakdown.self sum ({self_total})"
        )
    if opp_total != opp_score:
        raise ValidationError(
            f"score.opponent ({opp_score}) does not match breakdown.opponent sum ({opp_total})"
        )

    mistake_tags = record["mistake_tags"]
    if not isinstance(mistake_tags, list) or not all(isinstance(x, str) and x for x in mistake_tags):
        raise ValidationError("mistake_tags must be a list of non-empty strings")

    rule_updates = record["rule_updates"]
    if not isinstance(rule_updates, list) or not all(isinstance(x, str) and x for x in rule_updates):
        raise ValidationError("rule_updates must be a list of non-empty strings")

    counterfactuals = record["counterfactuals"]
    if not isinstance(counterfactuals, list):
        raise ValidationError("counterfactuals must be a list")
    for idx, cf in enumerate(counterfactuals):
        if not isinstance(cf, dict):
            raise ValidationError(f"counterfactuals[{idx}] must be an object")
        if not isinstance(cf.get("change"), str) or not cf["change"]:
            raise ValidationError(f"counterfactuals[{idx}].change must be non-empty string")
        _validate_int(cf.get("swing_vp_est"), f"counterfactuals[{idx}].swing_vp_est")
        confidence = cf.get("confidence", "med")
        if confidence not in CONFIDENCE:
            raise ValidationError(f"counterfactuals[{idx}].confidence must be in {sorted(CONFIDENCE)}")


def _build_rollup(records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Game Learning Rollup")
    lines.append("")

    if not records:
        lines.append("No records in dataset yet.")
        lines.append("")
        return "\n".join(lines)

    records_sorted = sorted(records, key=lambda r: (r.get("game_date", ""), r.get("game_id", "")))
    total_games = len(records_sorted)
    margins = [r["score"]["self"] - r["score"]["opponent"] for r in records_sorted]
    wins = sum(1 for m in margins if m > 0)
    losses = sum(1 for m in margins if m < 0)
    draws = total_games - wins - losses

    avg_self = statistics.fmean(r["score"]["self"] for r in records_sorted)
    avg_opp = statistics.fmean(r["score"]["opponent"] for r in records_sorted)
    avg_margin = statistics.fmean(margins)

    best_idx = max(range(total_games), key=lambda i: margins[i])
    worst_idx = min(range(total_games), key=lambda i: margins[i])

    lines.append("## Overall")
    lines.append("")
    lines.append(f"- Games: **{total_games}**")
    lines.append(f"- Record: **{wins}-{losses}-{draws}** (W-L-D)")
    lines.append(f"- Average score: **{avg_self:.1f} - {avg_opp:.1f}**")
    lines.append(f"- Average margin: **{avg_margin:+.1f} VP** (self - opponent)")
    lines.append(
        f"- Best margin: **{margins[best_idx]:+d} VP** in `{records_sorted[best_idx]['game_id']}`"
    )
    lines.append(
        f"- Worst margin: **{margins[worst_idx]:+d} VP** in `{records_sorted[worst_idx]['game_id']}`"
    )
    lines.append("")

    lines.append("## Average Category Deltas")
    lines.append("")
    lines.append("| Category | Avg Delta (self - opponent) |")
    lines.append("|---|---:|")
    for cat in CATEGORIES:
        delta = statistics.fmean(
            r["breakdown"]["self"][cat] - r["breakdown"]["opponent"][cat] for r in records_sorted
        )
        lines.append(f"| {cat} | {delta:+.1f} |")
    lines.append("")

    by_strategy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in records_sorted:
        by_strategy[rec["planned_strategy"]].append(rec)

    lines.append("## By Planned Strategy")
    lines.append("")
    lines.append("| Strategy | Games | Win Rate | Avg Margin |")
    lines.append("|---|---:|---:|---:|")
    for strategy in sorted(by_strategy):
        group = by_strategy[strategy]
        group_margins = [r["score"]["self"] - r["score"]["opponent"] for r in group]
        group_wins = sum(1 for m in group_margins if m > 0)
        win_rate = (100.0 * group_wins / len(group)) if group else 0.0
        avg_group_margin = statistics.fmean(group_margins) if group_margins else 0.0
        lines.append(f"| {strategy} | {len(group)} | {win_rate:.1f}% | {avg_group_margin:+.1f} |")
    lines.append("")

    mistake_counter: Counter[str] = Counter()
    for rec in records_sorted:
        mistake_counter.update(rec.get("mistake_tags", []))

    lines.append("## Top Mistake Tags")
    lines.append("")
    if mistake_counter:
        for tag, count in mistake_counter.most_common(10):
            lines.append(f"- `{tag}`: {count}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Recent Games")
    lines.append("")
    lines.append("| Date | Game ID | Strategy | Gen | Score (self-opp) | Margin |")
    lines.append("|---|---|---|---:|---|---:|")
    for rec in records_sorted[-10:]:
        margin = rec["score"]["self"] - rec["score"]["opponent"]
        lines.append(
            "| {date} | {gid} | {strategy} | {gen} | {s}-{o} | {m:+d} |".format(
                date=rec["game_date"],
                gid=rec["game_id"],
                strategy=rec["planned_strategy"],
                gen=rec["finish_generation"],
                s=rec["score"]["self"],
                o=rec["score"]["opponent"],
                m=margin,
            )
        )
    lines.append("")
    return "\n".join(lines)


def _write_rollup(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = _build_rollup(records)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)


def cmd_init_summary(args: argparse.Namespace) -> int:
    template = _load_json(args.template)
    template["game_url"] = args.game_url
    template["game_date"] = args.game_date
    template["game_id"] = _infer_game_id(args.game_url)

    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.force:
        raise ValidationError(f"Output already exists: {output}. Use --force to overwrite.")

    with output.open("w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=True)
        f.write("\n")

    print(f"Wrote summary template: {output}")
    return 0


def cmd_append(args: argparse.Namespace) -> int:
    record = _load_json(args.summary)
    _validate_record(record)

    records = _read_dataset(args.dataset)
    existing_ids = {r.get("game_id") for r in records}
    existing_urls = {r.get("game_url") for r in records}

    if not args.allow_duplicate:
        if record["game_id"] in existing_ids:
            raise ValidationError(f"Duplicate game_id: {record['game_id']}")
        if record["game_url"] in existing_urls:
            raise ValidationError(f"Duplicate game_url: {record['game_url']}")

    records.append(record)
    _write_dataset(args.dataset, records)
    _write_rollup(args.rollup, records)

    print(f"Appended: {record['game_id']}")
    print(f"Dataset: {args.dataset}")
    print(f"Rollup: {args.rollup}")
    return 0


def cmd_rollup(args: argparse.Namespace) -> int:
    records = _read_dataset(args.dataset)
    for rec in records:
        _validate_record(rec)
    _write_rollup(args.rollup, records)
    print(f"Rollup written: {args.rollup}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gameplay learning helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-summary", help="Create summary JSON from template")
    p_init.add_argument("--output", type=Path, required=True)
    p_init.add_argument("--game-url", required=True)
    p_init.add_argument("--game-date", required=True)
    p_init.add_argument("--template", type=Path, default=SUMMARY_TEMPLATE_DEFAULT)
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_init_summary)

    p_append = sub.add_parser("append", help="Validate and append summary to dataset")
    p_append.add_argument("--summary", type=Path, required=True)
    p_append.add_argument("--dataset", type=Path, default=DATASET_DEFAULT)
    p_append.add_argument("--rollup", type=Path, default=ROLLUP_DEFAULT)
    p_append.add_argument("--allow-duplicate", action="store_true")
    p_append.set_defaults(func=cmd_append)

    p_roll = sub.add_parser("rollup", help="Regenerate rollup markdown")
    p_roll.add_argument("--dataset", type=Path, default=DATASET_DEFAULT)
    p_roll.add_argument("--rollup", type=Path, default=ROLLUP_DEFAULT)
    p_roll.set_defaults(func=cmd_rollup)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValidationError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
