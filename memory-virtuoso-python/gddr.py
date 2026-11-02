"""GDDR-style educational DRAM tile for GPDK045.

Important distinction
----------------------
GDDR is an interface / standard family (GDDR5, GDDR6, GDDR6X, ...), not a
new storage-cell type.  The storage cell is still a 1T1C DRAM cell.  GDDR
adds high-speed DQ I/O, a source-synchronous clock, equalization, and
(optionally) PAM4 signaling at the interface.  This script therefore
generates a 1T1C cell plus a deliberately simplified "GDDR6-style" read
tile: array, precharge, sense amp and a single-ended output buffer.

It is not a GDDR PHY, not a timing model, and not a replacement for a
memory compiler.
"""

from __future__ import annotations

from common import Cell, VDD, VSS, capacitor, instance, nmos, pmos

ACCESS_W = 0.150
CAP_FF = 8.0

PC_W = 0.180
SA_P_W = 0.240
SA_N_W = 0.240
SA_TAIL_W = 0.480

IO_P_W = 0.240
IO_N_W = 0.120

ROWS = 4
COLS = 4


def gddr6_cell(w: float = ACCESS_W, cap_ff: float = CAP_FF) -> Cell:
    """GDDR-style 1T1C storage cell (same topology as DRAM1T1C)."""
    body = (
        nmos("M0", "BL", "WL", "SN", VSS, w=w),
        capacitor("C0", "SN", "PLATE", cap_ff),
    )
    return Cell(
        "GDDR6_CELL",
        ("BL", "WL", "PLATE", VSS),
        body,
        "GDDR-style 1T1C cell; ideal capacitor for education",
    )


def gddr6_precharge(w: float = PC_W) -> Cell:
    body = (
        pmos("MP0", "BL", "PRE", "VBL", VDD, w=w),
        pmos("MP1", "BLB", "PRE", "VBL", VDD, w=w),
        pmos("MP2", "BL", "BLB", "PRE", VDD, w=w),
    )
    return Cell(
        "GDDR6_PRECHARGE",
        ("BL", "BLB", "PRE", "VBL", VDD),
        body,
        "Active-low PMOS precharge/equalize to VBL",
    )


def gddr6_sense(
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
        "GDDR6_SENSE",
        ("BL", "BLB", "SAE", VDD, VSS),
        body,
        "GDDR tile sense amplifier",
    )


def gddr6_io(p_w: float = IO_P_W, n_w: float = IO_N_W) -> Cell:
    """Simplified single-ended output buffer (educational placeholder).

    A real GDDR transmitter needs pre-driver, slew control, termination,
    equalization and ESD.  This inverter is only a stand-in for the DQ pin.
    """
    body = (
        pmos("MP0", "PAD", "D", VDD, VDD, w=p_w),
        nmos("MN0", "PAD", "D", VSS, VSS, w=n_w),
    )
    return Cell(
        "GDDR6_IO",
        ("D", "PAD", VDD, VSS),
        body,
        "Simplified DQ output buffer placeholder",
    )


def gddr6_array(rows: int = ROWS, cols: int = COLS) -> Cell:
    wl = [f"WL{r}" for r in range(rows)]
    bl = [f"BL{c}" for c in range(cols)]
    body = tuple(
        instance(
            f"X{r}{c}",
            (bl[c], wl[r], "PLATE", VSS),
            "GDDR6_CELL",
        )
        for r in range(rows)
        for c in range(cols)
    )
    return Cell(
        f"GDDR6_ARRAY_{rows}X{cols}",
        (*wl, *bl, "PLATE", VSS),
        body,
        f"{rows}x{cols} array of GDDR6_CELL",
    )


def gddr6_tile(rows: int = ROWS, cols: int = COLS) -> Cell:
    wl = [f"WL{r}" for r in range(rows)]
    bl = [f"BL{c}" for c in range(cols)]
    blb = [f"BLB{c}" for c in range(cols)]
    dq = [f"DQ{c}" for c in range(cols)]
    body = [
        instance(
            "XARR",
            (*wl, *bl, "PLATE", VSS),
            f"GDDR6_ARRAY_{rows}X{cols}",
        )
    ]
    body += [
        instance(
            f"XPC{c}",
            (bl[c], blb[c], "PRE", "VBL", VDD),
            "GDDR6_PRECHARGE",
        )
        for c in range(cols)
    ]
    body += [
        instance(
            f"XSA{c}",
            (bl[c], blb[c], "SAE", VDD, VSS),
            "GDDR6_SENSE",
        )
        for c in range(cols)
    ]
    body += [
        instance(
            f"XIO{c}",
            (bl[c], dq[c], VDD, VSS),
            "GDDR6_IO",
        )
        for c in range(cols)
    ]
    return Cell(
        f"GDDR6_TILE_{rows}X{cols}",
        (*wl, *bl, *blb, *dq, "PRE", "SAE", "VBL", "PLATE", VDD, VSS),
        tuple(body),
        f"{rows}x{cols} GDDR6-style read tile (simplified)",
    )


def gddr_cells() -> list[Cell]:
    return [
        gddr6_cell(),
        gddr6_precharge(),
        gddr6_sense(),
        gddr6_io(),
        gddr6_array(),
        gddr6_tile(),
    ]
