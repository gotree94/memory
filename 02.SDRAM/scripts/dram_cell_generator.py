# =============================================================================
# DRAM / SDRAM 셀 파라미터/설정 제너레이터 (Python)
# DRAM Design Parameter & Config Generator
#
# 역할:
#   - DRAM 세대별 1T1C 셀 파라미터 정의
#   - Virtuoso SKILL 실행용 설정 JSON 생성
#   - 실제 레이아웃 객체 생성은 dram_cell_generator.skill이 담당
#
# 언어 조합 (최종 표준):
#   - Python : 파라미터 계산 + 설정/레포트 생성
#   - SKILL  : Virtuoso 레이아웃 생성 (본 파일이 호출 대상을 안내)
#   - Tcl    : DRC/LVS/시뮬레이션 흐름 제어 (flow/tcl)
# =============================================================================

import json
import pathlib
import sys
from dataclasses import dataclass, asdict
from typing import List
from enum import Enum

# Cadence 45nm 학습 PDK 메타데이터 (flow/python)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "flow" / "python"))
try:
    from cadence45 import write_cadence45_meta
    _HAS_CAD45 = True
except ImportError:
    _HAS_CAD45 = False


class CapacitorType(Enum):
    PLANAR = "planar"
    TRENCH = "trench"
    STACKED_CYLINDER = "stacked_cylinder"
    MIM = "mim"
    BCAT = "bcat"
    BCAT_HAR = "bcat_har"
    PILLAR = "pillar"


@dataclass
class DRAMCellConfig:
    """DRAM 1T1C 셀 설계 파라미터 (세대별)"""
    generation: str
    node_nm: float
    vdd: float
    capacitor: str
    aspect_ratio: float
    cell_height_nm: float
    cell_width_nm: float
    cap_value_fF: float
    refresh_time_ms: float
    tRCD_ns: float
    data_rate_MTs: float
    bandwidth_GB_s: float
    package: str


# =============================================================================
# 세대별 1T1C 파라미터
# =============================================================================
DRAM_GENERATIONS = [
    DRAMCellConfig("1세대 DRAM", 8000, 5.0, "planar", 1,
                   16000, 8000, 50, 4, 100, 0, 0, "DIP"),
    DRAMCellConfig("EDO DRAM", 600, 3.3, "trench", 5,
                   2400, 1200, 30, 4, 40, 0, 0, "SIMM, DIP"),
    DRAMCellConfig("SDRAM", 350, 3.3, "stacked_cylinder", 15,
                   1400, 700, 25, 64, 15, 133, 1.06, "DIMM, SIMM"),
    DRAMCellConfig("DDR (DDR1)", 180, 2.5, "mim", 25,
                   700, 350, 20, 64, 10, 266, 2.1, "DIMM (184)"),
    DRAMCellConfig("DDR2", 90, 1.8, "mim", 40,
                   350, 175, 15, 64, 5, 667, 5.3, "DIMM (240)"),
    DRAMCellConfig("DDR3", 65, 1.5, "bcat", 60,
                   260, 130, 12, 64, 3.5, 1600, 12.8, "DIMM (240)"),
    DRAMCellConfig("DDR4", 30, 1.2, "bcat_har", 100,
                   120, 60, 10, 64, 2.5, 3200, 25.6, "DIMM (288)"),
    DRAMCellConfig("DDR5", 14, 1.1, "pillar", 160,
                   56, 28, 8, 32, 1.75, 6400, 51.2, "DIMM (288)"),
]


# =============================================================================
# SKILL 생성 안내 (실제 코드는 .skill 파일)
# =============================================================================
def skill_generation_guide(config: DRAMCellConfig) -> str:
    """각 커패시터 타입에 해당하는 SKILL 생성 함수를 안내"""
    func_map = {
        "planar":           'dramCreatePlanar("dram_lib" "cell" "8um")',
        "trench":           'dramCreateTrench("dram_lib" "cell" "600nm")',
        "stacked_cylinder": 'dramCreateStackedCylinder("dram_lib" "cell" "350nm")',
        "mim":              'dramCreateStackedCylinder("dram_lib" "cell" "90nm")',
        "bcat":             'dramCreateBCAT("dram_lib" "cell" "65nm")',
        "bcat_har":         'dramCreateBCAT("dram_lib" "cell" "30nm")',
        "pillar":           'dramCreatePillar("dram_lib" "cell" "14nm")',
    }
    call = func_map.get(config.capacitor, "?")

    return (
        f"; DRAM {config.generation} @ {config.node_nm}nm\n"
        f";  커패시터: {config.capacitor}, AR {config.aspect_ratio}:1, "
        f"Cap {config.cap_value_fF}fF\n"
        f";  셀: {config.cell_height_nm}nm x {config.cell_width_nm}nm, "
        f"VDD {config.vdd}V\n"
        f";  생성   : {call}\n"
        f";  어레이 : dramCreateArray(\"dram_lib\" \"cell\" \"layout\" rows cols banks)\n"
    )


# =============================================================================
# 설정 JSON 생성
# =============================================================================
def generate_config_json() -> str:
    return json.dumps([asdict(c) for c in DRAM_GENERATIONS],
                      indent=2, ensure_ascii=False)


def main():
    print("=" * 60)
    print("DRAM / SDRAM Design Parameter Generator")
    print("=" * 60)

    print("\n[SKILL Guide]")
    for cfg in DRAM_GENERATIONS:
        print(skill_generation_guide(cfg), end="")

    # 요약 테이블
    print("\n[Summary]")
    print("-" * 88)
    print(f"{'Gen':<14} {'Node':<6} {'VDD':<5} {'Cap':<16} {'AR':<5} "
          f"{'Rate':<7} {'BW(GB/s)':<9} {'Pkg':<14}")
    print("-" * 88)
    for c in DRAM_GENERATIONS:
        print(f"{c.generation:<14} {c.node_nm:<6.0f} {c.vdd:<5.1f} "
              f"{c.capacitor:<16} {c.aspect_ratio:<5} {c.data_rate_MTs:<7.0f} "
              f"{c.bandwidth_GB_s:<9.2f} {c.package:<14}")
    print("-" * 88)

    # config 파일 저장
    import pathlib
    out = pathlib.Path(__file__).parent / "generated"
    out.mkdir(exist_ok=True)
    (out / "dram_cell_configs.json").write_text(
        generate_config_json(), encoding="utf-8")
    print(f"\nSaved: {out / 'dram_cell_configs.json'}")

    # Cadence 45nm 학습 PDK 메타데이터 (GPDK045 + gsclib045)
    if _HAS_CAD45:
        meta = write_cadence45_meta(out)
        print(f"Saved: {meta} (Cadence 45nm GPDK/gsclib catalog)")
    else:
        print("WARN: cadence45.py not found in flow/python")
    print("=" * 60)


if __name__ == "__main__":
    main()
