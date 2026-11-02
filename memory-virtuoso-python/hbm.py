"""HBM-style educational DRAM tile with a TSV model for GPDK045.

Important distinction
----------------------
HBM is a 3D stacked DRAM architecture with a very wide interface and
through-silicon vias (TSVs), not a new storage-cell type.  The storage cell
is still a 1T1C DRAM cell.  This script generates a 1T1C array plus a
simplified TSV model so that the stacking/interconnect idea is visible in
the netlist.

The TSV model is intentionally ideal: a series resistor and a shunt
capacitor.  A real TSV model needs process-specific RLC, keep-out zone,
substrate coupling and EM/IR checks.
"""

from __future__ import annotations

from common import Cell, VDD, VSS, capacitor, instance, nmos, pmos, resistor

ACCESS_W = 0.150
CAP_FF = 6.0

PC_W = 0.180
SA_P_W = 0.240
SA_N_W = 0.240
SA_TAIL_W = 0.480

TSV_R_OHM = 0.050
TSV_C_FF = 20.0

IO_P_W = 0.240
IO_N_W = 0.120

ROWS = 4
COLS = 4


def hbm3_cell(w: float = ACCESS_W, cap_ff: float = CAP_FF) -> Cell:
    """HBM-style 1T1C storage cell."""
    body = (
        nmos("M0", "BL", "WL", "SN", VSS, w=w),
        capacitor("C0", "SN", "PLATE", cap_ff),
    )
    return Cell(
        "HBM3_CELL",
        ("BL", "WL", "PLATE", VSS),
        body,
        "HBM-style 1T1C cell; ideal capacitor for education",
    )


def hbm3_precharge(w: float = PC_W) -> Cell:
    body = (
        pmos("MP0", "BL", "PRE", "VBL", VDD, w=w),
        pmos("MP1", "BLB", "PRE", "VBL", VDD, w=w),
        pmos("MP2", "BL", "BLB", "PRE", VDD, w=w),
    )
    return Cell(
        "HBM3_PRECHARGE",
        ("BL", "BLB", "PRE", "VBL", VDD),
        body,
        "Active-low PMOS precharge/equalize to VBL",
    )


def hbm3_sense(
    p_w: float = SA_P_W,
    n_w: float = SA_N_W,
    tail_w: float = SA_TAIL_W,
) -> Cell:
    body = (
        pmos("MP0", "BL", "BLB", VDD, VDD, w=p_w),
        pmos("MP1", "BLB", "BL", VDD, VDD, w=p_w),
        nmos("MN0", "BL", "BLB", "N0", VSS, w=n_w),
        nmos("MN1", "BLB", "BL", "N0", VSS, w=n_w),
        nmos("MN2", "N0", "SAE", VSS, VSS, w=tail_w),
    )
    return Cell(
        "HBM3_SENSE",
        ("BL", "BLB", "SAE", VDD, VSS),
        body,
        "HBM tile sense amplifier",
    )


def hbm3_io(p_w: float = IO_P_W, n_w: float = IO_N_W) -> Cell:
    """Simplified local output buffer before the TSV."""
    body = (
        pmos("MP0", "PAD", "D", VDD, VDD, w=p_w),
        nmos("MN0", "PAD", "D", VSS, VSS, w=n_w),
    )
    return Cell(
        "HBM3_IO",
        ("D", "PAD", VDD, VSS),
        body,
        "Simplified HBM local output buffer placeholder",
    )


def hbm3_tsv(r_ohm: float = TSV_R_OHM, c_ff: float = TSV_C_FF) -> Cell:
    """Ideal TSV: series R + shunt C to substrate."""
    body = (
        resistor("R0", "TOP", "BOTTOM", r_ohm),
        capacitor("C0", "BOTTOM", VSS, c_ff),
    )
    return Cell(
        "HBM3_TSV",
        ("TOP", "BOTTOM", VSS),
        body,
        "Ideal through-silicon-via model (R + C)",
    )


def hbm3_array(rows: int = ROWS, cols: int = COLS) -> Cell:
    wl = [f"WL{r}" for r in range(rows)]
    bl = [f"BL{c}" for c in range(cols)]
    body = tuple(
        instance(
            f"X{r}{c}",
            (bl[c], wl[r], "PLATE", VSS),
            "HBM3_CELL",
        )
        for r in range(rows)
        for c in range(cols)
    )
    return Cell(
        f"HBM3_ARRAY_{rows}X{cols}",
        (*wl, *bl, "PLATE", VSS),
        body,
        f"{rows}x{cols} array of HBM3_CELL",
    )


def hbm3_tile(rows: int = ROWS, cols: int = COLS) -> Cell:
    wl = [f"WL{r}" for r in range(rows)]
    bl = [f"BL{c}" for c in range(cols)]
    blb = [f"BLB{c}" for c in range(cols)]
    dq = [f"DQ{c}" for c in range(cols)]
    body = [
        instance(
            "XARR",
            (*wl, *bl, "PLATE", VSS),
            f"HBM3_ARRAY_{rows}X{cols}",
        )
    ]
    body += [
        instance(
            f"XPC{c}",
            (bl[c], blb[c], "PRE", "VBL", VDD),
            "HBM3_PRECHARGE",
        )
        for c in range(cols)
    ]
    body += [
        instance(
            f"XSA{c}",
            (bl[c], blb[c], "SAE", VDD, VSS),
            "HBM3_SENSE",
        )
        for c in range(cols)
    ]
    body += [
        instance(
            f"XIO{c}",
            (bl[c], f"TSVIN{c}", VDD, VSS),
            "HBM3_IO",
        )
        for c in range(cols)
    ]
    body += [
        instance(
            f"XTSV{c}",
            (f"TSVIN{c}", dq[c], VSS),
            "HBM3_TSV",
        )
        for c in range(cols)
    ]
    return Cell(
        f"HBM3_TILE_{rows}X{cols}",
        (*wl, *bl, *blb, *dq, "PRE", "SAE", "VBL", "PLATE", VDD, VSS),
        tuple(body),
        f"{rows}x{cols} HBM3-style tile with TSV models (simplified)",
    )


def hbm_cells() -> list[Cell]:
    return [
        hbm3_cell(),
        hbm3_precharge(),
        hbm3_sense(),
        hbm3_io(),
        hbm3_tsv(),
        hbm3_array(),
        hbm3_tile(),
    ]
