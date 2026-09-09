"""Run AICertify against a financial-advice-bot contract.

From the repo root::

    python examples/financial-advice-bot/run.py

Demonstrates a general financial-*education* assistant (never personalised
advice) evaluated against the EU AI Act, gopal BFS fair-lending / model-risk
policies, and the global cross-cutting bundle.

A green report does **not** authorise financial-advice delivery.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

WITH_LLM_METRICS = os.environ.get("AICERTIFY_WITH_LLM_METRICS") == "1"
if not WITH_LLM_METRICS:
    os.environ.pop("OPENAI_API_KEY", None)

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

from aicertify import application, regulations  # noqa: E402

EXAMPLE_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = EXAMPLE_DIR / "input_contract.json"
OUTPUT_DIR = Path.cwd() / "reports"


async def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text())

    regs = regulations.create("financial-advice-bot-eval")
    regs.add("eu_ai_act")
    regs.add("bfs")
    # Align with policy_config.yaml (eu_ai_act + bfs + global). Global may be
    # skipped by PolicyLoader topology in some installs; tolerate absence.
    try:
        regs.add("global")
    except ValueError:
        pass

    app = application.create(
        name=contract["application_name"],
        model_name=contract["model"]["model_name"],
        model_version=contract["model"]["model_version"],
        model_metadata=contract["model"].get("metadata", {}),
    )
    for interaction in contract["interactions"]:
        app.add_interaction(
            input_text=interaction["input_text"],
            output_text=interaction["output_text"],
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    await app.evaluate(
        regulations=regs,
        report_format="pdf",
        output_dir=str(OUTPUT_DIR),
    )

    report_paths = app.get_report()
    print("\nGenerated reports:")
    for framework, path in report_paths.items():
        print(f"  - {framework}: {path}")

    print(
        "\nReminder: a green AICertify report does NOT authorise financial-advice "
        "delivery, credit decisions, or MiFID/FCA advice permissions. Deployer "
        "remains responsible for organisational compliance and licensing."
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
