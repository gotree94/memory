# SRAM 셀 파라미터 제너레이터
# Virtuoso Parametric SRAM Cell Generator
# SRAM 세대별 셀 설계를 위한 파라미터 및 SKILL 코드 생성

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class TechnologyNode:
    """기술 노드 정의"""
    name: str
    node_nm: int
    gate_length: float  # nm
    min_pitch: float    # nm
    vdd: float          # V
    vth: float          # V (threshold voltage)
    oxide_thickness: float  # nm (EOT)


@dataclass
class SRAMCellConfig:
    """SRAM 셀 설계 파라미터"""
    cell_type: str          # 6T, 8T, 10T
    tech_node: TechnologyNode
    # 트랜지스터 크기 (λ 단위)
    pull_up_width: float    # PU PMOS width
    pull_down_width: float  # PD NMOS width
    pass_gate_width: float  # PG NMOS width
    # 레이아웃 파라미터
    cell_height: float      # nm
    cell_width: float       # nm
    # 전기적 파라미터
    snm: float              # Static Noise Margin (mV)
    read_current: float     # μA
    write_margin: float     # mV
    leakage: float          # nA/cell
    access_time: float      # ps


@dataclass
class SRAMDesignKit:
    """SRAM 설계 키트 - 세대별 전체 설정"""
    generation: str
    tech_node: TechnologyNode
    cell_configs: List[SRAMCellConfig] = field(default_factory=list)
    metal_layers: List[str] = field(default_factory=list)
    design_rules: Dict = field(default_factory=dict)


# ============================================================
# 세대별 기술 노드 정의
# ============================================================

TECH_NODES = {
    "gen1_5um": TechnologyNode(
        name="1세대 5μm", node_nm=5000, gate_length=5000,
        min_pitch=5000, vdd=5.0, vth=0.8, oxide_thickness=100
    ),
    "gen2_1um": TechnologyNode(
        name="2세대 1μm", node_nm=1000, gate_length=1000,
        min_pitch=1000, vdd=5.0, vth=0.7, oxide_thickness=20
    ),
    "gen3_350nm": TechnologyNode(
        name="3세대 350nm", node_nm=350, gate_length=350,
        min_pitch=400, vdd=3.3, vth=0.5, oxide_thickness=8
    ),
    "gen4_65nm": TechnologyNode(
        name="4세대 65nm", node_nm=65, gate_length=65,
        min_pitch=180, vdd=1.1, vth=0.35, oxide_thickness=2.5
    ),
    "gen5_14nm": TechnologyNode(
        name="5세대 14nm FinFET", node_nm=14, gate_length=14,
        min_pitch=48, vdd=0.75, vth=0.25, oxide_thickness=1.0
    ),
}


def create_sram_6t_configs() -> List[SRAMCellConfig]:
    """6T SRAM 셀 파라미터 생성 (세대별)"""
    configs = []

    # 1세대: 5μm 6T SRAM
    configs.append(SRAMCellConfig(
        cell_type="6T",
        tech_node=TECH_NODES["gen1_5um"],
        pull_up_width=10.0,   # 2λ
        pull_down_width=10.0, # 2λ
        pass_gate_width=5.0,  # 1λ
        cell_height=40000,    # 8λ (λ=5μm)
        cell_width=20000,     # 4λ
        snm=800, read_current=50, write_margin=900,
        leakage=1000, access_time=50000
    ))

    # 2세대: 1μm 6T SRAM (Full CMOS)
    configs.append(SRAMCellConfig(
        cell_type="6T",
        tech_node=TECH_NODES["gen2_1um"],
        pull_up_width=2.0,
        pull_down_width=2.0,
        pass_gate_width=1.5,
        cell_height=8000,    # 8λ
        cell_width=4000,     # 4λ
        snm=650, read_current=80, write_margin=750,
        leakage=100, access_time=15000
    ))

    # 3세대: 350nm 6T SRAM (Thin-Cell)
    configs.append(SRAMCellConfig(
        cell_type="6T",
        tech_node=TECH_NODES["gen3_350nm"],
        pull_up_width=0.7,
        pull_down_width=0.7,
        pass_gate_width=0.5,
        cell_height=1400,    # 3.5λ
        cell_width=800,      # 2λ
        snm=450, read_current=120, write_margin=550,
        leakage=10, access_time=5000
    ))

    # 4세대: 65nm 6T SRAM (Low-Leakage)
    configs.append(SRAMCellConfig(
        cell_type="6T",
        tech_node=TECH_NODES["gen4_65nm"],
        pull_up_width=0.21,  # 3λ (λ=70nm)
        pull_down_width=0.14,# 2λ
        pass_gate_width=0.105,# 1.5λ
        cell_height=360,     # 5λ
        cell_width=140,      # 2λ
        snm=250, read_current=200, write_margin=350,
        leakage=1, access_time=500
    ))

    # 5세대: 14nm FinFET 6T SRAM
    configs.append(SRAMCellConfig(
        cell_type="6T",
        tech_node=TECH_NODES["gen5_14nm"],
        pull_up_width=0.042, # 3 fins
        pull_down_width=0.028,# 2 fins
        pass_gate_width=0.021,# 1.5 fins
        cell_height=72,      # 6T height
        cell_width=30,       # 2λ
        snm=180, read_current=300, write_margin=250,
        leakage=0.1, access_time=100
    ))

    return configs


