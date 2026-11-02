"""Generate all memory-cell CDL files and manifests.

Usage:
    python run_all.py
    python run_all.py --only SRAM,SDRAM
    python run_all.py --out out
    python run_all.py --list

The output layout is:

    out/
      01_SRAM/   *.cdl + manifest.json
      02_SDRAM/  *.cdl + manifest.json
      03_GDDR/   *.cdl + manifest.json
      04_HBM/    *.cdl + manifest.json
      manifest.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

import gddr
import hbm
import sdram
import sram
from common import Cell, write_cells

GROUPS: dict[str, Callable[[], list[Cell]]] = {
    "01_SRAM": sram.sram_cells,
    "02_SDRAM": sdram.sdram_cells,
    "03_GDDR": gddr.gddr_cells,
    "04_HBM": hbm.hbm_cells,
}


def _selected(key: str, wanted: set[str]) -> bool:
    if not wanted:
        return True
    short = key.split("_", 1)[1].lower()
    return key.lower() in wanted or short in wanted


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate memory-cell CDL files")
    parser.add_argument("--out", default="out", help="output root directory")
    parser.add_argument(
        "--only",
        default=None,
        help="comma-separated groups: SRAM,SDRAM,GDDR,HBM",
    )
    parser.add_argument("--list", action="store_true", help="list cells and exit")
    args = parser.parse_args()

    wanted = {
        item.strip().lower()
        for item in (args.only or "").split(",")
        if item.strip()
    }
    out_root = Path(args.out)

    if args.list:
        for key, factory in GROUPS.items():
            if _selected(key, wanted):
                print(key)
                for cell in factory():
                    print(f"  {cell.name}  pins={len(cell.pins)}  {cell.counts()}")
        return

    all_manifest: dict[str, dict[str, object]] = {}
    for key, factory in GROUPS.items():
        if not _selected(key, wanted):
            continue

        cells = factory()
        group_dir = out_root / key
        paths = write_cells(cells, group_dir)
        manifest = {cell.name: cell.summary() for cell in cells}
        (group_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        all_manifest[key] = manifest
        print(f"[{key}] {len(paths)} cells -> {group_dir}")

    if not all_manifest:
        raise SystemExit(f"No groups matched: {sorted(wanted)}")

    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "manifest.json").write_text(
        json.dumps(all_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[MANIFEST] {out_root / 'manifest.json'}")


if __name__ == "__main__":
    main()
