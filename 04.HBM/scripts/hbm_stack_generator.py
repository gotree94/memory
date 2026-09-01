# HBM 메모리 3D 적층 파라미터 제너레이터
# Virtuoso Parametric HBM Stack Generator
# HBM 세대별 TSV 적층, Base Die, 채널 구조 설계를 위한 파라미터 및 SKILL 코드 생성

import json
from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path
from enum import Enum


class StackingMethod(Enum):
    """HBM 적층 방식"""
    TSV_MICROBUMP = "tsv_microbump"
    TSV_ADVBUMP = "tsv_advbump"
    MR_MUF = "mr_muf"
    NCF = "ncf"


class ChannelArch(Enum):
    """HBM 채널 아키텍처"""
    SINGLE_1024 = "single_1024bit"        # HBM1
    PSEUDO_2X512 = "pseudo_2x512bit"      # HBM2
    MULTI_1024 = "multi_1024bit"          # HBM2E
    SIXTEEN_64 = "16x64bit"               # HBM3


@dataclass
class TechnologyNode:
    name: str
    node_nm: int
    vdd: float
    oxide_thickness: float  # nm


@dataclass
class HBMConfig:
    """HBM 스택 설계 파라미터"""
    generation: str
    tech_node: TechnologyNode
    stacking: StackingMethod
    channel_arch: ChannelArch
    # 적층 파라미터
    num_dies: int               # 스택 높이 (Hi)
    die_thickness: float        # μm
    tsv_diameter: float         # μm
    tsv_pitch: float            # μm
    tsv_per_die: int            # 다이당 TSV 수
    microbump_pitch: float      # μm
    # 채널
    num_channels: int
    bits_per_channel: int
    bus_width: int
    pseudo_channels_per_channel: int
    # I/O
    data_rate: float            # Gbps/pin
    bandwidth: float            # GB/s (스택당)
    # 용량
    capacity_per_die: float     # Gb
    total_capacity: float       # GB (스택당)
    # 패키징
    package: str
    interposer: str
    # 특징
    features: List[str] = field(default_factory=list)


# ============================================================
# HBM 세대별 설정
# ============================================================

