# =============================================================================
# SRAM 셀 파라미터/설정 제너레이터 (Python)
# SRAM Design Parameter & Config Generator
#
# 역할:
#   - SRAM 세대별 (6T/8T/10T) 셀 파라미터 정의
#   - Virtuoso SKILL 실행용 설정 JSON 생성
#   - 실제 레이아웃 객체 생성은 sram_6t/8t/10t_generator.skill이 담당
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

# Cadence 45nm 학습 PDK 메타데이터 (flow/python)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "flow" / "python"))
try:
    from cadence45 import write_cadence45_meta
    _HAS_CAD45 = True
except ImportError:
    _HAS_CAD45 = False

SEMICONDUCTOR_LAMBDA = 0.5  # λ = min_pitch / 2


@dataclass
class SRAMCellConfig:
    """SRAM 셀 설계 파라미터 (세대별)"""
    generation: str
    cell_type: str          # 6T, 8T, 10T
    node_nm: float          # 공정 (nm)
    vdd: float              # V
    cell_height_nm: float
    cell_width_nm: float
    pull_up_width_nm: float
    pull_down_width_nm: float
    pass_gate_width_nm: float
    snm_mv: float
    access_time_ns: float
    leakage_nA: float


# =============================================================================
# 세대별 6T 파라미터
# =============================================================================
SRAM_6T_GENERATIONS = [
    SRAMCellConfig("1세대", "6T", 5000, 5.0, 40000, 20000,
                   10000, 10000, 5000, 800, 50.0, 1000.0),
    SRAMCellConfig("2세대", "6T", 1000, 5.0, 8000, 4000,
                   2000, 2000, 1500, 650, 15.0, 100.0),
    SRAMCellConfig("3세대", "6T", 350, 3.3, 1400, 800,
                   700, 700, 500, 450, 5.0, 10.0),
    SRAMCellConfig("4세대", "6T", 65, 1.1, 360, 140,
                   210, 140, 105, 250, 0.5, 1.0),
    SRAMCellConfig("5세대", "6T", 14, 0.75, 72, 30,
                   42, 28, 21, 180, 0.1, 0.1),
]

# =============================================================================
# 8T / 10T 파라미터 (듀얼 포트)
# =============================================================================
SRAM_8T_GENERATIONS = [
    SRAMCellConfig("4세대", "8T", 65, 1.1, 360, 196,
                   210, 140, 105, 280, 0.45, 1.5),
    SRAMCellConfig("5세대", "8T", 14, 0.75, 72, 40,
                   42, 28, 21, 200, 0.08, 0.15),
]

SRAM_10T_GENERATIONS = [
    SRAMCellConfig("4세대", "10T", 65, 1.1, 360, 252,
                   210, 140, 105, 300, 0.42, 2.0),
    SRAMCellConfig("5세대", "10T", 14, 0.75, 72, 52,
                   42, 28, 21, 220, 0.07, 0.2),
]


# =============================================================================
# SKILL 생성 안내 (실제 코드는 .skill 파일)
# =============================================================================
def skill_generation_guide(cell_type: str, config: SRAMCellConfig) -> str:
    """각 셀 유형에 해당하는 SKILL 생성 함수를 안내"""
    funcs = {
        "6T": {
            "single": 'sram6TGenerate("sram_lib" "cell" "techNode")',
            "array":  'sram6TPlaceAndRoute("sram_lib" "cell" rows cols)',
        },
        "8T": {
            "single": 'sram8TGenerate("sram_lib" "cell" "techNode")',
            "array":  'sram8TArray("sram_lib" "cell" rows cols)',
        },
        "10T": {
            "single": 'sram10TGenerate("sram_lib" "cell" "techNode")',
            "array":  'sram10TArray("sram_lib" "cell" rows cols)',
        },
    }[cell_type]

    guide = (
        f"; SRAM {cell_type} @ {config.node_nm}nm ({config.generation})\n"
        f"; 셀: {config.cell_height_nm}nm x {config.cell_width_nm}nm, "
        f"SNM {config.snm_mv}mV, VDD {config.vdd}V\n"
        f"; 단일 셀 생성 : {funcs['single']}\n"
        f"; 어레이 생성  : {funcs['array']}\n"
    )
    return guide


# =============================================================================
# 설정 JSON 생성
# =============================================================================
def generate_config_json() -> str:
    all_configs = (SRAM_6T_GENERATIONS + SRAM_8T_GENERATIONS
                   + SRAM_10T_GENERATIONS)
    return json.dumps([asdict(c) for c in all_configs],
                      indent=2, ensure_ascii=False)


def main():
    print("=" * 60)
    print("SRAM Design Parameter Generator")
    print("=" * 60)

    # 설정 JSON 생성
    config_json = generate_config_json()
    print("\n[Config] SRAM cell parameters generated (JSON)")

    # SKILL 생성 가이드 출력
    print("\n[SKILL Guide]")
    for group, label in [
        (SRAM_6T_GENERATIONS, "6T"),
        (SRAM_8T_GENERATIONS, "8T"),
        (SRAM_10T_GENERATIONS, "10T"),
    ]:
        for cfg in group:
            guide = skill_generation_guide(label, cfg)
            print(guide, end="")

    # 요약 테이블
    print("\n[Summary]")
    print("-" * 80)
    print(f"{'Cell':<6} {'Gen':<6} {'Node':<6} {'VDD':<6} "
          f"{'Area(um2)':<12} {'SNM(mV)':<8} {'Acc(ns)':<8}")
    print("-" * 80)
    all_cfgs = (SRAM_6T_GENERATIONS + SRAM_8T_GENERATIONS
                + SRAM_10T_GENERATIONS)
    for c in all_cfgs:
        area = (c.cell_height_nm * c.cell_width_nm) / 1e6
        print(f"{c.cell_type:<6} {c.generation:<6} {c.node_nm:<6.0f} "
              f"{c.vdd:<6.2f} {area:<12.4f} {c.snm_mv:<8} {c.access_time_ns:<8}")
    print("-" * 80)

    # config 파일 저장
    import pathlib
    out = pathlib.Path(__file__).parent / "generated"
    out.mkdir(exist_ok=True)
    (out / "sram_cell_configs.json").write_text(config_json, encoding="utf-8")
    print(f"\nSaved: {out / 'sram_cell_configs.json'}")

    # Cadence 45nm 학습 PDK 메타데이터 (GPDK045 + gsclib045)
    if _HAS_CAD45:
        meta = write_cadence45_meta(out)
        print(f"Saved: {meta} (Cadence 45nm GPDK/gsclib catalog)")
    else:
        print("WARN: cadence45.py not found in flow/python")
    print("=" * 60)


if __name__ == "__main__":
    main()
