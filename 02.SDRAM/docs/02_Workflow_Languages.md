# DRAM / SDRAM 설계 자동화 워크플로우 (SKILL + Tcl + Python)

## 1. 언어 조합 개요

| 역할 | 언어 | 실제 파일 |
|------|------|-----------|
| 1T1C 셀/어레이 레이아웃 생성 | **SKILL** | `scripts/dram_cell_generator.skill` |
| 셀 파라미터/설정 생성 | **Python** | `scripts/dram_cell_generator.py` |
| DRC/LVS/시뮬레이션 흐름 | **Tcl** | `flow/tcl/run_flow.tcl` |
| 파이프라인 오케스트레이션 | **Python** | `flow/python/pipeline_orchestrator.py` |
| 대규모 배치 (선택) | **C++ OA** | `flow/oa_cpp/sram_oa_layout.cpp` |
| 성능 예측/리포트 | **Python** | `flow/python/memory_model.py` |

---

## 2. 파이프라인 흐름도

```
[1] Python 파라미터 생성
    dram_cell_generator.py
    → dram_cell_configs.json (세대별 1T1C 파라미터)
          │
[2] SKILL 레이아웃 생성 (Virtuoso)
    dramCreatePlanar / StackedCylinder / BCAT / Pillar
    → 셀 레이아웃 + dramCreateArray → 어레이
          │
[3] Tcl 흐름 제어 (flow/tcl/run_flow.tcl)
    - DRC (PVS/Assura)
    - LVS
    - RC 추출 → netlist
          │
[4] Python 시뮬레이션 분석
    memory_model.py → 접근시간/리프레시/대역폭
          │
[5] 리포트 생성
    pipeline_report.json
```

---

## 3. 명령어 실행 방법

### 3.1 전체 파이프라인

```bash
python flow/python/pipeline_orchestrator.py --type sdram --node 65
```

### 3.2 개별 단계

```bash
# 파라미터 생성
python 02.SDRAM/scripts/dram_cell_generator.py

# Tcl 흐름
tclsh flow/tcl/run_flow.tcl

# 성능 모델
python flow/python/memory_model.py
```

### 3.3 Virtuoso CIW에서 (SKILL 직접 실행)

```skill
load("02.SDRAM/scripts/dram_cell_generator.skill")

; 세대별 셀 생성
dramCreatePlanar("dram_lib" "dram_planar_8um" "8um")          ; 1세대
dramCreateStackedCylinder("dram_lib" "dram_sdr_350nm" "350nm") ; SDRAM
dramCreateBCAT("dram_lib" "dram_ddr3_65nm" "65nm")             ; DDR3
dramCreatePillar("dram_lib" "dram_ddr5_14nm" "14nm")           ; DDR5

; 어레이 생성 (8K 워드 x 8비트, 8뱅크)
dramCreateArray("dram_lib" "dram_ddr3_65nm" "layout" 8192 8 8)
```

---

## 4. 세대별 SKILL 생성 함수 매핑

| 세대 | 커패시터 | SKILL 함수 | 노드 인자 |
|------|---------|-----------|-----------|
| 1세대 | Planar | `dramCreatePlanar` | "8um" |
| EDO | Trench | `dramCreateTrench` | "600nm" |
| SDRAM | Stacked Cylinder | `dramCreateStackedCylinder` | "350nm" |
| DDR1 | MIM | `dramCreateStackedCylinder` | "180nm" |
| DDR2 | MIM | `dramCreateStackedCylinder` | "90nm" |
| DDR3 | BCAT | `dramCreateBCAT` | "65nm" |
| DDR4 | BCAT+HAR | `dramCreateBCAT` | "30nm" |
| DDR5 | Pillar | `dramCreatePillar` | "14nm" |

---

## 5. 생성 산출물

```
02.SDRAM/
├── scripts/
│   ├── dram_cell_generator.py     (Python 파라미터/설정 생성)
│   ├── dram_cell_generator.skill  (SKILL 1T1C 레이아웃 생성)
│   └── generated/
│       └── dram_cell_configs.json (세대별 파라미터 설정)
└── docs/
    └── 01_DRAM_Generation_Guide.md
```

---

## 6. 언어별 담당 영역 요약

| 단계 | SKILL | Tcl | Python | OA C++ |
|------|:----:|:---:|:------:|:------:|
| 파라미터 계산 | - | - | ✓ | - |
| 1T1C 셀 레이아웃 | **✓** | - | - | ● |
| 커패시터 타입별 배치 | **✓** | - | - | ● |
| 어레이/뱅크 배치 | **✓** | - | - | ● |
| DRC/LVS | - | **✓** | - | - |
| 리프레시/타이밍 분석 | - | - | **✓** | - |

✓ = 주 담당, ● = 보조