# DRAM / SDRAM 셀 파라미터 제너레이터
# Virtuoso Parametric DRAM Cell Generator
# DRAM 세대별 1T1C 셀 설계를 위한 파라미터 및 SKILL 코드 생성

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path
from enum import Enum


class CapacitorType(Enum):
    """커패시터 타입"""
    PLANAR = "planar"                    # 평면 커패시터 (1세대)
    TRENCH = "trench"                    # 트렌치 커패시터 (EDO)
    STACKED_CYLINDER = "stacked_cylinder" # 스택 실린더 (SDRAM~DDR2)
    MIM = "mim"                          # MIM 커패시터 (DDR2~DDR3)
    BCAT = "bcat"                        # 매립형 채널 트랜지스터 (DDR3~DDR4)
    BCAT_HAR = "bcat_har"               # HAR BCAT (DDR4~DDR5)
    VCT = "vct"                          # 수직 채널 트랜지스터 (차세대)
    PILLAR = "pillar"                    # 필러 커패시터 (DDR5)


@dataclass
class TechnologyNode:
    """기술 노드 정의"""
    name: str
    node_nm: int
    gate_length: float  # nm
    min_pitch: float    # nm
    vdd: float          # V
    vth: float          # V
    oxide_thickness: float  # nm (EOT)


@dataclass
class DRAMCellConfig:
    """DRAM 1T1C 셀 설계 파라미터"""
    generation: str                     # 세대 (SDRAM, DDR, DDR2, etc.)
    tech_node: TechnologyNode
    capacitor_type: CapacitorType
    # 트랜지스터 파라미터
    gate_length: float                  # nm (가둠 길이)
    gate_width: float                   # nm (채널 폭)
    # 커패시터 파라미터
    cap_value: float                    # fF (커패시턴스)
    cap_height: float                   # nm (적층 높이)
    cap_diameter: float                 # nm (직경)
    aspect_ratio: float                 # 종횡비
    # 레이아웃 파라미터
    cell_height: float                  # nm
    cell_width: float                   # nm
    # 전기적 파라미터
    vref: float                         # V (참조 전압)
    sense_margin: float                 # mV (센스 마진)
    refresh_time: float                 # ms (리프레시 주기)
    tRCD: float                         # ns (RAS-to-CAS delay)
    tCAS: float                         # ns (CAS latency)
    tRP: float                          # ns (Row Precharge time)
    data_rate: float                    # MT/s (데이터 레이트)
    bandwidth: float                    # GB/s (대역폭)
    # 패키징
    package: str
    # 기술 특징
    features: List[str] = field(default_factory=list)


# ============================================================
# 기술 노드 정의
# ============================================================

TECH_NODES = {
    "gen1_8um": TechnologyNode(
        name="1세대 8μm", node_nm=8000, gate_length=8000,
        min_pitch=8000, vdd=5.0, vth=0.8, oxide_thickness=50
    ),
    "gen_edo_600nm": TechnologyNode(
        name="EDO 600nm", node_nm=600, gate_length=600,
        min_pitch=600, vdd=3.3, vth=0.6, oxide_thickness=10
    ),
    "sdram_350nm": TechnologyNode(
        name="SDRAM 350nm", node_nm=350, gate_length=350,
        min_pitch=400, vdd=3.3, vth=0.5, oxide_thickness=8
    ),
    "ddr_180nm": TechnologyNode(
        name="DDR 180nm", node_nm=180, gate_length=180,
        min_pitch=200, vdd=2.5, vth=0.45, oxide_thickness=5
    ),
    "ddr2_90nm": TechnologyNode(
        name="DDR2 90nm", node_nm=90, gate_length=90,
        min_pitch=100, vdd=1.8, vth=0.4, oxide_thickness=3
    ),
    "ddr3_65nm": TechnologyNode(
        name="DDR3 65nm", node_nm=65, gate_length=65,
        min_pitch=80, vdd=1.5, vth=0.35, oxide_thickness=2.5
    ),
    "ddr4_30nm": TechnologyNode(
        name="DDR4 30nm", node_nm=30, gate_length=30,
        min_pitch=40, vdd=1.2, vth=0.3, oxide_thickness=1.5
    ),
    "ddr5_14nm": TechnologyNode(
        name="DDR5 14nm", node_nm=14, gate_length=14,
        min_pitch=24, vdd=1.1, vth=0.25, oxide_thickness=1.0
    ),
}