def create_sram_8t_configs() -> List[SRAMCellConfig]:
    """8T SRAM 셀 파라미터 생성 (Dual-Port)"""
    configs = []

    # 4세대: 65nm 8T SRAM
    configs.append(SRAMCellConfig(
        cell_type="8T",
        tech_node=TECH_NODES["gen4_65nm"],
        pull_up_width=0.21,
        pull_down_width=0.14,
        pass_gate_width=0.105,
        cell_height=360,
        cell_width=196,      # 읽기 포트 추가로 확장
        snm=280, read_current=250, write_margin=380,
        leakage=1.5, access_time=450
    ))

    # 5세대: 14nm 8T SRAM
    configs.append(SRAMCellConfig(
        cell_type="8T",
        tech_node=TECH_NODES["gen5_14nm"],
        pull_up_width=0.042,
        pull_down_width=0.028,
        pass_gate_width=0.021,
        cell_height=72,
        cell_width=40,
        snm=200, read_current=350, write_margin=270,
        leakage=0.15, access_time=80
    ))

    return configs


def create_sram_10t_configs() -> List[SRAMCellConfig]:
    """10T SRAM 셀 파라미터 생성 (Dual-Port, Full Duplex)"""
    configs = []

    # 4세대: 65nm 10T SRAM
    configs.append(SRAMCellConfig(
        cell_type="10T",
        tech_node=TECH_NODES["gen4_65nm"],
        pull_up_width=0.21,
        pull_down_width=0.14,
        pass_gate_width=0.105,
        cell_height=360,
        cell_width=252,      # 듀얼 포트 전체
        snm=300, read_current=280, write_margin=400,
        leakage=2.0, access_time=420
    ))

    # 5세대: 14nm 10T SRAM
    configs.append(SRAMCellConfig(
        cell_type="10T",
        tech_node=TECH_NODES["gen5_14nm"],
        pull_up_width=0.042,
        pull_down_width=0.028,
        pass_gate_width=0.021,
        cell_height=72,
        cell_width=52,
        snm=220, read_current=380, write_margin=290,
        leakage=0.2, access_time=70
    ))

    return configs


# ============================================================
# SKILL 코드 생성 함수들
# ============================================================

def generate_skill_header(lib_name: str, cell_name: str, view_name: str = "layout") -> str:
    """SKILL 스크립트 헤더 생성"""
    return f"""; ============================================================
; SRAM Cell Layout Generator
; Library: {lib_name}
; Cell:    {cell_name}
; View:    {view_name}
; Auto-generated by SRAM Design Automation Tool
; ============================================================

procedure(sramCreate{cell_name}()
    let((cv ws tech cellBox dx dy)

        ; 라이브러리 및 셀 생성
        when(geCreateCell(nil "{lib_name}" "{cell_name}" "{view_name}" "layout")
            sprintf(msg "Created cell: %s/%s/%s" "{lib_name}" "{cell_name}" "{view_name}")
            println(msg)
        )

        ; 기술 라이브러리 로드
        tech = techOpen("{lib_name}")
        cv = dbOpenCellViewByType("{lib_name}" "{cell_name}" "{view_name}" "" "a")

        ; 디자인 규칙 설정
        techSetTechnologyName(tech "cmos65")

        ; 레이아웃 편집 시작
        dbAddDRO(cv list("cviDrawingGroup" 1) 0 0)
"""


