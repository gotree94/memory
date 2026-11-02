# 메모리 셀 설계 Python 스캐폴드 (GPDK045 / IC6.1.8)

`01.SRAM`, `02.SDRAM`, `03.GDDR`, `04.HBM`의 메모리 셀과 교육용 array/tile을
Python으로 CDL로 생성하는 프로젝트입니다. 앞에서 만든
`virtuoso-python`과 같은 GPDK045 / Virtuoso IC6.1.8 환경을 가정합니다.

핵심 원칙:

- **schematic은 Python → CDL → Virtuoso CDL In**으로 생성합니다.
- layout/DRC/LVS/PEX는 이 프로젝트의 범위가 아닙니다.
- GDDR과 HBM은 **셀 이름이 아니라 인터페이스/적층 규격**입니다. 저장 셀은
  기본적으로 DRAM 1T1C이며, GDDR/HBM 문서에서는 차이를 인터페이스 관점에서
  설명합니다.
- GPDK045는 **로직 PDK**입니다. 실제 DRAM 공정의 deep-trench/stack capacitor,
  retention, refresh 특성을 재현하지 못합니다. 따라서 이 프로젝트는
  **교육용 토폴로지/배열/주변회로 스캐폴드**입니다.

---

## 1. 폴더 구조

```text
memory/
├─ README.md              # 이 문서
├─ common.py              # CDL 빌더 (MOS/C/R/X, Cell, manifest)
├─ sram.py                # 6T SRAM bitcell + array/tile
├─ sdram.py               # 1T1C DRAM cell + SDRAM-style array/tile
├─ gddr.py                # GDDR6-style 1T1C tile + IO placeholder
├─ hbm.py                 # HBM3-style 1T1C tile + TSV model
├─ run_all.py             # 전체 CDL 생성 + manifest
├─ verify.py              # CDL 구조/manifest 검증
├─ requirements.txt       # 외부 의존성 없음
├─ docs/
│  ├─ 01_SRAM.md
│  ├─ 02_SDRAM.md
│  ├─ 03_GDDR.md
│  └─ 04_HBM.md
└─ out/                   # run_all.py가 생성하는 CDL + manifest
   ├─ 01_SRAM/
   ├─ 02_SDRAM/
   ├─ 03_GDDR/
   ├─ 04_HBM/
   └─ manifest.json
```

---

## 2. 빠른 실행

Python 3.8 이상이면 외부 패키지 없이 실행됩니다.

```powershell
cd C:\Users\Administrator\Desktop\memory
python run_all.py
python verify.py
```

특정 그룹만 생성:

```powershell
python run_all.py --only SRAM,SDRAM
```

셀 목록 확인:

```powershell
python run_all.py --list
```

정상 실행 시 `out/` 아래에 23개의 CDL과 `manifest.json`이 생성됩니다.

---

## 3. 생성 셀 요약

| 그룹 | 셀 | 설명 |
|---|---|---|
| 01_SRAM | `SRAM6T` | 6T SRAM bitcell (cross-coupled inverter + 2 access NMOS) |
| 01_SRAM | `SRAM_PRECHARGE` | BL/BLB precharge + equalize |
| 01_SRAM | `SRAM_SENSE` | cross-coupled sense amplifier + SAE tail |
| 01_SRAM | `SRAM_ARRAY_8X8` | 64개 `SRAM6T` array |
| 01_SRAM | `SRAM_TILE_8X8` | array + 8 precharge + 8 sense amp |
| 02_SDRAM | `DRAM1T1C` | 1T1C DRAM cell + ideal storage capacitor |
| 02_SDRAM | `DRAM_PRECHARGE` | active-low PMOS precharge/equalize to VBL |
| 02_SDRAM | `DRAM_SENSE` | cross-coupled DRAM sense amplifier |
| 02_SDRAM | `SDRAM_ARRAY_8X8` | 64개 `DRAM1T1C` array |
| 02_SDRAM | `SDRAM_TILE_8X8` | array + precharge + sense amp |
| 03_GDDR | `GDDR6_CELL` | GDDR-style 1T1C cell |
| 03_GDDR | `GDDR6_PRECHARGE` | GDDR tile precharge/equalize |
| 03_GDDR | `GDDR6_SENSE` | GDDR tile sense amplifier |
| 03_GDDR | `GDDR6_IO` | 단순 DQ 출력 버퍼 placeholder |
| 03_GDDR | `GDDR6_ARRAY_4X4` | 16개 `GDDR6_CELL` array |
| 03_GDDR | `GDDR6_TILE_4X4` | array + precharge + sense + DQ buffer |
| 04_HBM | `HBM3_CELL` | HBM-style 1T1C cell |
| 04_HBM | `HBM3_PRECHARGE` | HBM tile precharge/equalize |
| 04_HBM | `HBM3_SENSE` | HBM tile sense amplifier |
| 04_HBM | `HBM3_IO` | TSV 앞단 출력 버퍼 placeholder |
| 04_HBM | `HBM3_TSV` | ideal TSV R + C 모델 |
| 04_HBM | `HBM3_ARRAY_4X4` | 16개 `HBM3_CELL` array |
| 04_HBM | `HBM3_TILE_4X4` | array + precharge + sense + IO + TSV |

---

## 4. Virtuoso CDL In 절차

1. Library Manager에서 `MEMORY45` 라이브러리를 만들고 `gpdk045` technology를
   attach합니다.
