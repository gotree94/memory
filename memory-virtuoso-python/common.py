"""Common CDL helpers for the memory-cell generators.

The scripts target the same educational environment as the sibling
``virtuoso-python`` project:

    GPDK045 v6.0 / Virtuoso IC6.1.8 / Python 3.8+

Only a CDL netlist is generated here.  Import the CDL with Virtuoso's
CDL In flow to create schematics.  Layout, DRC, LVS and PEX are outside
the scope of this educational scaffold.

CDL MOS order is:  M<name> <drain> <gate> <source> <bulk> <model> w= l= nf= m=
Capacitors and resistors use ideal SPICE elements and must be replaced by
PDK MIM/MOM or extracted TSV models before any real sign-off work.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Union

# ---------------------------------------------------------------------------
# GPDK045 defaults
# ---------------------------------------------------------------------------
NMOS_MODEL = "g45n1svt"
PMOS_MODEL = "g45p1svt"
L = 0.045

VDD = "VDD"
VSS = "VSS"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def _um(value: float) -> str:
    """0.045 -> '0.045u'."""
    return f"{value:g}u"


# ---------------------------------------------------------------------------
# CDL body items
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Mos:
    name: str
    drain: str
    gate: str
    source: str
    bulk: str
    model: str
    w: float
    l: float = L
    nf: int = 1
    m: int = 1

    def line(self) -> str:
        return (
            f"{self.name} {self.drain} {self.gate} {self.source} {self.bulk} "
            f"{self.model} w={_um(self.w)} l={_um(self.l)} nf={self.nf} m={self.m}"
        )


@dataclass(frozen=True)
class Capacitor:
    name: str
    positive: str
    negative: str
    c_ff: float

    def line(self) -> str:
        return f"{self.name} {self.positive} {self.negative} {self.c_ff:g}f"


@dataclass(frozen=True)
class Resistor:
    name: str
    positive: str
    negative: str
    r_ohm: float

    def line(self) -> str:
        return f"{self.name} {self.positive} {self.negative} {self.r_ohm:g}"


@dataclass(frozen=True)
class SubcktInstance:
    name: str
    pins: tuple[str, ...]
    master: str

    def line(self) -> str:
        return " ".join((self.name, *self.pins, self.master))


BodyItem = Union[Mos, Capacitor, Resistor, SubcktInstance, str]


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------
def nmos(
    name: str,
    drain: str,
    gate: str,
    source: str,
    bulk: str = VSS,
    w: float = 0.120,
    l: float = L,
    nf: int = 1,
    m: int = 1,
) -> Mos:
    return Mos(name, drain, gate, source, bulk, NMOS_MODEL, w, l, nf, m)


def pmos(
    name: str,
    drain: str,
    gate: str,
    source: str,
    bulk: str = VDD,
    w: float = 0.240,
    l: float = L,
    nf: int = 1,
    m: int = 1,
) -> Mos:
    return Mos(name, drain, gate, source, bulk, PMOS_MODEL, w, l, nf, m)


def capacitor(name: str, positive: str, negative: str, c_ff: float) -> Capacitor:
    return Capacitor(name, positive, negative, c_ff)


def resistor(name: str, positive: str, negative: str, r_ohm: float) -> Resistor:
    return Resistor(name, positive, negative, r_ohm)


def instance(name: str, pins: Iterable[str], master: str) -> SubcktInstance:
    return SubcktInstance(name, tuple(pins), master)


# ---------------------------------------------------------------------------
# Cell and file output
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Cell:
    name: str
    pins: tuple[str, ...]
    body: tuple[BodyItem, ...]
    comment: str = ""

    def cdl(self) -> str:
        lines = [f".SUBCKT {self.name} {' '.join(self.pins)}"]
        if self.comment:
            lines.append(f"* {self.comment}")
        for item in self.body:
            lines.append(item if isinstance(item, str) else item.line())
        lines.append(".ENDS")
        return "\n".join(lines) + "\n"

    def counts(self) -> dict[str, int]:
        return {
            "mos": sum(isinstance(item, Mos) for item in self.body),
            "cap": sum(isinstance(item, Capacitor) for item in self.body),
            "res": sum(isinstance(item, Resistor) for item in self.body),
            "x": sum(isinstance(item, SubcktInstance) for item in self.body),
        }

    def summary(self) -> dict[str, object]:
        return {
            "name": self.name,
            "pins": list(self.pins),
            **self.counts(),
            "lines": len(self.cdl().splitlines()),
        }

    def write(self, out_dir: Path) -> Path:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{self.name}.cdl"
        path.write_text(self.cdl(), encoding="utf-8")
        return path


def write_cells(cells: Iterable[Cell], out_dir: Path) -> list[Path]:
    """Write all cells to ``out_dir`` and return the generated paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for cell in cells:
        paths.append(cell.write(out_dir))
    return paths
