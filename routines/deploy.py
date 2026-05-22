"""
deploy.py — Routine deployment helper.

Usage (run from inside the trading_bot/routines/ directory, or its parent):
    python routines/deploy.py

What it does:
1. Reads every .md file in the routines/ folder
2. Parses frontmatter (name, routine_id, cron, model, repo) + body prompt
3. Loads real API keys from .env and substitutes ${PLACEHOLDER} tokens
4. Outputs a deployment plan and writes routines/deploy_plan.json

Then, in a Claude Code conversation, say:
    "Execute the deploy plan in routines/deploy_plan.json"

Claude Code will call RemoteTrigger to create or update each routine and write
the returned routine IDs back into the .md frontmatter.
"""

import json
import os
import re
import sys
from pathlib import Path

# ── locate the trading_bot root ───────────────────────────────────────────────
HERE = Path(__file__).resolve().parent          # routines/
ROOT = HERE.parent                              # trading_bot/
ENV_FILE = ROOT / ".env"
ROUTINES_DIR = HERE
PLAN_FILE = HERE / "deploy_plan.json"


def load_env() -> dict[str, str]:
    """Load key=value pairs from .env (ignores comments and blanks)."""
    env: dict[str, str] = {}
    if not ENV_FILE.exists():
        print(f"[warn] .env not found at {ENV_FILE} — placeholders will NOT be substituted")
        return env
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Returns (meta dict, body string)."""
    if not text.startswith("---"):
        return {}, text
    end = text.index("---", 3)
    fm_block = text[3:end].strip()
    body = text[end + 3:].strip()

    meta: dict = {}
    for line in fm_block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def substitute(text: str, env: dict[str, str]) -> str:
    """Replace ${KEY} tokens with values from env."""
    def replacer(match):
        key = match.group(1)
        if key not in env:
            print(f"  [warn] placeholder ${{{key}}} has no value in .env")
            return match.group(0)
        return env[key]
    return re.sub(r"\$\{([^}]+)\}", replacer, text)


def main() -> None:
    env = load_env()
    md_files = sorted(ROUTINES_DIR.glob("*.md"))

    if not md_files:
        print("No .md routine files found in", ROUTINES_DIR)
        sys.exit(1)

    plan = []
    print(f"\n{'='*60}")
    print(f"  Trading Bot — Routine Deploy Plan")
    print(f"  Reading from: {ROUTINES_DIR}")
    print(f"{'='*60}\n")

    for md_path in md_files:
        raw = md_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)

        prompt = substitute(body, env)
        routine_id = meta.get("routine_id", "").strip()
        action = "update" if routine_id else "create"

        entry = {
            "action": action,
            "source_file": md_path.name,
            "routine_id": routine_id or None,
            "name": meta.get("name", md_path.stem),
            "cron": meta.get("cron", ""),
            "schedule_human": meta.get("schedule_human", ""),
            "enabled": meta.get("enabled", "true").lower() == "true",
            "model": meta.get("model", "claude-sonnet-4-6"),
            "repo": meta.get("repo", ""),
            "prompt": prompt,
        }
        plan.append(entry)

        status = f"UPDATE  (id: {routine_id})" if action == "update" else "CREATE  (new)"
        print(f"  [{action.upper():6}] {entry['name']}")
        print(f"           file   : {md_path.name}")
        print(f"           cron   : {entry['cron']}  ({entry['schedule_human']})")
        print(f"           status : {status}")
        print()

    PLAN_FILE.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"{'='*60}")
    print(f"  deploy_plan.json written to: {PLAN_FILE}")
    print(f"{'='*60}")
    print()
    print("Next step — in a Claude Code conversation, say:")
    print('  "Execute the deploy plan in routines/deploy_plan.json"')
    print()
    print("Claude Code will create/update each routine via RemoteTrigger")
    print("and write the routine IDs back into the .md files.\n")


if __name__ == "__main__":
    main()