HBM_CONFIGS = {
    "HBM1": HBMConfig(
        generation="HBM1",
        tech_node=TechnologyNode(
            name="HBM1 28nm", node_nm=28, vdd=1.0, oxide_thickness=2.0),
        stacking=StackingMethod.TSV_MICROBUMP,
        channel_arch=ChannelArch.SINGLE_1024,
        num_dies=4, die_thickness=50,
        tsv_diameter=10, tsv_pitch=40, tsv_per_die=5000, microbump_pitch=40,
        num_channels=8, bits_per_channel=128, bus_width=1024,
        pseudo_channels_per_channel=1,
        data_rate=1.0, bandwidth=128,
        capacity_per_die=4, total_capacity=1,
        package="2.5D Silicon Interposer", interposer="Silicon",
        features=["최초 3D 적층", "1024-bit 버스", "Base Die", "TSV+Microbump"]
    ),
    "HBM2": HBMConfig(
        generation="HBM2",
        tech_node=TechnologyNode(
            name="HBM2 20nm", node_nm=20, vdd=1.0, oxide_thickness=1.5),
        stacking=StackingMethod.TSV_MICROBUMP,
        channel_arch=ChannelArch.PSEUDO_2X512,
        num_dies=8, die_thickness=40,
        tsv_diameter=8, tsv_pitch=36, tsv_per_die=6000, microbump_pitch=36,
        num_channels=8, bits_per_channel=128, bus_width=1024,
        pseudo_channels_per_channel=2,
        data_rate=2.0, bandwidth=256,
        capacity_per_die=4, total_capacity=2,
        package="2.5D Interposer", interposer="Silicon",
        features=["Pseudo Channel", "8-Hi", "ECC", "Thermal Shield"]
    ),
    "HBM2E": HBMConfig(
        generation="HBM2E",
        tech_node=TechnologyNode(
            name="HBM2E 10nm", node_nm=10, vdd=0.95, oxide_thickness=1.2),
        stacking=StackingMethod.TSV_ADVBUMP,
        channel_arch=ChannelArch.MULTI_1024,
        num_dies=12, die_thickness=35,
        tsv_diameter=6, tsv_pitch=32, tsv_per_die=8000, microbump_pitch=32,
        num_channels=8, bits_per_channel=128, bus_width=1024,
        pseudo_channels_per_channel=2,
        data_rate=3.6, bandwidth=600,
        capacity_per_die=8, total_capacity=24,
        package="Advanced 2.5D", interposer="Silicon",
        features=["12-Hi", "고용량", "미세 범프", "AI 가속기"]
    ),
    "HBM3": HBMConfig(
        generation="HBM3",
        tech_node=TechnologyNode(
            name="HBM3 1α/EUV", node_nm=10, vdd=0.9, oxide_thickness=1.0),
        stacking=StackingMethod.NCF,
        channel_arch=ChannelArch.SIXTEEN_64,
        num_dies=16, die_thickness=30,
        tsv_diameter=5, tsv_pitch=28, tsv_per_die=10000, microbump_pitch=28,
        num_channels=16, bits_per_channel=64, bus_width=1024,
        pseudo_channels_per_channel=1,
        data_rate=6.4, bandwidth=1000,
        capacity_per_die=8, total_capacity=64,
        package="2.5D/3D Interposer", interposer="Silicon",
        features=["16채널", "ODECC", "16-Hi", "NCF 패키징"]
    ),
    "HBM3E": HBMConfig(
        generation="HBM3E",
        tech_node=TechnologyNode(
            name="HBM3E 1α/1β", node_nm=9, vdd=0.85, oxide_thickness=0.9),
        stacking=StackingMethod.MR_MUF,
        channel_arch=ChannelArch.SIXTEEN_64,
        num_dies=12, die_thickness=25,
        tsv_diameter=4, tsv_pitch=25, tsv_per_die=12000, microbump_pitch=25,
        num_channels=16, bits_per_channel=64, bus_width=1024,
        pseudo_channels_per_channel=1,
        data_rate=9.2, bandwidth=1200,
        capacity_per_die=16, total_capacity=48,
        package="Advanced 2.5D (MR-MUF)", interposer="Silicon",
        features=["MR-MUF", "방열 2.5배", "Custom Base Die", "1.2TB/s"]
    ),
}


# ============================================================
# SKILL 코드 생성
# ============================================================

def hbm_header(lib: str, cell: str) -> str:
    return f"""; ============================================================
; HBM 3D Stack Generator
; Library: {lib}
; Cell:    {cell}
; Auto-generated by HBM Design Automation Tool
; ============================================================

procedure(hbmCreate{cell}()
    let((cv ws tech
          dieW dieH dieTh
          tsvR tsvPitch tsvCols tsvRows
          chSel chX
          i j k))
"""