def create_dram_cell_configs() -> List[DRAMCellConfig]:
    """DRAM 셀 파라미터 생성 (세대별)"""
    configs = []

    # 1세대 DRAM: Planar Capacitor
    configs.append(DRAMCellConfig(
        generation="1세대 DRAM",
        tech_node=TECH_NODES["gen1_8um"],
        capacitor_type=CapacitorType.PLANAR,
        gate_length=8000, gate_width=8000,
        cap_value=50, cap_height=0, cap_diameter=4000, aspect_ratio=1,
        cell_height=16000, cell_width=8000,
        vref=2.5, sense_margin=800, refresh_time=4,
        tRCD=100, tCAS=100, tRP=100, data_rate=0, bandwidth=0,
        package="DIP",
        features=["비동기식", "평면 커패시터", "1T1C 기본 구조"]
    ))

    # EDO DRAM: Early Trench/Stacked
    configs.append(DRAMCellConfig(
        generation="EDO DRAM",
        tech_node=TECH_NODES["gen_edo_600nm"],
        capacitor_type=CapacitorType.TRENCH,
        gate_length=600, gate_width=600,
        cap_value=30, cap_height=2000, cap_diameter=400, aspect_ratio=5,
        cell_height=2400, cell_width=1200,
        vref=1.65, sense_margin=500, refresh_time=4,
        tRCD=40, tCAS=40, tRP=40, data_rate=0, bandwidth=0,
        package="SIMM, DIP",
        features=["EDO 출력 유지", "초기 입체 커패시터"]
    ))

    # SDRAM: Stacked Cylinder
    configs.append(DRAMCellConfig(
        generation="SDRAM",
        tech_node=TECH_NODES["sdram_350nm"],
        capacitor_type=CapacitorType.STACKED_CYLINDER,
        gate_length=350, gate_width=350,
        cap_value=25, cap_height=3000, cap_diameter=200, aspect_ratio=15,
        cell_height=1400, cell_width=700,
        vref=1.65, sense_margin=350, refresh_time=64,
        tRCD=15, tCAS=15, tRP=15, data_rate=133, bandwidth=1.06,
        package="DIMM, SIMM",
        features=["동기식", "실린더형 커패시터", "파이프라인 동작"]
    ))

    # DDR: Advanced Stacked MIM
    configs.append(DRAMCellConfig(
        generation="DDR (DDR1)",
        tech_node=TECH_NODES["ddr_180nm"],
        capacitor_type=CapacitorType.MIM,
        gate_length=180, gate_width=180,
        cap_value=20, cap_height=4000, cap_diameter=150, aspect_ratio=25,
        cell_height=700, cell_width=350,
        vref=1.25, sense_margin=250, refresh_time=64,
        tRCD=10, tCAS=10, tRP=10, data_rate=266, bandwidth=2.1,
        package="DIMM (184핀)",
        features=["DDR (양에지 전송)", "MIM 커패시터", "2n-prefetch"]
    ))

    # DDR2: MIM Capacitor
    configs.append(DRAMCellConfig(
        generation="DDR2",
        tech_node=TECH_NODES["ddr2_90nm"],
        capacitor_type=CapacitorType.MIM,
        gate_length=90, gate_width=90,
        cap_value=15, cap_height=5000, cap_diameter=120, aspect_ratio=40,
        cell_height=350, cell_width=175,
        vref=0.9, sense_margin=180, refresh_time=64,
        tRCD=5, tCAS=5, tRP=5, data_rate=667, bandwidth=5.3,
        package="DIMM (240핀)",
        features=["4n-prefetch", "ODT", "Fly-by 구조"]
    ))

    # DDR3: BCAT
    configs.append(DRAMCellConfig(
        generation="DDR3",
        tech_node=TECH_NODES["ddr3_65nm"],
        capacitor_type=CapacitorType.BCAT,
        gate_length=65, gate_width=65,
        cap_value=12, cap_height=6000, cap_diameter=100, aspect_ratio=60,
        cell_height=260, cell_width=130,
        vref=0.75, sense_margin=140, refresh_time=64,
        tRCD=3.5, tCAS=3.5, tRP=3.5, data_rate=1600, bandwidth=12.8,
        package="DIMM (240핀)",
        features=["8n-prefetch", "BCAT 매립형 채널", "ZQ Calibration"]
    ))

    # DDR4: BCAT + HAR
    configs.append(DRAMCellConfig(
        generation="DDR4",
        tech_node=TECH_NODES["ddr4_30nm"],
        capacitor_type=CapacitorType.BCAT_HAR,
        gate_length=30, gate_width=30,
        cap_value=10, cap_height=8000, cap_diameter=80, aspect_ratio=100,
        cell_height=120, cell_width=60,
        vref=0.6, sense_margin=100, refresh_time=64,
        tRCD=2.5, tCAS=2.5, tRP=2.5, data_rate=3200, bandwidth=25.6,
        package="DIMM (288핀)",
        features=["Bank Group", "VDDQ 독립 전원", "CRC/Parity"]
    ))

    # DDR5: Ultra-HAR Pillar + EUV
    configs.append(DRAMCellConfig(
        generation="DDR5",
        tech_node=TECH_NODES["ddr5_14nm"],
        capacitor_type=CapacitorType.PILLAR,
        gate_length=14, gate_width=14,
        cap_value=8, cap_height=10000, cap_diameter=60, aspect_ratio=160,
        cell_height=56, cell_width=28,
        vref=0.55, sense_margin=80, refresh_time=32,
        tRCD=1.75, tCAS=1.75, tRP=1.75, data_rate=6400, bandwidth=51.2,
        package="DIMM (288핀), SO-DIMM (262핀)",
        features=["16n-prefetch", "On-die ECC", "PMIC 내장", "Dual 32-bit subchannel"]
    ))

    return configs