def generate_sram_6t_layout(config: SRAMCellConfig, lib_name: str = "sram_lib") -> str:
    """6T SRAM 셀 레이아웃 SKILL 코드 생성"""
    cell_name = f"sram_6t_{config.tech_node.node_nm}nm"
    λ = config.tech_node.min_pitch / 2  # lambda

    skill = generate_skill_header(lib_name, cell_name)

    skill += f"""
        ; ========================================
        ; 6T SRAM Cell - {config.tech_node.name}
        ; ========================================
        ; Cell Size: {config.cell_height}nm x {config.cell_width}nm
        ; VDD: {config.tech_node.vdd}V
        ; SNM: {config.snm}mV

        ; --- N-Well 생성 (PMOS 영역) ---
        dx = {config.cell_width / 1000}  ; μm 단위
        dy = {config.cell_height / 1000}

        ; Pull-Up PMOS (M1, M2) 배치
        ; PG NMOS (M3, M4) 배치
        ; Pull-Down NMOS (M5, M6) 배치

        ; Active Area 정의
        ; Metal1: VDD rail, VSS rail, Q, Q_bar
        ; Poly: Wordline (WL)
        ; Metal2: Bitline (BL), Bitline_bar (BLB)

        ; --- 6T SRAM 스케마틱 구조 ---
        ;     VDD       VDD
        ;     |         |
        ;    [M1]      [M2]     <- Pull-Up PMOS (가장자리 결함)
        ;     |         |
        ;     +----Q----+----Q_bar----+
        ;     |         |             |
        ;    [M3]      [M4]          [M5]      [M6]  <- PD/PG NMOS
        ;     |         |             |          |
        ;    BL        BLB           VSS        VSS

        println("6T SRAM cell layout generation completed")
    )

    skill += """
        ; 레이아웃 종료
        when(cv,
            dbSave(cv)
            println("Layout saved successfully")
        )
    )

    return(scmCreateCellView(cv))
endprocedure
"""
    return skill


def generate_sram_8t_layout(config: SRAMCellConfig, lib_name: str = "sram_lib") -> str:
    """8T SRAM 셀 레이아웃 SKILL 코드 생성"""
    cell_name = f"sram_8t_{config.tech_node.node_nm}nm"

    skill = generate_skill_header(lib_name, cell_name)

    skill += f"""
        ; ========================================
        ; 8T SRAM Cell (Dual-Port) - {config.tech_node.name}
        ; ========================================
        ; 6T 기본 셀 + 읽기 전용 포트 (M7, M8)
        ; Cell Size: {config.cell_height}nm x {config.cell_width}nm
        ; VDD: {config.tech_node.vdd}V

        ; --- 8T SRAM 스케마틱 구조 ---
        ;     VDD       VDD
        ;     |         |
        ;    [M1]      [M2]     <- Pull-Up PMOS
        ;     |         |
        ;     +----Q----+----Q_bar----+
        ;     |         |             |
        ;    [M3]      [M4]          [M5]      [M6]
        ;     |         |             |          |
        ;    BL_W      BLB_W        VSS        VSS
        ;
        ;              Q_bar
        ;               |
        ;              [M7]       <- Read Port NMOS (게이트: RBL_WL)
        ;               |
        ;              [M8]       <- Read Buffer NMOS
        ;               |
        ;              RBL        <- Read Bitline

        ; 읽기 포트: Q_bar를 기반으로 독립적 읽기
        ; 읽기/쓰기 동시 동작 지원

        println("8T SRAM cell layout generation completed")
    )

    skill += """
        when(cv,
            dbSave(cv)
            println("Layout saved successfully")
        )
    )

    return(scmCreateCellView(cv))
endprocedure
"""
    return skill


def generate_sram_10t_layout(config: SRAMCellConfig, lib_name: str = "sram_lib") -> str:
    """10T SRAM 셀 레이아웃 SKILL 코드 생성"""
    cell_name = f"sram_10t_{config.tech_node.node_nm}nm"

    skill = generate_skill_header(lib_name, cell_name)

    skill += f"""
        ; ========================================
        ; 10T SRAM Cell (Full Dual-Port) - {config.tech_node.name}
        ; ========================================
        ; 6T 기본 + 2개 독립적 읽기/쓰기 포트
        ; Cell Size: {config.cell_height}nm x {config.cell_width}nm
        ; VDD: {config.tech_node.vdd}V

        ; --- 10T SRAM 스케마틱 구조 ---
        ; Port A (Read/Write): WL_A, BL_A, BLB_A
        ; Port B (Read/Write): WL_B, BL_B, BLB_B
        ;
        ;     VDD           VDD
        ;     |             |
        ;    [M1]          [M2]     <- Pull-Up PMOS
        ;     |             |
        ;     +----Q--------+----Q_bar----+
        ;     |             |             |
        ;    [M3]          [M4]          [M5]          [M6]
        ;     |             |             |              |
        ;    BL_A          BLB_A         BL_B          BLB_B
        ;    (WL_A)        (WL_A)        (WL_B)        (WL_B)

        ; 완전 듀얼 포트: 포트 A와 포트 B 독립 동작
        ; 동시 읽기/쓰기 지원

        println("10T SRAM cell layout generation completed")
    )

    skill += """
        when(cv,
            dbSave(cv)
            println("Layout saved successfully")
        )
    )

    return(scmCreateCellView(cv))
