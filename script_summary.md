# 메모리 설계 자동화 스크립트 요약 (Script Summary)

> 프로젝트 루트: `C:\Users\Administrator\Desktop\memory`
> 기준 언어 조합: **SKILL + Tcl + Python + OA C++** (실무 표준, Cadence Virtuoso)

---

## 1. 목적

메모리 세대별(SRAM/SDRAM/GDDR/HBM) 설계 자동화 스크립트를
**언어별 역할 분담**으로 구성하고, Cadence 45nm 학습 PDK
(GPDK045/giolib045 + gsclib045)와 연동하여 Virtuoso에서 바로
레이아웃·주변회로·검증 흐름을 돌릴 수 있게 정리한다.

---

## 2. 언어 조합 및 담당 영역

| 역할 | 언어 | 파일 위치 |
|------|------|-----------|
| 레이아웃/스케마틱 객체 생성 (셀·어레이·I/O·TSV) | **SKILL** | 각 폴더 `scripts/*.skill` |
| 셀 파라미터 계산 + 설정 JSON 생성 | **Python** | 각 폴더 `scripts/*_generator.py` |
| DRC/LVS/시뮬레이션 툴 흐름 제어 | **Tcl** | `flow/tcl/run_flow.tcl` |
| 파이프라인 오케스트레이터 (전체 자동화) | **Python** | `flow/python/pipeline_orchestrator.py` |
| 성능 예측/스케일링 모델 | **Python** | `flow/python/memory_model.py` |
| 대규모 배치 자동화 (100만+ 셀, 선택) | **C++ (OA)** | `flow/oa_cpp/sram_oa_layout.cpp` |

---

## 3. 디렉토리 구조

```
memory/
├── README.md                     세대별 비교 + 자동화 아키텍처
├── GPDK045/                      Cadence 45nm 학습 PDK (giolib045 I/O)
├── gsclib045_all_v4.8/           Cadence 45nm 표준 셀 (gsclib045)
├── 01.SRAM/                      scripts(.skill/.py) + docs
├── 02.SDRAM/                     scripts(.skill/.py) + docs
├── 03.GDDR/                      scripts(.skill/.py) + docs
├── 04.HBM/                       scripts(.skill/.py) + docs
└── flow/
    ├── skill/cad45_init.skill    Cadence 45nm PDK 초기화 (공용)
    ├── skill/cad45_periph.skill  주변회로→표준셀 매핑 (공용)
    ├── tcl/run_flow.tcl          Tcl 통합 흐름 제어
    ├── python/pipeline_orchestrator.py  파이프라인 오케스트레이터
    ├── python/memory_model.py    성능 예측 모델 (45nm 지원)
    ├── python/cadence45.py       45nm 학습 PDK 카탈로그 (공용)
    ├── oa_cpp/sram_oa_layout.cpp OA C++ 레이아웃 예제
    └── reports/pipeline_report.json    파이프라인 결과 리포트
```

---

## 4. 메모리 타입별 스크립트/문서

| 폴더 | Python 제너레이터 | SKILL 제너레이터 | 문서 |
|------|-------------------|------------------|------|
| 01.SRAM | `sram_cell_generator.py` | `sram_6t/8t/10t_generator.skill` | `01~03_*_Design.md`, `04_Workflow_Languages.md` |
| 02.SDRAM | `dram_cell_generator.py` | `dram_cell_generator.skill` | `01_DRAM_Generation_Guide.md`, `02_Workflow_Languages.md` |
| 03.GDDR | `gddr_cell_generator.py` | `gddr_generator.skill` | `01_GDDR_Design_Guide.md`, `02_Workflow_Languages.md` |
| 04.HBM | `hbm_stack_generator.py` | `hbm_stack_generator.skill` | `01_HBM_Stack_Design_Guide.md`, `02_Workflow_Languages.md` |

각 제너레이터는 실행 시 `scripts/generated/`에:
- 설정 JSON (`sram_cell_configs.json`, `dram_cell_configs.json`, `gddr_configs.json`, `hbm_configs.json`)
- Cadence 45nm 카탈로그 (`cadence45.json`)
을 생성한다.

---

## 5. Cadence 45nm 학습 PDK 연동