def generate_stack_layout(gen_name: str, cfg: HBMConfig, lib: str = "hbm_lib") -> str:
    """HBM 스택 어레이 생성"""
    cell_name = f"hbm_{gen_name.lower()}_stack"

    skill = hbm_header(lib, cell_name)

    # 대략적 다이 크기 (mm)
    dieW, dieH = 10.0, 8.0

    skill += f"""
        ; ========================================
        ; {gen_name} - {cfg.tech_node.name}
        ; ========================================
        ; 적층: {cfg.num_dies}-Hi
        ; 다이 두께: {cfg.die_thickness}μm
        ; TSV: 지름 {cfg.tsv_diameter}μm, 피치 {cfg.tsv_pitch}μm
        ; TSV 수: {cfg.tsv_per_die}/다이
        ; 채널: {cfg.num_channels}개 x {cfg.bits_per_channel}-bit
        ; 버스: {cfg.bus_width}-bit
        ; 대역폭: {cfg.bandwidth} GB/s
        ; 용량: {cfg.total_capacity} GB (스택당)
        ; 패키징: {cfg.package}

        ; ┌─────────────────────────────┐
        ; │  Die n (Core)              │
        ; │   ┌───────────────┐        │
        ; │   │ 1T1C Cell     │  TSV   │
        ; │   │ Array         │●●●    │
        ; │   └───────────────┘        │
        ; └─────────────────────────────┘
        ;            ⋮ (N-Hi 적층)
        ; ┌─────────────────────────────┐
        ; │  Base Die (Logic/Buffer)   │
        ; │  PHY + Controller + TSV    │
        ; └─────────────────────────────┘
        ;      ↓ microbump
        ;   [Silicon Interposer]
        ;      ↓ RDL
        ;   [Package Substrate]
    """

    # Core Die 배치 (각 다이별)
    skill += f"""
        ; ── Core Die 어레이 배치 ──
        dieW = {dieW};  dieH = {dieH}
        for(i 0 ({cfg.num_dies}-1)
            ; 다이 영역 (수평 배치로 표현. 실제는 수직 적층)
            dy = i * (dieH + 0.5)
            dbCreateRect(cv list("M1" "drawing")
                list(0.0 dy dieW (+ dy dieH)))

            ; 다이 라벨
            dbCreateText(cv sprintf(nil "Core_Die_%02d" i)
                list(0.5 (+ dy 0.8)) "M1" 0.6 "centerLeft")

            ; TSV 어레이 배치 (모든 다이 공통 위치)
            tsvCols = {cfg.tsv_per_die // 100}
            for(col 0 tsvCols-1,
                tsvX = 1.0 + col * 0.5
                for(row 0 99,
                    tsvY = dy + 1.5 + row * 0.05
                    ; TSV 원근사 사각형
                    dbCreateCircle(cv list("M3" "drawing")
                        tsvX tsvY {cfg.tsv_diameter/1000})
                )
            )
        )
    """

    # Base Die 배치
    skill += f"""
        ; ── Base Die (로직) ──
        baseDY = {cfg.num_dies} * (dieH + 0.5)
        dbCreateRect(cv list("M4" "drawing")
            list(0.0 baseDY dieW (+ baseDY dieH)))

        dbCreateText(cv "Base_Die (Logic/Buffer)"
            list(0.5 (+ baseDY 0.8)) "M4" 0.6 "centerLeft")
        dbCreateText(cv "PHY"
            list(1.0 (+ baseDY 2.0)) "M4" 0.4 "centerLeft")
        dbCreateText(cv "Controller"
            list(1.0 (+ baseDY 3.0)) "M4" 0.4 "centerLeft")

        ; 채널 분할
        chW = dieW / {cfg.num_channels}
        for(ch 0 ({cfg.num_channels}-1)
            dbCreateText(cv sprintf(nil "CH%02d_%dbit" ch {cfg.bits_per_channel})
                list(+ (* ch chW) 0.5) (+ baseDY 1.0)
                "M4" 0.3 "centerLeft")
        )
    """

    # 채널 아키텍처별 라벨
    if cfg.channel_arch == ChannelArch.PSEUDO_2X512:
        skill += f"""
        ; Pseudo Channel (2x512-bit)
        dbCreateText(cv "PseudoCH_0: 512-bit"
            list(1.0 (+ baseDY 5.0)) "M4" 0.3 "centerLeft")
        dbCreateText(cv "PseudoCH_1: 512-bit"
            list(1.0 (+ baseDY 5.5)) "M4" 0.3 "centerLeft")
        """
    elif cfg.channel_arch == ChannelArch.SIXTEEN_64:
        skill += f"""
        ; 16개 독립 채널 (채널당 64-bit)
        dbCreateText(cv "16 x 64-bit = 1024-bit"
            list(1.0 (+ baseDY 5.0)) "M4" 0.3 "centerLeft")
        """

    # ECC 표시
    if "ODECC" in cfg.features or "On-Die ECC" in cfg.features:
        skill += """
        dbCreateText(cv "On-Die ECC (ODECC)"
            list(1.0 (+ baseDY 6.0)) "M4" 0.3 "centerLeft")
        """

    # 패키징 표시
    skill += f"""
        ; ── 패키징 구조 ──
        pkgDY = ({cfg.num_dies}+1) * (dieH + 0.5)
        dbCreateText(cv "{cfg.package}"
            list(0.5 (+ pkgDY 2.0)) "M2" 0.5 "centerLeft")
        dbCreateText(cv "TSV x {cfg.tsv_per_die}/die"
            list(0.5 (+ pkgDY 2.6)) "M2" 0.3 "centerLeft")
        dbCreateText(cv "Microbump pitch {cfg.microbump_pitch}μm"
            list(0.5 (+ pkgDY 3.2)) "M2" 0.3 "centerLeft")

        when(cv,
            dbSave(cv)
            println("{gen_name} stack layout generated")
        )
    )
endprocedure
"""
    return skill