# ============================================================
# SKILL 코드 생성 함수들
# ============================================================

def generate_dram_skill_header(lib_name: str, cell_name: str) -> str:
    """DRAM SKILL 스크립트 헤더"""
    return f"""; ============================================================
; DRAM 1T1C Cell Layout Generator
; Library: {lib_name}
; Cell:    {cell_name}
; View:    layout
; Auto-generated by DRAM Design Automation Tool
; ============================================================

procedure(dramCreate{cell_name}()
    let((cv ws tech cellBox
          gateL gateW capD capH capAR
          cellH cellW
          m1Width m2Width m3Width
          polyWidth))

        ; 라이브러리 및 셀 생성
        when(geCreateCell(nil "{lib_name}" "{cell_name}" "layout" "layout")
            sprintf(msg "Created cell: %s/%s/%s" "{lib_name}" "{cell_name}" "layout")
            println(msg)
        )

        cv = dbOpenCellViewByType("{lib_name}" "{cell_name}" "layout" "" "a")
"""


def generate_planar_dram(config: DRAMCellConfig, lib_name: str = "dram_lib") -> str:
    """1세대 Planar DRAM 셀 생성"""
    cell_name = f"dram_planar_{config.tech_node.node_nm}nm"

    skill = generate_dram_skill_header(lib_name, cell_name)

    skill += f"""
        ; ========================================
        ; 1T1C Planar DRAM Cell - {config.generation}
        ; ========================================
        ; Cell Size: {config.cell_height}nm x {config.cell_width}nm
        ; VDD: {config.tech_node.vdd}V
        ; Cap: {config.cap_value}fF (Planar)

        ; --- 셀 구조 ---
        ;     Wordline (WL)
        ;          |
        ;     ┌────┴────┐
        ;     │ Access   │
        ;     │ Transistor│
        ;     └────┬────┘
        ;          |
        ;     Bitline (BL)
        ;          |
        ;     ┌────┴────┐
        ;     │ Storage  │
        ;     │Capacitor │
        ;     └────┬────┘
        ;          |
        ;        VSS

        ; --- 1T1C 스케마틱 ---
        ; BL ----[Access NMOS]----+---- Storage Cap ---- VSS
        ;                          |
        ;                         WL

        ; 평면 커패시터 (Planar Capacitor)
        ; 트랜지스터와 동일 평면에 배치
        ; 면적이 넓어 밀도가 낮음

        println("Planar DRAM cell layout generation completed")
    )

    skill += """
        when(cv,
            dbSave(cv)
            println("Layout saved successfully")
        )
    )
