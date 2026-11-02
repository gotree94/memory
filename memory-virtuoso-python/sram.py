"""6T SRAM bitcell and an educational 8x8 SRAM tile for GPDK045.

Topology
--------
        VDD                 VDD
         |                   |
       MP0                 MP1
         |                   |
  BL -- MN2 -- Q === QB -- MN3 -- BLB
         |                   |
       MN0                 MN1
         |                   |
        VSS                 VSS

MN2/MN3 are the access NMOS controlled by WL.  The cross-coupled
inverters (MP0/MN0 and MP1/MN1) store the bit.  This is a read/write
educational model, not a silicon-qualified SRAM bitcell.

Default sizing (GPDK045, L=45 nm):
    pull-down NMOS  W = 240 nm
    pull-up   PMOS  W = 120 nm
    access    NMOS  W = 180 nm
The pull-down/access ratio (beta ratio) is intentionally > 1 so that
the cell is less likely to flip during a read.  Real bitcells must be
sized with Monte Carlo, IR drop and DRC/LVS in the target memory process.
"""

from __future__ import annotations

from common import Cell, VDD, VSS, instance, nmos, pmos

PD_W = 0.240
PU_W = 0.120
PG_W = 0.180

PC_W = 0.120
SA_P_W = 0.240
SA_N_W = 0.240
SA_TAIL_W = 0.480

ROWS = 8
COLS = 8


def sram6t(
    pd_w: float = PD_W,
    pu_w: float = PU_W,
    pg_w: float = PG_W,
) -> Cell:
    """Return the 6T SRAM bitcell."""
    body = (
        pmos("MP0", "Q", "QB", VDD, VDD, w=pu_w),
        pmos("MP1", "QB", "Q", VDD, VDD, w=pu_w),
        nmos("MN0", "Q", "QB", VSS, VSS, w=pd_w),
        nmos("MN1", "QB", "Q", VSS, VSS, w=pd_w),
        nmos("MN2", "BL", "WL", "Q", VSS, w=pg_w),
        nmos("MN3", "BLB", "WL", "QB", VSS, w=pg_w),
    )
    return Cell(
        "SRAM6T",
        ("BL", "BLB", "WL", VDD, VSS),
        body,
        "6T SRAM bitcell: cross-coupled inverters + two access NMOS",
    )


def sram_precharge(w: float = PC_W) -> Cell:
    """Bitline precharge and equalization (active-low PRE)."""
    body = (
        pmos("MP0", "BL", "PRE", VDD, VDD, w=w),
        pmos("MP1", "BLB", "PRE", VDD, VDD, w=w),
        pmos("MP2", "BL", "BLB", VDD, VDD, w=w),
    )
    return Cell(
        "SRAM_PRECHARGE",
        ("BL", "BLB", "PRE", VDD),
        body,
        "Precharge BL/BLB to VDD and equalize them when PRE is low",
    )


def sram_sense(
    p_w: float = SA_P_W,
    n_w: float = SA_N_W,
    tail_w: float = SA_TAIL_W,
) -> Cell:
    """Cross-coupled latch sense amplifier with an SAE tail switch."""
    body = (
        pmos("MP0", "BL", "BLB", VDD, VDD, w=p_w),
        pmos("MP1", "BLB", "BL", VDD, VDD, w=p_w),
        nmos("MN0", "BL", "BLB", "N0", VSS, w=n_w),
        nmos("MN1", "BLB", "BL", "N0", VSS, w=n_w),
        nmos("MN2", "N0", "SAE", VSS, VSS, w=tail_w),
    )
    return Cell(
        "SRAM_SENSE",
        ("BL", "BLB", "SAE", VDD, VSS),
        body,
        "Cross-coupled sense amplifier; SAE enables the NMOS tail",
    )


def sram_array(rows: int = ROWS, cols: int = COLS) -> Cell:
    """Array of 6T bitcells, without periphery."""
    wl = [f"WL{r}" for r in range(rows)]
    bl = [f"BL{c}" for c in range(cols)]
    blb = [f"BLB{c}" for c in range(cols)]
    body = tuple(
        instance(
            f"X{r}{c}",
            (bl[c], blb[c], wl[r], VDD, VSS),
            "SRAM6T",
        )
        for r in range(rows)
        for c in range(cols)
    )
    return Cell(
        f"SRAM_ARRAY_{rows}X{cols}",
        (*wl, *bl, *blb, VDD, VSS),
        body,
        f"{rows}x{cols} array of SRAM6T bitcells",
    )


def sram_tile(rows: int = ROWS, cols: int = COLS) -> Cell:
    """Array + per-column precharge and sense amplifiers."""
    wl = [f"WL{r}" for r in range(rows)]
    bl = [f"BL{c}" for c in range(cols)]
    blb = [f"BLB{c}" for c in range(cols)]
    body = [
        instance(
            "XARR",
            (*wl, *bl, *blb, VDD, VSS),
            f"SRAM_ARRAY_{rows}X{cols}",
        )
    ]
    body += [
        instance(
            f"XPC{c}",
            (bl[c], blb[c], "PRE", VDD),
            "SRAM_PRECHARGE",
        )
        for c in range(cols)
    ]
    body += [
        instance(
            f"XSA{c}",
            (bl[c], blb[c], "SAE", VDD, VSS),
            "SRAM_SENSE",
        )
        for c in range(cols)
    ]
    return Cell(
        f"SRAM_TILE_{rows}X{cols}",
        (*wl, *bl, *blb, "PRE", "SAE", VDD, VSS),
        tuple(body),
        f"{rows}x{cols} SRAM tile with precharge and sense amplifiers",
    )


def sram_cells() -> list[Cell]:
    return [
        sram6t(),
        sram_precharge(),
        sram_sense(),
        sram_array(),
        sram_tile(),
    ]
