"""Run AICertify against a financial-advice-bot contract.

From the repo root::

    python examples/financial-advice-bot/run.py

Loads ``policy_config.yaml`` and ``input_contract.json`` (canonical
``AiCertifyContract`` shape) so documented config changes are applied.
Exits nonzero if any regulation evaluation errors or expected reports are missing.

A green report does **not** authorise financial-advice delivery.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import yaml

WITH_LLM_METRICS = os.environ.get("AICERTIFY_WITH_LLM_METRICS") == "1"
if not WITH_LLM_METRICS:
    os.environ.pop("OPENAI_API_KEY", None)

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

from aicertify import application, regulations  # noqa: E402
from aicertify.models.contract import load_contract  # noqa: E402

EXAMPLE_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = EXAMPLE_DIR / "input_contract.json"
POLICY_PATH = EXAMPLE_DIR / "policy_config.yaml"
OUTPUT_DIR = Path.cwd() / "reports"


def _load_policy_config() -> dict:
    raw = yaml.safe_load(POLICY_PATH.read_text())
    if not isinstance(raw, dict):
        raise ValueError(f"{POLICY_PATH} must contain a mapping")
    return raw


async def main() -> int:
    cfg = _load_policy_config()
    contract = load_contract(CONTRACT_PATH)
    if contract is None:
        print(f"error: could not load contract from {CONTRACT_PATH}", file=sys.stderr)
        return 1

    regs = regulations.create("financial-advice-bot-eval")
    for framework in cfg.get("frameworks", []):
        fw_id = framework.get("id")
        if not fw_id:
            continue
        try:
            regs.add(fw_id)
        except ValueError as exc:
            print(f"warning: skipping framework {fw_id!r}: {exc}", file=sys.stderr)

    if not regs.get_regulations():
        print("error: no regulations loaded from policy_config.yaml", file=sys.stderr)
        return 1

    report_cfg = cfg.get("report") or {}
    formats = report_cfg.get("formats") or ["pdf"]
    output_dir = Path(report_cfg.get("output_dir") or "reports")
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir

    app = application.create(
        name=contract.application_name,
        model_name=contract.model_info.model_name,
        model_version=contract.model_info.model_version,
        model_metadata=dict(contract.model_info.metadata or {}),
    )
    # Prefer the file's validated contract (UUID, context, compliance_context).
    app.contract = contract

    output_dir.mkdir(parents=True, exist_ok=True)
    had_error = False
    for fmt in formats:
        results = await app.evaluate(
            regulations=regs,
            report_format=str(fmt),
            output_dir=str(output_dir),
        )
        for name, result in results.items():
            if isinstance(result, dict) and result.get("error"):
                print(
                    f"error: evaluation failed for {name} ({fmt}): {result['error']}",
                    file=sys.stderr,
                )
                had_error = True

    report_paths = app.get_report()
    print("\nGenerated reports:")
    if isinstance(report_paths, dict):
        if not report_paths:
            print("  (none)", file=sys.stderr)
            had_error = True
        for framework, path in report_paths.items():
            print(f"  - {framework}: {path}")
            if not path or not Path(path).exists():
                print(f"error: missing report file for {framework}: {path}", file=sys.stderr)
                had_error = True
    else:
        print(f"  - {report_paths}")

    print(
        "\nReminder: a green AICertify report does NOT authorise financial-advice "
        "delivery, credit decisions, or MiFID/FCA advice permissions. Deployer "
        "remains responsible for organisational compliance and licensing."
    )
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