def generate_base_die(gen_name: str, cfg: HBMConfig, lib: str = "hbm_lib") -> str:
    """Base Die (로직) 회로 생성"""
    cell_name = f"hbm_{gen_name.lower()}_base_die"

    skill = hbm_header(lib, cell_name)

    skill += f"""
        ; ========================================
        ; {gen_name} Base Die (Logic/Buffer)
        ; ========================================
        ; 역할:
        ;  1. PHY 인터페이스 (DRAM ↔ Host)
        ;  2. 메모리 컨트롤러 인터페이스
        ;  3. TSV 신호 완충 (Buffer)
        ;  4. 전력 관리
        ; 채널: {cfg.num_channels}개
        ; 버스: {cfg.bus_width}-bit

        ; 블록 배치
        ; ┌─────────────────────────────┐
        ; │  [PHY]   [Controller]       │
        ; │  [TSV Buffer]  [Power Mgt]  │
        ; └─────────────────────────────┘

        ; PHY 블록
        dbCreateRect(cv list("M1" "drawing") list(0.5 6.0 4.0 8.0))
        dbCreateText(cv "PHY" list(1.0 7.5) "M1" 0.4 "centerLeft")
        dbCreateText(cv sprintf(nil "DQ[0:%d]" {cfg.bus_width-1})
            list(1.0 7.0) "M1" 0.3 "centerLeft")

        ; Controller 블록
        dbCreateRect(cv list("M1" "drawing") list(4.5 6.0 8.0 8.0))
        dbCreateText(cv "Controller" list(5.0 7.5) "M1" 0.4 "centerLeft")

        ; TSV Buffer 블록
        dbCreateRect(cv list("M2" "drawing") list(0.5 3.0 8.0 5.0))
        dbCreateText(cv "TSV_Buffer" list(1.0 4.5) "M2" 0.4 "centerLeft")
        dbCreateText(cv sprintf(nil "TSV x %d" {cfg.tsv_per_die})
            list(1.0 4.0) "M2" 0.3 "centerLeft")

        ; Power Management 블록
        dbCreateRect(cv list("M3" "drawing") list(0.5 0.5 8.0 2.5))
        dbCreateText(cv "Power_Mgmt" list(1.0 2.0) "M3" 0.4 "centerLeft")
        dbCreateText(cv sprintf(nil "VDD %.2fV" {cfg.tech_node.vdd})
            list(1.0 1.5) "M3" 0.3 "centerLeft")

        when(cv,
            dbSave(cv)
        )
    )
endprocedure
"""
    return skill


def generate_tsv_layout(gen_name: str, cfg: HBMConfig, lib: str = "hbm_lib") -> str:
    """TSV 어레이 레이아웃 생성"""
    cell_name = f"hbm_{gen_name.lower()}_tsv"

    skill = hbm_header(lib, cell_name)

    skill += f"""
        ; ========================================
        ; {gen_name} TSV Array
        ; ========================================
        ; TSV 지름: {cfg.tsv_diameter}μm
        ; TSV 피치: {cfg.tsv_pitch}μm
        ; TSV 개수: {cfg.tsv_per_die}/다이
        ; 다이 두께: {cfg.die_thickness}μm

        ; TSV 좌표 계산
        tsvD = {cfg.tsv_diameter}
        tsvPitch = {cfg.tsv_pitch}
        tsvPerRow = 100
        tsvRows = {cfg.tsv_per_die} / tsvPerRow

        ; TSV 배치 (정사각 어레이)
        for(row 0 tsvRows-1,
            for(col 0 tsvPerRow-1,
                x = col * tsvPitch
                y = row * tsvPitch
                ; TSV 홀 생성
                dbCreateCircle(cv list("TSV" "drawing")
                    x y (tsvD / 2))
            )
        )

        ; TSV 신호 분류
        dbCreateText(cv "Signal_TSV" list(1.0 (+ (* tsvRows tsvPitch) 1.0))
            "M3" 0.3 "centerLeft")
        dbCreateText(cv "Power_TSV" list(1.0 (+ (* tsvRows tsvPitch) 2.0))
            "M4" 0.3 "centerLeft")
        dbCreateText(cv "GND_TSV" list(1.0 (+ (* tsvRows tsvPitch) 3.0))
            "M4" 0.3 "centerLeft")

        when(cv,
            dbSave(cv)
        )
    )
endprocedure
"""
    return skill