| 라이브러리 | 내용 | 쓰임 |
|-----------|------|------|
| `GPDK045/giolib045_v3.3` | OA `giolib045` IO/PAD 셀, `cdl/giolib045.cdl`, `lef/giolib045.lef` | 메모리 I/O 링, LVS/LEF 소스 |
| `gsclib045_all_v4.8/GSCLIB045` | OA `gsclib045` 표준 셀 69종 | 디코더/WL 드라이버/레지스터/컬럼 mux |
| 디바이스 모델 | `g45p1svt`·`g45n1svt`(1.0V), `g45p2svt`·`g45n2svt`(2.5V) | 트랜지스터 네이밍 (gpdk045) |

표준 셀 매핑 예:
- 주소 디코더: `NAND2X8 / NOR2X4 / AND2XL / INVXL`
- 워드라인 드라이버: `BUFX20 / TBUFX6 / BUFX6`
- 레지스터: `DFFHQX1 / SDFFQX4 / DFFHQX2`   (※ `DFFQX1` 셀은 gsclib045에 존재하지 않음)
- 컬럼 mux: `MX2X1 / MXI2X1 / MX3X1`
- 타이밍 지연: `DLY1X4 / DLY2X4 / DLY4X1`

I/O PAD는 OA 셀뷰 유무에 따라 두 그룹으로 구분하여 사용한다.
- **OA 셀뷰 존재(instancing 가능)**: `PADVDD / PADVDD25 / PADVDDIOR / IORINGVSS / IORINGVSS25 / IORINGDI / IORINGFEED3X / IORINGFEED60 / bidirlogic / ESDCore04_Input / nonzoutlogic`
- **CDL/LEF 전용(OA 없음, LVS·LEF 참조용)**: `PADDI / PADDO / PADDOZ / PADDB / BONDPAD52 / PADANALOG / PADVSS / PADVSS25 / PADVSSIOR`

---

## 6. 실행 방법

### 6.1 전체 파이프라인 (Python, 오프라인 데모)

```bash
# 전 메모리 타입, Cadence 45nm 학습 PDK 노드 기준
python flow/python/pipeline_orchestrator.py --type all --node 45

# 특정 타입만
python flow/python/pipeline_orchestrator.py --type sram --node 65
```

색인: 리포트 자동 생성 → `flow/reports/pipeline_report.json`

### 6.2 Tcl 통합 흐름

```bash
tclsh flow/tcl/run_flow.tcl
```
`flow_init_pdk`가 GPDK045 OA 경로·LEF·CDL 소스를 구성한다.
OA 라이브러리 루트는 셀 디렉토리를 포함한
`.../GPDK045/giolib045_v3.3/oa22/giolib045`와
`.../gsclib045_all_v4.8/GSCLIB045/oa22/gsclib045`를 가리킨다.

### 6.3 성능 모델

```bash
python flow/python/memory_model.py
```

### 6.4 Virtuoso CIW에서 SKILL 직접 실행

```skill
; 공용 초기화 + 주변회로 매핑
load("flow/skill/cad45_init.skill")
load("flow/skill/cad45_periph.skill")

; 메모리 타입별 주변회로 계획 확인
cad45PeriphPlan("sram")

; SRAM (45nm GPDK045 기반)
sram6TGenerate("sram_lib" "cell6t_45" "45nm")
sram6TPlaceAndRoute("sram_lib" "array_45" 128 128)

; SDRAM (1T1C, 커패시터 타입별)
dramCreateBCAT("dram_lib" "ddr3_cell" "65nm")
dramCreateArray("dram_lib" "ddr3_cell" "layout" 8192 8 8)

; GDDR 채널 어레이 + I/O
gddrCreateArray("gddr_lib" "gddr6x_array" "GDDR6X" 16 4 16)
gddrCreatePAM4IO("gddr_lib" "gddr6x_pam4_io")

; HBM 3D 스택
hbmGenerateFull("hbm_lib" "HBM3E")
```

---

## 7. 주요 수정/정리 내역

1. **공용 `flow/` 신규 구성**
   - `tcl/run_flow.tcl`: 단일화된 검증/시뮬레이션 흐름 프레임워크, PDK 초기화 추가
   - `python/pipeline_orchestrator.py`: 5단계 파이프라인 오케스트레이터
   - `python/memory_model.py`: 공정 스케일링 성능 예측 (45nm 학습 노드 포함)
   - `oa_cpp/sram_oa_layout.cpp`: OA C++ 참조 예제 (giolib045/gsclib045 콜아웃)

2. **파서/실행 버그 수정**
   - SRAM/SDRAM Python 제너레이터의 `IndentationError` → 파라미터+JSON+SKILL 가이드 구조로 재작성
   - `pipeline_orchestrator.py`: `Optional` import 누락 수정
   - `memory_model.py`: TECH 딕셔너리 타입 키 및 `_nearest()` 노드 대체 추가
   - Tcl: `puts "...[...]..."`의 Tcl 명령 치환 오류를 중괄호/이스케이프로 수정

