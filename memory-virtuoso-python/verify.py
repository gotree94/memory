"""Validate generated CDL files against the manifests.

Usage:
    python verify.py
    python verify.py --out out --strict

Checks:
  - one .SUBCKT / one .ENDS per file
  - subcircuit name and pin list match the manifest
  - M/C/R/X device counts match the manifest
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SUB_RE = re.compile(r"^\.SUBCKT\s+(\S+)\s*(.*)$", re.MULTILINE)
MOS_RE = re.compile(r"^M\S+\s+", re.MULTILINE)
CAP_RE = re.compile(r"^C\S+\s+", re.MULTILINE)
RES_RE = re.compile(r"^R\S+\s+", re.MULTILINE)
X_RE = re.compile(r"^X\S+\s+", re.MULTILINE)
ENDS_RE = re.compile(r"^\.ENDS\b", re.MULTILINE)


def parse_cdl(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = SUB_RE.search(text)
    if not match:
        raise ValueError(f"{path}: no .SUBCKT")
    pins = match.group(2).split()
    return {
        "name": match.group(1),
        "pins": pins,
        "mos": len(MOS_RE.findall(text)),
        "cap": len(CAP_RE.findall(text)),
        "res": len(RES_RE.findall(text)),
        "x": len(X_RE.findall(text)),
        "subckts": len(SUB_RE.findall(text)),
        "ends": len(ENDS_RE.findall(text)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated memory CDL")
    parser.add_argument("--out", default="out", help="output root directory")
    parser.add_argument("--strict", action="store_true", help="exit 1 on any mismatch")
    args = parser.parse_args()

    out_root = Path(args.out)
    manifest_path = out_root / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"manifest not found: {manifest_path} (run run_all.py first)")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    checked = 0

    for group, cells in manifest.items():
        for name, expected in cells.items():
            path = out_root / group / f"{name}.cdl"
            if not path.exists():
                errors.append(f"missing file: {path}")
                continue

            actual = parse_cdl(path)
            checked += 1

            if actual["subckts"] != 1 or actual["ends"] != 1:
                errors.append(
                    f"{path}: subckt/ends = {actual['subckts']}/{actual['ends']}"
                )
            if actual["name"] != name:
                errors.append(f"{path}: name {actual['name']} != {name}")
            if actual["pins"] != expected["pins"]:
                errors.append(
                    f"{path}: pins {actual['pins']} != {expected['pins']}"
                )
            for key in ("mos", "cap", "res", "x"):
                if actual[key] != expected[key]:
                    errors.append(
                        f"{path}: {key} {actual[key]} != {expected[key]}"
                    )
            if not errors:
                print(
                    f"[OK] {group}/{name}: "
                    f"pins={len(actual['pins'])} "
                    f"mos={actual['mos']} cap={actual['cap']} "
                    f"res={actual['res']} x={actual['x']}"
                )

    print(f"\nchecked={checked} errors={len(errors)}")
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        if args.strict:
            raise SystemExit(1)
        return

    print("[PASS] all generated CDL files match their manifests")


if __name__ == "__main__":
    main()
