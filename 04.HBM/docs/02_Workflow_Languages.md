# HBM 메모리 설계 자동화 워크플로우 (SKILL + Tcl + Python)

## 1. 언어 조합 개요

| 역할 | 언어 | 실제 파일 |
|------|------|-----------|
| 스택/3D 적층/Base Die/TSV 생성 | **SKILL** | `scripts/hbm_stack_generator.skill` |
| 세대별 파라미터/설정 생성 | **Python** | `scripts/hbm_stack_generator.py` |
| 3D 패키징/TSV 파라미터 | **Python** | `scripts/hbm_stack_generator.py` |
| DRC/LVS/시뮬레이션 흐름 | **Tcl** | `flow/tcl/run_flow.tcl` |
| 파이프라인 오케스트레이션 | **Python** | `flow/python/pipeline_orchestrator.py` |
| 대역폭/용량/채널 성능 모델 | **Python** | `flow/python/memory_model.py` |

---

## 2. 파이프라인 흐름도

```
[1] Python 파라미터 생성
    hbm_stack_generator.py
    → hbm_configs.json (HBM1~HBM3E 파라미터)
          │
[2] SKILL 3D 스택 생성 (Virtuoso)
    hbmGenerateFull("hbm_lib" "HBM3E")
    → HBM3E_stack        (Core Die 어레이)
    → HBM3E_base_die     (로직/PHY)
    → HBM3E_tsv          (TSV 어레이)
          │
[3] Tcl 흐름 제어
    - 패키징 DRC (Advanced Package)
    - 전기 검증 (TSV 기생 RC)
    - 열 분석 동작 제어
          │
[4] Python 성능 분석
    memory_model.py → 대역폭/용량/채널 효율
          │
[5] 리포트 생성
    pipeline_report.json
```

---

## 3. 명령어 실행 방법

### 3.1 전체 파이프라인

```bash
python flow/python/pipeline_orchestrator.py --type hbm --node 10
```

### 3.2 Virtuoso CIW에서 (SKILL 직접 실행)

```skill
load("04.HBM/scripts/hbm_stack_generator.skill")

; HBM3E 풀 스택 생성 (가장 간편)
hbmGenerateFull("hbm_lib" "HBM3E")
; → HBM3E_stack, HBM3E_base_die, HBM3E_tsv

; 또는 개별 생성
hbmCreateStack("hbm_lib" "hbm3_stack" "HBM3" 16 16 64)
hbmCreateBaseDie("hbm_lib" "hbm3_base" "HBM3" 16 1024)
hbmCreateTSV("hbm_lib" "hbm3_tsv" 5 28 10000)
```

### 3.3 Python 제너레이터 실행

```bash
cd 04.HBM/scripts
python hbm_stack_generator.py
# → generated/ 에 세대별 stack/base_die/tsv SKILL + hbm_configs.json
```

---

## 4. 세대별 SKILL 생성 함수 매핑

| 세대 | 적층 | 채널 | SKILL 함수 | 대역폭 |
|------|------|------|-----------|--------|
| HBM1 | 4-Hi | 8x128-bit | `hbmGenerateFull("hbm_lib" "HBM1")` | 128 GB/s |
| HBM2 | 8-Hi | Pseudo 2x512 | `hbmGenerateFull("hbm_lib" "HBM2")` | 256 GB/s |
| HBM2E | 12-Hi | Pseudo 2x512 | `hbmGenerateFull("hbm_lib" "HBM2E")` | 600 GB/s |
| HBM3 | 16-Hi | 16x64-bit | `hbmGenerateFull("hbm_lib" "HBM3")` | 1 TB/s |
| HBM3E | 12-Hi | 16x64-bit | `hbmGenerateFull("hbm_lib" "HBM3E")` | 1.2 TB/s |

---

## 5. 생성 산출물

```
04.HBM/
├── scripts/
│   ├── hbm_stack_generator.py     (Python 파라미터/설정 생성)
│   ├── hbm_stack_generator.skill  (SKILL 스택/TSV/Base Die 생성)
│   └── generated/
│       ├── hbm_hbm1_stack.skill ... hbm_hbm3e_stack.skill
│       ├── hbm_hbm1_base_die.skill ... hbm_hbm3e_base_die.skill
│       ├── hbm_hbm1_tsv.skill ... hbm_hbm3e_tsv.skill
│       └── hbm_configs.json
└── docs/
    └── 01_HBM_Stack_Design_Guide.md
```

---

## 6. 언어별 담당 영역 요약

| 단계 | SKILL | Tcl | Python | OA C++ |
|------|:----:|:---:|:------:|:------:|
| 세대별 파라미터 | - | - | ✓ | - |
| Core Die 스택 레이아웃 | **✓** | - | - | ● |
| TSV 어레이 | **✓** | - | - | ● |
| Base Die (PHY/로직) | **✓** | - | - | ● |
| 패키징 DRC/전기 검증 | - | **✓** | - | - |
| 대역폭/적층 성능 분석 | - | - | **✓** | - |

✓ = 주 담당, ● = 보조