endprocedure
"""
    return skill


def generate_stacked_dram(config: DRAMCellConfig, lib_name: str = "dram_lib") -> str:
    """Stacked Cylinder DRAM 셀 생성"""
    cell_name = f"dram_stacked_{config.tech_node.node_nm}nm"

    skill = generate_dram_skill_header(lib_name, cell_name)

    skill += f"""
        ; ========================================
        ; 1T1C Stacked Cylinder DRAM Cell - {config.generation}
        ; ========================================
        ; Cell Size: {config.cell_height}nm x {config.cell_width}nm
        ; VDD: {config.tech_node.vdd}V
        ; Cap: {config.cap_value}fF (Stacked Cylinder)
        ; Cap Height: {config.cap_height}nm
        ; Cap Diameter: {config.cap_diameter}nm
        ; Aspect Ratio: {config.aspect_ratio}:1

        ; --- 셀 구조 ---
        ;        ┌─────────────┐
        ;        │  Stacked     │
        ;        │  Cylinder    │ ← 커패시터 (위쪽 적층)
        ;        │  Capacitor   │
        ;        └──────┬──────┘
        ;               │
        ;     Wordline ──┤
        ;               │
        ;        ┌──────┴──────┐
        ;        │   Access     │
        ;        │  Transistor  │ ← 트랜지스터 (기판)
        ;        └──────┬──────┘
        ;               │
        ;           Bitline

        ; --- 3D 구조 ---
        ; 기판 상단에 실린더형 커패시터를 수직으로 적층
        ; 평면 면적을 줄이고 커패시턴스 확보

        println("Stacked Cylinder DRAM cell layout generation completed")
    )

    skill += """
        when(cv,
            dbSave(cv)
            println("Layout saved successfully")
        )
    )
endprocedure
"""
    return skill


def generate_bcat_dram(config: DRAMCellConfig, lib_name: str = "dram_lib") -> str:
    """BCAT (Buried Channel Array Transistor) DRAM 셀 생성"""
    cell_name = f"dram_bcat_{config.tech_node.node_nm}nm"

    skill = generate_dram_skill_header(lib_name, cell_name)

    skill += f"""
        ; ========================================
        ; 1T1C BCAT DRAM Cell - {config.generation}
        ; ========================================
        ; Cell Size: {config.cell_height}nm x {config.cell_width}nm
        ; VDD: {config.tech_node.vdd}V
        ; Cap: {config.cap_value}fF (HAR Stacked)
        ; Cap Height: {config.cap_height}nm
        ; Aspect Ratio: {config.aspect_ratio}:1

        ; --- BCAT 구조 ---
        ;        ┌─────────────┐
        ;        │  HAR Cap     │ ← High Aspect Ratio 커패시터
        ;        │  (Stacked)   │    종횡비 {config.aspect_ratio}:1
        ;        └──────┬──────┘
        ;               │
        ;     Bitline ──┤
        ;               │
        ;     ┌─────────┴─────────┐
        ;     │  Buried Channel    │ ← 기판 내부 매립형 채널
        ;     │  Array Transistor  │    BCAT 트랜지스터
        ;     └─────────┬─────────┘
        ;               │
        ;     Wordline ──┘

        ; --- BCAT 장점 ---
        ; 1. 단채널 효과(Short Channel Effect) 극복
        ; 2. 실질적 채널 길이 연장
        ; 3. 셀 면적 증가 없이 누설 전류 감소

        ; --- HAR 커패시터 ---
        ; 비트라인 상부에 종횡비 30:1 이상의
        ; 높고 가느다란 스택 커패시터 형성

        println("BCAT DRAM cell layout generation completed")
    )

    skill += """
        when(cv,
            dbSave(cv)
            println("Layout saved successfully")
        )
    )
