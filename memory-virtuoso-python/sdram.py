"""1T1C DRAM cell and an educational 8x8 SDRAM-style tile.

A real SDRAM cell is a storage capacitor plus one access transistor.  In a
logic PDK such as GPDK045 there is no deep-trench or stacked DRAM capacitor,
so this script uses an ideal capacitor to make the topology and the
array/periphery structure visible.  It is a schematic teaching model, not a
retention-qualified DRAM bitcell.

Topology
--------
             WL
              |
  BL --- M0 --+--- SN --- C0 --- PLATE
                    |
                   VSS (access NMOS bulk)

The tile uses an explicit ``VBL`` pin for the bitline precharge level.  A
real SDRAM uses a VDD/2 generator and a reference scheme; those blocks are
not modeled here.
"""

from __future__ import annotations

from common import Cell, VDD, VSS, capacitor, instance, nmos, pmos

ACCESS_W = 0.180
CAP_FF = 10.0

PC_W = 0.180
SA_P_W = 0.240
SA_N_W = 0.240
SA_TAIL_W = 0.480

ROWS = 8
COLS = 8


def dram1t1c(w: float = ACCESS_W, cap_ff: float = CAP_FF) -> Cell:
    """One-transistor, one-capacitor DRAM storage cell."""
    body = (
        nmos("M0", "BL", "WL", "SN", VSS, w=w),
        capacitor("C0", "SN", "PLATE", cap_ff),
    )
    return Cell(
        "DRAM1T1C",
        ("BL", "WL", "PLATE", VSS),
        body,
        "1T1C DRAM cell; C0 is an ideal educational storage capacitor",
    )


def dram_precharge(w: float = PC_W) -> Cell:
    """Active-low PMOS precharge/equalize to VBL.

    PMOS is used instead of an NMOS pass gate so that the bitline can settle
    at VBL without losing an NMOS threshold voltage.  A real SDRAM also needs
    a VDD/2 generator and a reference scheme.
    """
    body = (
        pmos("MP0", "BL", "PRE", "VBL", VDD, w=w),
        pmos("MP1", "BLB", "PRE", "VBL", VDD, w=w),
        pmos("MP2", "BL", "BLB", "PRE", VDD, w=w),
    )
    return Cell(
        "DRAM_PRECHARGE",
        ("BL", "BLB", "PRE", "VBL", VDD),
        body,
        "Active-low PMOS precharge/equalize to VBL",
    )


def dram_sense(
    p_w: float = SA_P_W,
    n_w: float = SA_N_W,
    tail_w: float = SA_TAIL_W,
) -> Cell:
    """Cross-coupled sense amplifier used by the DRAM tile."""
    body = (
        pmos("MP0", "BL", "BLB", VDD, VDD, w=p_w),
        pmos("MP1", "BLB", "BL", VDD, VDD, w=p_w),
        nmos("MN0", "BL", "BLB", "N0", VSS, w=n_w),
        nmos("MN1", "BLB", "BL", "N0", VSS, w=n_w),
        nmos("MN2", "N0", "SAE", VSS, VSS, w=tail_w),
    )
    return Cell(
        "DRAM_SENSE",
        ("BL", "BLB", "SAE", VDD, VSS),
        body,
        "Cross-coupled DRAM sense amplifier with SAE tail switch",
    )


def sdram_array(rows: int = ROWS, cols: int = COLS) -> Cell:
    """Array of 1T1C cells; BLB/reference generation is in the tile."""
    wl = [f"WL{r}" for r in range(rows)]
    bl = [f"BL{c}" for c in range(cols)]
    body = tuple(
        instance(
            f"X{r}{c}",
            (bl[c], wl[r], "PLATE", VSS),
            "DRAM1T1C",
        )
        for r in range(rows)
        for c in range(cols)
    )
    return Cell(
        f"SDRAM_ARRAY_{rows}X{cols}",
        (*wl, *bl, "PLATE", VSS),
        body,
        f"{rows}x{cols} array of DRAM1T1C cells",
    )


def sdram_tile(rows: int = ROWS, cols: int = COLS) -> Cell:
    """Array + per-column precharge and sense amplifiers."""
    wl = [f"WL{r}" for r in range(rows)]
    bl = [f"BL{c}" for c in range(cols)]
    blb = [f"BLB{c}" for c in range(cols)]
    body = [
        instance(
            "XARR",
            (*wl, *bl, "PLATE", VSS),
            f"SDRAM_ARRAY_{rows}X{cols}",
        )
    ]
    body += [
        instance(
            f"XPC{c}",
            (bl[c], blb[c], "PRE", "VBL", VDD),
            "DRAM_PRECHARGE",
        )
        for c in range(cols)
    ]
    body += [
        instance(
            f"XSA{c}",
            (bl[c], blb[c], "SAE", VDD, VSS),
            "DRAM_SENSE",
        )
        for c in range(cols)
    ]
    return Cell(
        f"SDRAM_TILE_{rows}X{cols}",
        (*wl, *bl, *blb, "PRE", "SAE", "VBL", "PLATE", VDD, VSS),
        tuple(body),
        f"{rows}x{cols} SDRAM-style tile with precharge and sense amplifiers",
    )


def sdram_cells() -> list[Cell]:
    return [
        dram1t1c(),
        dram_precharge(),
        dram_sense(),
        sdram_array(),
        sdram_tile(),
    ]