2. 낮은 계층부터 CDL In으로 가져옵니다.

```text
01_SRAM:  SRAM6T → SRAM_PRECHARGE → SRAM_SENSE → SRAM_ARRAY_8X8 → SRAM_TILE_8X8
02_SDRAM: DRAM1T1C → DRAM_PRECHARGE → DRAM_SENSE → SDRAM_ARRAY_8X8 → SDRAM_TILE_8X8
03_GDDR:  GDDR6_CELL → GDDR6_PRECHARGE → GDDR6_SENSE → GDDR6_IO → GDDR6_ARRAY_4X4 → GDDR6_TILE_4X4
04_HBM:   HBM3_CELL → HBM3_PRECHARGE → HBM3_SENSE → HBM3_IO → HBM3_TSV → HBM3_ARRAY_4X4 → HBM3_TILE_4X4
```

Virtuoso 메뉴:

```text
File > Import > CDL
Input File: out/01_SRAM/SRAM6T.cdl
Target Library: MEMORY45
```

상위 셀이 하위 셀을 `X` 인스턴스로 참조하므로, **하위 셀을 먼저 import**해야
합니다. import 후 schematic에서 pin 이름과 instance master가 맞는지 확인하세요.

---

## 5. 설계 파라미터

| 항목 | 값 | 비고 |
|---|---|---|
| MOS L | 45 nm | GPDK045 기본 |
| SRAM pull-down | 240 nm | read stability를 위한 출발점 |
| SRAM pull-up | 120 nm | cross-coupled inverter |
| SRAM access | 180 nm | beta ratio > 1 |
| DRAM access | 180 nm | SDRAM tile |
| GDDR/HBM access | 150 nm | 교육용 차이 |
| SDRAM storage cap | 10 fF | ideal capacitor |
| GDDR storage cap | 8 fF | ideal capacitor |
| HBM storage cap | 6 fF | ideal capacitor |
| Sense amp PMOS/NMOS | 240 nm | tail 480 nm |
| Precharge PMOS | 120~180 nm | active-low |

> 이 값은 **스케일링 출발점**입니다. 실제 bitcell은 Monte Carlo, read/write
> margin, leakage, EM/IR, DRC/LVS를 통해 재조정해야 합니다.

### 5.1 코드에서 사이징 변경

각 모듈의 factory 함수는 파라미터를 받습니다.

```python
import sram

cell = sram.sram6t(pd_w=0.300, pu_w=0.120, pg_w=0.180)
print(cell.cdl())
```

`run_all.py`는 기본값을 사용합니다. 다른 값을 일괄 적용하려면 각 모듈의
기본값을 바꾸거나, 별도 스크립트에서 factory를 호출해 `write_cells()`로
저장하면 됩니다.

---

## 6. 검증

`verify.py`는 다음을 확인합니다.

- 파일마다 `.SUBCKT`/`.ENDS`가 하나씩 있는지
- subcircuit 이름과 pin list가 manifest와 같은지
- MOS/C/R/X 개수가 manifest와 같은지

현재 결과:

```text
checked=23 errors=0
[PASS] all generated CDL files match their manifests
```

이 검증은 **CDL 구조 검증**입니다. Spectre 동작, DRC, LVS, PEX를 대체하지 않습니다.

---

## 7. 중요한 한계

1. **GPDK045는 DRAM 공정이 아닙니다.** 1T1C의 capacitor는 ideal C이며,
   retention/refresh/leakage를 예측할 수 없습니다.
2. **GDDR/HBM은 cell topology가 아닙니다.** 저장 셀은 1T1C이고, GDDR/HBM의
   핵심은 DQ 인터페이스, clocking, equalization, TSV/적층입니다. 이 프로젝트는
   그중 셀/배열/간단한 주변회로만 모델링합니다.
3. **layout은 없습니다.** 6T/1T1C bitcell layout은 DRC/LVS/DFM이 매우 어렵기
   때문에 이 스캐폴드에서는 CDL schematic까지만 다룹니다.
4. **row/column decoder, refresh controller, write driver, ESD, PHY는 없습니다.**
   교육용 array/tile 수준입니다.
5. **CDL In 모델명**은 PDK `auCdl` 설정에 따라 `g45n1svt` 대신 `nmos1v`를
   요구할 수 있습니다. import 오류가 나면 모델명을 바꿔보세요.

---

## 8. 다음 단계

- `SRAM6T`에 write driver와 row decoder를 추가해 full macro로 확장
- `DRAM1T1C`에 VDD/2 generator와 reference cell을 추가
- GDDR tile에 differential DQ, termination, equalization 추가
- HBM tile을 multi-channel/pseudo-channel 구조로 확장
- Spectre testbench로 read/write margin, sense delay, power 측정
- 실제 메모리 공정 PDK가 있다면 capacitor/access device를 교체

각 그룹의 상세 설명은 아래 문서를 참고하세요.

- [01_SRAM](docs/01_SRAM.md)
- [02_SDRAM](docs/02_SDRAM.md)
- [03_GDDR](docs/03_GDDR.md)
- [04_HBM](docs/04_HBM.md)

---

## 9. 라이선스 / 주의

이 프로젝트는 교육용입니다. GPDK045는 Cadence 교육용 로직 PDK이며, 실제
silicon sign-off용이 아닙니다. DRAM retention, GDDR/HBM PHY 성능, HBM 적층
신뢰성을 보장하지 않습니다.