endprocedure
"""
    return skill


def generate_pillar_dram(config: DRAMCellConfig, lib_name: str = "dram_lib") -> str:
    """Ultra-HAR Pillar DRAM 셀 생성 (DDR5)"""
    cell_name = f"dram_pillar_{config.tech_node.node_nm}nm"

    skill = generate_dram_skill_header(lib_name, cell_name)

    skill += f"""
        ; ========================================
        ; 1T1C Pillar DRAM Cell - {config.generation}
        ; ========================================
        ; Cell Size: {config.cell_height}nm x {config.cell_width}nm
        ; VDD: {config.tech_node.vdd}V
        ; Cap: {config.cap_value}fF (Pillar)
        ; Cap Height: {config.cap_height}nm
        ; Aspect Ratio: {config.aspect_ratio}:1

        ; --- Pillar 구조 ---
        ;        ┌─────────────┐
        ;        │  Pillar Cap  │ ← 초고종횡비 필러 커패시터
        ;        │  (Ultra HAR) │    종횡비 {config.aspect_ratio}:1
        ;        │  EUV Pattern │    EUV 리소그래피 적용
        ;        └──────┬──────┘
        ;               │
        ;     Bitline ──┤
        ;               │
        ;     ┌─────────┴─────────┐
        ;     │  VCT (Vertical     │ ← 수직 채널 트랜지스터
        ;     │  Channel Trans.)   │    차세대 DRAM 구조
        ;     └─────────┬─────────┘
        ;               │
        ;     Wordline ──┘

        ; --- DDR5 특징 ---
        ; 1. EUV 리소그래피로 초미세 패턴 작성
        ; 2. VCT(수직 채널 트랜지스터) 적용
        ; 3. Ultra-HAR 커패시터로 극미세 면적에서도 Cap 확보
        ; 4. On-die ECC로 데이터 무결성 보장

        println("Pillar DRAM cell layout generation completed")
    )

    skill += """
        when(cv,
            dbSave(cv)
            println("Layout saved successfully")
        )
    )
endprocedure
"""
    return skill