3. **Cadence 45nm 학습 PDK 통합 (최신)**
   - 공용 `cad45_init.skill` / `cad45_periph.skill` 신설
   - 공용 카탈로그 `flow/python/cadence45.py` → 각 `generated/cadence45.json` 자동 생성
   - SRAM SKILL에 `"45nm"`(GPDK045) 분기 추가
   - SDRAM/GDDR/HBM SKILL에 PDK 프리앰블 로드
   - `memory_model.py` 모든 메모리 타입에 45nm 노드 추가
   - `pipeline_orchestrator.py` PDK 존재 자동 검출 → 리포트 반영
   - `run_flow.tcl` PDK/LEF/CDL 환경 구성
   - README에 학습 PDK 연동 섹션 추가

4. **학습 PDK 대조 감사 및 문제 수정 (최신)**
   - `DFFQX1`(존재하지 않음) → `DFFHQX1` 일괄 교체
     - `cadence45.py` `register_ff`, `cad45_periph.skill` `data_ff`, `oa_cpp` 주석,
       `README.md`, `script_summary.md`, 4종 `generated/cadence45.json` 재생성
   - PAD 인벤토리를 `cad45_pads_oa`(OA 셀뷰, instancing 가능) /
     `cad45_pads_cdl`(CDL·LEF 전용)로 분리, `cad45_periph.skill` PAD 맵도
     `cad45_pad_map_oa` / `cad45_pad_map_cdl`로 이원화
   - OA 라이브러리 루트를 셀 디렉토리 포함 경로로 보정
     (`cad45_init.skill`, `run_flow.tcl`), `cad45CellExists`를 layout 뷰 기준으로 변경
   - SKILL 제너레이터 6종에서 `geCreateCell(nil ...)` → `geCreateCell(ddGetObj(libName) ...)`
   - `sram_6t_generator.skill` 손상 식별자 `t和技术Exists` → `techExists` 복구,
     6개 제너레이터 한글 주석 인코딩(CP949 역변환) 복원 + UTF-8 BOM 제거
   - `run_flow.tcl` `file join $dir scripts ...` → `set skill_script_dir [file join $dir scripts]`
   - 상세 표는 `README.md > 학습 PDK 감사(audit) 및 문제 수정 내역` 참조

---

## 8. 검증 결과

```
$ python flow/python/pipeline_orchestrator.py --type all --node 45
  Cadence 45nm PDK: giolib045 + gsclib045 (installed)
     sram: access= 0.35ns  BW=  46.2GB/s
    sdram: access= 6.35ns  BW=   2.3GB/s
     gddr: access= 4.51ns  BW=  46.2GB/s
      hbm: access= 5.54ns  BW= 591.6GB/s
  Report: flow/reports/pipeline_report.json   (exit 0)

$ tclsh flow/tcl/run_flow.tcl   → "Memory Flow completed." (exit 0)
4개 제너레이터 + memory_model(45nm) 모두 정상 실행
```

**감사 재검증 (PDK 경로 보정 + 셀/PAD 인벤토리 수정 후) 재실행 결과 (exit 0):**

```
$ python flow/python/pipeline_orchestrator.py
  Cadence 45nm PDK: giolib045 + gsclib045 (installed)
     sram: access=    0.50ns  BW=    32.0GB/s
    sdram: access=    7.33ns  BW=     1.6GB/s
     gddr: access=    5.87ns  BW=    32.0GB/s
      hbm: access=    5.54ns  BW=   591.6GB/s
  Report: flow/reports/pipeline_report.json   (exit 0)

$ tclsh flow/tcl/run_flow.tcl
    - gsclib045 (std cells) : .../GSCLIB045/oa22/gsclib045
    - giolib045 (IO pads)   : .../giolib045_v3.3/oa22/giolib045
  "Memory Flow completed." (exit 0)
```

전체 소스 트리 검사: 소스 파일에서 `DFFQX1`, `geCreateCell(nil`, 손상 식별자
(`t和技术Exists` 계열) 0건. `DFFQX1` 문자열은 PDK 내부 OA 이진 데이터(`sch.oa`)에만 잔존.

`pipeline_report.json`에 `cadence_45nm_learning_pdk: { "installed": true, ... }`
블록이 기록되어 PDK 연동 상태를 확인할 수 있다.