endprocedure
"""
    return skill


def generate_sram_array_generator(lib_name: str = "sram_lib") -> str:
    """SRAM 어레이 (array) 생성 SKILL 코드"""
    return f"""; ============================================================
; SRAM Array Generator
; NxM 어레이 자동 생성
; ============================================================

procedure(sramCreateArray(
    libName       ; 라이브러리 이름
    cellName      ; 셀 이름 (예: "sram_6t_65nm")
    viewName      ; 뷰 이름 (예: "layout")
    numWords      ; 워드 수 (행)
    numBits       ; 비트 수 (열)
    muxRatio      ; 멀티플렉스 비율 (1, 2, 4, 8)
)
    let((cv cell cvArray rows cols colIdx rowIdx
           cellW cellH x y objList wl bl blb vdd vss)

        ; 셀 디멘션 확인
        cv = dbOpenCellViewByType(libName cellName viewName "" "a")
        when(nil == cv,
            printf("Error: Cell %s not found\\n" cellName)
            return(nil)
        )

        ; 어레이 크기 계산
        rows = numWords
        cols = numBits * muxRatio

        ; 셀 레이아웃 인스턴스 생성
        cvArray = dbOpenCellViewByType(libName
                    sprintf(nil "%s_array_%dx%d" cellName rows cols)
                    viewName "" "a")

        ; 셀 배치 루프
        for(i 0 rows-1
            for(j 0 cols-1
                x = j * cellW
                y = i * cellH
                ; 셀 인스턴스 배치
                dbCreateInst(cvArray cv cellName
                    sprintf(nil "SRAM_%d_%d" i j) x y "R0")
            )
        )

        ; Wordline 배선 자동 생성
        for(i 0 rows-1
            y = i * cellH + cellH/2
            ; Metal2 Wordline
            dbCreatePath(cvArray
                list(0 y cols*cellW y)
                "M2" 0.1
                list(0 0 cols*cellW cols*cellH))
        )

        ; Bitline 배선 자동 생성
        for(j 0 cols-1
            x = j * cellW + cellW/2
            ; Metal3 Bitline
            dbCreatePath(cvArray
                list(x 0 x rows*cellH)
                "M3" 0.08
                list(0 0 cols*cellW rows*cellH))
        )

        ; VDD/VSS 레일 배선
        for(i 0 rows-1
            y_vdd = i * cellH
            y_vss = (i+1) * cellH - 0.1
            ; VDD (Metal1)
            dbCreatePath(cvArray
                list(0 y_vdd cols*cellW y_vdd)
                "M1" 0.12
                list(0 0 cols*cellW rows*cellH))
            ; VSS (Metal1)
            dbCreatePath(cvArray
                list(0 y_vss cols*cellW y_vss)
                "M1" 0.12
                list(0 0 cols*cellW rows*cellH))
        )

        ; 결과 저장
        dbSave(cvArray)
        printf("SRAM Array created: %s (%dx%d)\\n" cellName rows cols)
    )
    return(cvArray)
endprocedure


; ============================================================
; SRAM 셀 파라미터 최적화 분석
; ============================================================

procedure(sramAnalyzeCell(
    libName
    cellName
    viewName
)
    let((cv cellBox w h ratio)

        cv = dbOpenCellViewByType(libName cellName viewName "" "a")
        cellBox = dbGetCellBox(cv)

        w = xCoord(car(cdr(cellBox))) - xCoord(car(cellBox))
        h = yCoord(cdr(cellBox)) - yCoord(car(cellBox))
        ratio = h / w

        printf("Cell Analysis: %s\\n" cellName)
        printf("  Width:  %.2f um\\n" w)
        printf("  Height: %.2f um\\n" h)
        printf("  Aspect Ratio: %.2f\\n" ratio)
        printf("  Area: %.2f um^2\\n" (* w h))

        return(list(w h ratio))
    )
endprocedure
"""


def generate_python_config(configs: List[SRAMCellConfig], output_dir: str) -> str:
    """Python 설정 파일 생성"""
    config_dict = []
    for c in configs:
        config_dict.append({
            "cell_type": c.cell_type,
            "tech_node": c.tech_node.name,
            "node_nm": c.tech_node.node_nm,
            "vdd": c.tech_node.vdd,
            "pull_up_width_um": c.pull_up_width,
            "pull_down_width_um": c.pull_down_width,
            "pass_gate_width_um": c.pass_gate_width,
            "cell_height_nm": c.cell_height,
            "cell_width_nm": c.cell_width,
            "snm_mv": c.snm,
            "read_current_ua": c.read_current,
            "write_margin_mv": c.write_margin,
            "leakage_na": c.leakage,
            "access_time_ps": c.access_time,
        })

    return json.dumps(config_dict, indent=2, ensure_ascii=False)


# ============================================================
# 메인 실행
# ============================================================

def main():
    """SRAM 셀 파라미터 생성 및 SKILL 코드 출력"""
    output_dir = Path(__file__).parent / "generated"
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("SRAM Cell Design Automation Tool")
    print("=" * 60)

    # 6T SRAM 셀 생성
    print("\n[1] 6T SRAM Cell Generation...")
    configs_6t = create_sram_6t_configs()
    for config in configs_6t:
        skill_code = generate_sram_6t_layout(config)
        filename = f"sram_6t_{config.tech_node.node_nm}nm.skill"
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(skill_code)
        print(f"  Generated: {filename}")

    # 8T SRAM 셀 생성
    print("\n[2] 8T SRAM Cell Generation...")
    configs_8t = create_sram_8t_configs()
    for config in configs_8t:
        skill_code = generate_sram_8t_layout(config)
        filename = f"sram_8t_{config.tech_node.node_nm}nm.skill"
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(skill_code)
        print(f"  Generated: {filename}")

    # 10T SRAM 셀 생성
    print("\n[3] 10T SRAM Cell Generation...")
    configs_10t = create_sram_10t_configs()
    for config in configs_10t:
        skill_code = generate_sram_10t_layout(config)
        filename = f"sram_10t_{config.tech_node.node_nm}nm.skill"
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(skill_code)
        print(f"  Generated: {filename}")

    # 어레이 생성 스크립트
    print("\n[4] SRAM Array Generator...")
    array_skill = generate_sram_array_generator()
    filepath = output_dir / "sram_array_generator.skill"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(array_skill)
    print(f"  Generated: sram_array_generator.skill")

    # Python 설정 파일 생성
    print("\n[5] Configuration Files...")
    all_configs = configs_6t + configs_8t + configs_10t
    config_json = generate_python_config(all_configs, str(output_dir))
    filepath = output_dir / "sram_cell_configs.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(config_json)
    print(f"  Generated: sram_cell_configs.json")

    # 전체 설정 저장
    design_kit = {
        "name": "SRAM Design Kit",
        "generations": [],
        "cell_types": ["6T", "8T", "10T"],
        "output_directory": str(output_dir),
    }

    for config in all_configs:
        gen_entry = {
            "generation": config.tech_node.name,
            "cell_type": config.cell_type,
            "node_nm": config.tech_node.node_nm,
            "cell_area_um2": (config.cell_height * config.cell_width) / 1e6,
            "vdd": config.tech_node.vdd,
        }
        design_kit["generations"].append(gen_entry)

    filepath = output_dir / "sram_design_kit.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(design_kit, f, indent=2, ensure_ascii=False)
    print(f"  Generated: sram_design_kit.json")

    print("\n" + "=" * 60)
    print(f"All files generated in: {output_dir}")
    print("=" * 60)

    # 요약 테이블 출력
    print("\n[Summary] Generated SRAM Cells:")
    print("-" * 90)
    print(f"{'Cell Type':<10} {'Technology':<20} {'Area (um2)':<12} {'VDD (V)':<10} {'SNM (mV)':<10}")
    print("-" * 90)
    for config in all_configs:
        area = (config.cell_height * config.cell_width) / 1e6
        print(f"{config.cell_type:<10} {config.tech_node.name:<20} {area:<12.2f} {config.tech_node.vdd:<10.1f} {config.snm:<10}")
    print("-" * 90)


if __name__ == "__main__":
    main()