def generate_dram_array_generator(lib_name: str = "dram_lib") -> str:
    """DRAM 어레이 생성 SKILL 코드"""
    return f"""; ============================================================
; DRAM Array Generator
; DRAM 메모리 어레이 자동 생성
; ============================================================

procedure(dramCreateArray(
    libName       ; 라이브러리 이름
    cellName      ; 셀 이름 (예: "dram_bcat_65nm")
    viewName      ; 뷰 이름 (예: "layout")
    numRows       ; 행 수 (월드 수)
    numCols       ; 열 수 (비트 라인 수)
    bankCount     ; 뱅크 수
)
    let((cv cvArray rows cols colIdx rowIdx
           cellW cellH x y objList wl bl vdd vss)

        ; 셀 디멘션 확인
        cv = dbOpenCellViewByType(libName cellName viewName "" "a")
        when(nil == cv,
            printf("Error: Cell %s not found\\n" cellName)
            return(nil)
        )

        ; 어레이 크기 계산
        rows = numRows
        cols = numCols

        ; 어레이 셀 뷰 생성
        arrayName = sprintf(nil "%s_array_%dx%d_%dbank" cellName rows cols bankCount)
        when(geCreateCell(libName arrayName viewName "layout" "layout"),
            cvArray = dbOpenCellViewByType(libName arrayName viewName "" "a")
        )

        ; ========================================
        ; 각 뱅크별 어레이 생성
        ; ========================================
        for(bank 0 bankCount-1,
            bankOffset = bank * cols * cellW * 1.5  ; 뱅크 간 간격

            ; 셀 배치 루프
            for(i 0 rows-1,
                for(j 0 cols-1,
                    x = bankOffset + j * cellW
                    y = i * cellH
                    ; 셀 인스턴스 배치
                    dbCreateInst(cvArray cv cellName
                        sprintf(nil "DRAM_B%02d_%02d_%02d" bank i j)
                        x y "R0")
                )
            )

            ; Wordline 배선 자동 생성
            for(i 0 rows-1,
                y = i * cellH + cellH/2
                ; Metal2 Wordline
                dbCreatePath(cvArray
                    list(bankOffset y (+ bankOffset (* cols cellW)) y)
                    "M2" 0.08
                    list(0 0 (* cols cellW) (* rows cellH)))
            )

            ; Bitline 배선 자동 생성
            for(j 0 cols-1,
                x = bankOffset + j * cellW + cellW/2
                ; Metal3 Bitline
                dbCreatePath(cvArray
                    list(x 0 x (* rows cellH))
                    "M3" 0.06
                    list(0 0 (* cols cellW) (* rows cellH)))
            )

            ; 뱅크 라벨
            dbCreateText(cvArray
                sprintf(nil "BANK_%02d" bank)
                list(bankOffset (- 0.3))
                "M1" 0.1 "centerCenter")
        )

        ; ========================================
        ; 공통 배선 (Global Wordline, Global Bitline)
        ; ========================================

        ; VDD rail
        for(i 0 rows-1,
            y = i * cellH
            dbCreatePath(cvArray
                list((- 0.1) y (+ (* bankCount cols cellW) 0.1) y)
                "M1" 0.1
                list(0 0 (* bankCount cols cellW 1.5) (* rows cellH)))
        )

        ; VSS rail
        for(i 0 rows-1,
            y = i * cellH + cellH * 0.8
            dbCreatePath(cvArray
                list((- 0.1) y (+ (* bankCount cols cellW) 0.1) y)
                "M1" 0.1
                list(0 0 (* bankCount cols cellW 1.5) (* rows cellH)))
        )

        ; 결과 저장
        dbSave(cvArray)
        printf("DRAM Array created: %s\\n" arrayName)
        printf("  Rows: %d, Cols: %d, Banks: %d\\n" rows cols bankCount)
        printf("  Total Capacity: %d bits\\n" (* rows cols bankCount))
    )
    return(cvArray)
endprocedure


; ============================================================
; DRAM 타이밍 분석
; ============================================================

procedure(dramAnalyzeTiming(
    libName
    cellName
)
    let((cv cellBox w h)

        cv = dbOpenCellViewByType(libName cellName "layout" "" "a")
        cellBox = dbGetCellBox(cv)

        w = xCoord(car(cdr(cellBox))) - xCoord(car(cellBox))
        h = yCoord(cdr(cellBox)) - yCoord(car(cellBox))

        printf("DRAM Cell Analysis: %s\\n" cellName)
        printf("  Width:  %.3f um\\n" w)
        printf("  Height: %.3f um\\n" h)
        printf("  Area: %.6f um^2\\n" (* w h))
        printf("  Cell Density: %.2f Mbit/cm^2\\n"
            (/ 1e8 (* w h)))

        return(list(w h))
    )
endprocedure
"""


