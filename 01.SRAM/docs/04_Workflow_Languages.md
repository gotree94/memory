# SRAM 설계 자동화 워크플로우 (SKILL + Tcl + Python)

## 1. 언어 조합 개요

| 역할 | 언어 | 실제 파일 |
|------|------|-----------|
| 레이아웃 셀/어레이 생성 | **SKILL** | `scripts/sram_6t_generator.skill` |
| 셀 파라미터/설정 생성 | **Python** | `scripts/sram_cell_generator.py` |
| DRC/LVS/시뮬레이션 흐름 | **Tcl** | `flow/tcl/run_flow.tcl` |
| 파이프라인 오케스트레이션 | **Python** | `flow/python/pipeline_orchestrator.py` |
| 대규모 배치 (선택) | **C++ OA** | `flow/oa_cpp/sram_oa_layout.cpp` |
| 성능 예측/리포트 | **Python** | `flow/python/memory_model.py` |

---

## 2. 파이프라인 흐름도

```
[1] Python 파라미터 생성
    sram_cell_generator.py
    → sram_cell_configs.json (세대별 6T/8T/10T 파라미터)
          │
[2] SKILL 레이아웃 생성 (Virtuoso)
    sram6TGenerate("sram_lib" "cell" "65nm")
    sram6TPlaceAndRoute("sram_lib" "cell" rows cols)
    → layout 셀 생성
          │
[3] Tcl 흐름 제어 (flow/tcl/run_flow.tcl)
    - DRC 실행 (PVS/Assura)
    - LVS 실행
    - RC 추출
          │
[4] Python 시뮬레이션 분석
    memory_model.py → SNM/접근시간/전력 예측
          │
[5] 리포트 생성
    pipeline_report.json
```

---

## 3. 명령어 실행 방법

### 3.1 전체 파이프라인 (Python 오케스트레이터)

```bash
# SRAM만 65nm 기준 실행
python flow/python/pipeline_orchestrator.py --type sram --node 65

# 모든 메모리 타입 실행
python flow/python/pipeline_orchestrator.py --type all --node 65
```

### 3.2 개별 단계 실행

```bash
# 1) 파라미터 생성
python 01.SRAM/scripts/sram_cell_generator.py

# 2) Tcl 흐름 (Virtuoso 환경에서)
#    CIW에서 load("flow/tcl/run_flow.tcl") 또는
tclsh flow/tcl/run_flow.tcl

# 3) 성능 모델
python flow/python/memory_model.py
```

### 3.3 Virtuoso CIW에서 (SKILL 직접 실행)

```skill
load("01.SRAM/scripts/sram_6t_generator.skill")
load("01.SRAM/scripts/sram_8t_generator.skill")
load("01.SRAM/scripts/sram_10t_generator.skill")

; 6T 셀 생성 (65nm)
sram6TGenerate("sram_lib" "my_6t_65nm" "65nm")

; 어레이 생성 (64 워드 x 8 비트)
sram6TPlaceAndRoute("sram_lib" "my_6t_65nm" 64 8)

; 검증
techRunDRC(cv nil nil)
techRunLVS(cv schematicCV nil)
```

---

## 4. 세대별 SKILL 생성 함수 매핑

| 셀 | 세대 | SKILL 함수 | 노드 인자 |
|----|------|-----------|-----------|
| 6T | 1세대 | `sram6TGenerate(... "5um")` | 5000nm |
| 6T | 2세대 | `sram6TGenerate(... "1um")` | 1000nm |
| 6T | 3세대 | `sram6TGenerate(... "350nm")` | 350nm |
| 6T | 4세대 | `sram6TGenerate(... "65nm")` | 65nm |
| 6T | 5세대 | `sram6TGenerate(... "14nm")` | 14nm |
| 8T | 4/5세대 | `sram8TGenerate(... "65nm"/"14nm")` | 65/14nm |
| 10T | 4/5세대 | `sram10TGenerate(... "65nm"/"14nm")` | 65/14nm |

---

## 5. 생성 산출물

```
01.SRAM/
├── scripts/
│   ├── sram_cell_generator.py        (Python 파라미터/설정 생성)
│   ├── sram_6t_generator.skill       (SKILL 6T 레이아웃)
│   ├── sram_8t_generator.skill       (SKILL 8T 레이아웃)
│   ├── sram_10t_generator.skill      (SKILL 10T 레이아웃)
│   └── generated/
│       └── sram_cell_configs.json    (세대별 파라미터 설정)
└── docs/
    ├── 01_6T_SRAM_Design.md
    ├── 02_8T_SRAM_Design.md
    └── 03_10T_SRAM_Design.md
```

---

## 6. 언어별 담당 영역 요약

| 단계 | SKILL | Tcl | Python | OA C++ |
|------|:----:|:---:|:------:|:------:|
| 파라미터 계산 | - | - | ✓ | - |
| 셀 레이아웃 | **✓** | - | - | ● (대규모) |
| 어레이 배치 | **✓** | - | - | ● |
| DRC/LVS | - | **✓** | - | - |
| 시뮬레이션 | ● | **✓** | - | - |
| 파형/리포트 분석 | - | - | **✓** | - |
| 흐름 오케스트레이션 | - | **✓** | **✓** | - |

✓ = 주 담당, ● = 보조