def generate_python_config() -> str:
    """HBM 설정 JSON 생성"""
    data = []
    for gen, cfg in HBM_CONFIGS.items():
        data.append({
            "generation": cfg.generation,
            "tech": cfg.tech_node.name,
            "node_nm": cfg.tech_node.node_nm,
            "vdd_V": cfg.tech_node.vdd,
            "stacking": cfg.stacking.value,
            "channel_arch": cfg.channel_arch.value,
            "num_dies_hi": cfg.num_dies,
            "die_thickness_um": cfg.die_thickness,
            "tsv_diameter_um": cfg.tsv_diameter,
            "tsv_pitch_um": cfg.tsv_pitch,
            "tsv_per_die": cfg.tsv_per_die,
            "microbump_pitch_um": cfg.microbump_pitch,
            "num_channels": cfg.num_channels,
            "bits_per_channel": cfg.bits_per_channel,
            "bus_width": cfg.bus_width,
            "pseudo_channels_per_channel": cfg.pseudo_channels_per_channel,
            "data_rate_Gbps_per_pin": cfg.data_rate,
            "bandwidth_GB_s": cfg.bandwidth,
            "capacity_per_die_Gb": cfg.capacity_per_die,
            "total_capacity_GB": cfg.total_capacity,
            "package": cfg.package,
            "interposer": cfg.interposer,
            "features": cfg.features,
        })
    return json.dumps(data, indent=2, ensure_ascii=False)


def main():
    output_dir = Path(__file__).parent / "generated"
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("HBM 3D Stack Design Automation Tool")
    print("=" * 60)

    for gen_name, cfg in HBM_CONFIGS.items():
        print(f"\n[{gen_name}] Generating...")

        (output_dir / f"hbm_{gen_name.lower()}_stack.skill").write_text(
            generate_stack_layout(gen_name, cfg), encoding='utf-8')
        print(f"  Generated: stack layout skill")

        (output_dir / f"hbm_{gen_name.lower()}_base_die.skill").write_text(
            generate_base_die(gen_name, cfg), encoding='utf-8')
        print(f"  Generated: base die skill")

        (output_dir / f"hbm_{gen_name.lower()}_tsv.skill").write_text(
            generate_tsv_layout(gen_name, cfg), encoding='utf-8')
        print(f"  Generated: TSV layout skill")

        print(f"  {cfg.num_dies}-Hi, {cfg.num_channels}ch, "
              f"{cfg.bandwidth}GB/s, {cfg.total_capacity}GB")

    # 설정 JSON
    (output_dir / "hbm_configs.json").write_text(
        generate_python_config(), encoding='utf-8')
    print("\n[Common] Generated: hbm_configs.json")

    print("\n" + "=" * 60)
    print(f"All files in: {output_dir}")
    print("=" * 60)

    # 요약
    print("\n[Summary]")
    print("-" * 95)
    print(f"{'Gen':<7} {'Tech':<10} {'Stack':<7} {'Ch':<4} {'Rate':<7} {'BW(GB/s)':<10} {'Cap(GB)':<8} {'Pkg':<25}")
    print("-" * 95)
    for gen, cfg in HBM_CONFIGS.items():
        print(f"{gen:<7} {cfg.tech_node.name:<10} {cfg.num_dies}-Hi  "
              f"{cfg.num_channels:<4} {cfg.data_rate:<7} {cfg.bandwidth:<10} "
              f"{cfg.total_capacity:<8} {cfg.package:<25}")
    print("-" * 95)


if __name__ == "__main__":
    main()