def generate_python_config(configs: List[DRAMCellConfig], output_dir: str) -> str:
    """Python 설정 파일 생성"""
    config_dict = []
    for c in configs:
        config_dict.append({
            "generation": c.generation,
            "tech_node": c.tech_node.name,
            "node_nm": c.tech_node.node_nm,
            "vdd": c.tech_node.vdd,
            "capacitor_type": c.capacitor_type.value,
            "gate_length_nm": c.gate_length,
            "cap_value_fF": c.cap_value,
            "cap_height_nm": c.cap_height,
            "aspect_ratio": c.aspect_ratio,
            "cell_height_nm": c.cell_height,
            "cell_width_nm": c.cell_width,
            "cell_area_um2": (c.cell_height * c.cell_width) / 1e6,
            "vref_V": c.vref,
            "sense_margin_mV": c.sense_margin,
            "refresh_time_ms": c.refresh_time,
            "tRCD_ns": c.tRCD,
            "tCAS_ns": c.tCAS,
            "tRP_ns": c.tRP,
            "data_rate_MTs": c.data_rate,
            "bandwidth_GB_s": c.bandwidth,
            "package": c.package,
            "features": c.features,
        })

    return json.dumps(config_dict, indent=2, ensure_ascii=False)


# ============================================================
# 메인 실행
# ============================================================

def main():
    """DRAM 셀 파라미터 생성 및 SKILL 코드 출력"""
    output_dir = Path(__file__).parent / "generated"
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("DRAM 1T1C Cell Design Automation Tool")
    print("=" * 60)

    configs = create_dram_cell_configs()

    # 각 커패시터 타입별 SKILL 코드 생성
    print("\n[1] DRAM Cell Generation...")
    for config in configs:
        if config.capacitor_type == CapacitorType.PLANAR:
            skill_code = generate_planar_dram(config)
        elif config.capacitor_type in [CapacitorType.TRENCH, CapacitorType.STACKED_CYLINDER, CapacitorType.MIM]:
            skill_code = generate_stacked_dram(config)
        elif config.capacitor_type in [CapacitorType.BCAT, CapacitorType.BCAT_HAR]:
            skill_code = generate_bcat_dram(config)
        elif config.capacitor_type in [CapacitorType.PILLAR, CapacitorType.VCT]:
            skill_code = generate_pillar_dram(config)
        else:
            skill_code = generate_stacked_dram(config)

        filename = f"dram_{config.capacitor_type.value}_{config.tech_node.node_nm}nm.skill"
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(skill_code)
        print(f"  Generated: {filename}")

    # 어레이 생성 스크립트
    print("\n[2] DRAM Array Generator...")
    array_skill = generate_dram_array_generator()
    filepath = output_dir / "dram_array_generator.skill"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(array_skill)
    print(f"  Generated: dram_array_generator.skill")

    # Python 설정 파일 생성
    print("\n[3] Configuration Files...")
    config_json = generate_python_config(configs, str(output_dir))
    filepath = output_dir / "dram_cell_configs.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(config_json)
    print(f"  Generated: dram_cell_configs.json")

    print("\n" + "=" * 60)
    print(f"All files generated in: {output_dir}")
    print("=" * 60)

    # 요약 테이블 출력
    print("\n[Summary] Generated DRAM Cells:")
    print("-" * 120)
    print(f"{'Generation':<15} {'Tech':<12} {'Cap Type':<18} {'Area (um2)':<12} {'VDD':<6} {'Data Rate':<12} {'BW (GB/s)':<10}")
    print("-" * 120)
    for config in configs:
        area = (config.cell_height * config.cell_width) / 1e6
        print(f"{config.generation:<15} {config.tech_node.name:<12} {config.capacitor_type.value:<18} {area:<12.6f} {config.tech_node.vdd:<6.1f} {config.data_rate:<12} {config.bandwidth:<10}")
    print("-" * 120)


if __name__ == "__main__":
    main()
