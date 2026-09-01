# GDDR 메모리 설계 자동화 워크플로우 (SKILL + Tcl + Python)

## 1. 언어 조합 개요

| 역할 | 언어 | 실제 파일 |
|------|------|-----------|
| 어레이/채널/I-O 회로 생성 | **SKILL** | `scripts/gddr_generator.skill` |
| 세대별 파라미터/설정 생성 | **Python** | `scripts/gddr_cell_generator.py` |
| 고속 I/O 설계 파라미터 | **Python** | `scripts/gddr_cell_generator.py` |
| DRC/LVS/시뮬레이션 흐름 | **Tcl** | `flow/tcl/run_flow.tcl` |
| 파이프라인 오케스트레이션 | **Python** | `flow/python/pipeline_orchestrator.py` |
| 시그널링(MOC) 성능 모델 | **Python** | `flow/python/memory_model.py` |

---

## 2. 파이프라인 흐름도

```
[1] Python 파라미터 생성
    gddr_cell_generator.py
    → gddr_configs.json (GDDR5/6/6X 파라미터)
          │
[2] SKILL 어레이/I-O 생성 (Virtuoso)
    gddrCreateArray(... generation ...)
    gddrCreateDualChannel("gddr_lib" "ch" 16)
    gddrCreatePAM4IO("gddr_lib" "pam4_io")   ; GDDR6X
    gddrCreateIOCircuit("gddr_lib" "io" gen) ; NRZ
    gddrCreateClockTree("gddr_lib" "clk" 2 4)
          │
[3] Tcl 흐름 제어
    - DRC (PVS)
    - LVS (I/O 회로)
    - SerDes 시뮬레이션 (Spectre)
          │
[4] Python 시그널링 분석
    PAM4/NRZ 눈(Eye) 마진, 대역폭 예측
          │
[5] 리포트 생성
    pipeline_report.json
```

---

## 3. 명령어 실행 방법

### 3.1 전체 파이프라인

```bash
python flow/python/pipeline_orchestrator.py --type gddr --node 12
```

### 3.2 Virtuoso CIW에서 (SKILL 직접 실행)

```skill
load("03.GDDR/scripts/gddr_generator.skill")

; GDDR5 어레이 (16뱅크, 4뱅크그룹, 32-bit)
gddrCreateArray("gddr_lib" "gddr5_array" "GDDR5" 16 4 32)

; GDDR6 듀얼 16-bit 채널
gddrCreateArray("gddr_lib" "gddr6_array" "GDDR6" 16 4 16)
gddrCreateDualChannel("gddr_lib" "gddr6_channels" 16)

; GDDR6X PAM4 I/O 회로
gddrCreatePAM4IO("gddr_lib" "gddr6x_pam4_io")

; 클럭 트리 (2 PLL, 4 WCK)
gddrCreateClockTree("gddr_lib" "gddr_clock" 2 4)
```

### 3.3 Python 제너레이터 실행

```bash
cd 03.GDDR/scripts
python gddr_cell_generator.py
# → generated/ 에 SKILL 6개 + gddr_configs.json 생성
```

---

## 4. 세대별 SKILL 생성 함수 매핑

| 세대 | 시그널링 | 채널 | SKILL 함수 | 핵심 파라미터 |
|------|---------|------|-----------|--------------|
| GDDR5 | NRZ | 단일 32-bit | `gddrCreateArray(... "GDDR5" ...)` | 6 Gbps/pin |
| GDDR6 | NRZ | 듀얼 16-bit | `gddrCreateArray(... "GDDR6" ...)` + `gddrCreateDualChannel` | 16 Gbps/pin |
| GDDR6X | PAM4 | 듀얼 16-bit | `gddrCreateArray(... "GDDR6X" ...)` + `gddrCreatePAM4IO` | 21 Gbps/pin |

---

## 5. 생성 산출물

```
03.GDDR/
├── scripts/
│   ├── gddr_cell_generator.py     (Python 파라미터/설정 생성)
│   ├── gddr_generator.skill       (SKILL 어레이/I-O/클럭 생성)
│   └── generated/
│       ├── gddr_gddr5_array.skill
│       ├── gddr_gddr6_array.skill
│       ├── gddr_gddr6x_array.skill
│       ├── gddr_*_io_driver.skill (NRZ/PAM4)
│       ├── pam4_encoder.skill
│       └── gddr_configs.json
└── docs/
    └── 01_GDDR_Design_Guide.md
```

---

## 6. 언어별 담당 영역 요약

| 단계 | SKILL | Tcl | Python | OA C++ |
|------|:----:|:---:|:------:|:------:|
| 세대별 파라미터 | - | - | ✓ | - |
| 채널/뱅크 어레이 레이아웃 | **✓** | - | - | ● |
| PAM4/NRZ I/O 회로 | **✓** | - | - | ● |
| 클럭 트리 (WCK/CK) | **✓** | - | - | - |
| DRC/LVS | - | **✓** | - | - |
| 눈(Eye) 마진 분석 | - | - | **✓** | - |

✓ = 주 담당, ● = 보조