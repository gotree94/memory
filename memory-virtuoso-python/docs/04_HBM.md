# 04. HBM — HBM-style 1T1C tile with TSV

## 1. 먼저 구분할 것

**HBM은 메모리 셀의 이름이 아니라 3D 적층 DRAM 아키텍처입니다.**

- HBM은 여러 DRAM die를 TSV(Through-Silicon Via)로 쌓고, base die를 통해
  넓은 interface로 SoC와 연결합니다.
- 저장 셀 자체는 SDRAM/GDDR과 같은 **1T1C DRAM cell**입니다.
- HBM의 차이는 cell topology가 아니라 다음에 있습니다.
  - 3D stacking
  - TSV
  - very wide interface
  - channel / pseudo-channel 구조
  - base die / PHY
  - thermal/EM/IR 관리

따라서 이 문서의 "HBM cell"은 **HBM 규격을 가정한 1T1C 셀과 교육용 TSV/tile**을
의미합니다.

## 2. 이 프로젝트가 모델링하는 것

`hbm.py`는 다음을 생성합니다.

| 셀 | 내용 |
|---|---|
| `HBM3_CELL` | HBM-style 1T1C storage cell |
| `HBM3_PRECHARGE` | active-low PMOS precharge/equalize to VBL |
| `HBM3_SENSE` | cross-coupled sense amplifier |
| `HBM3_IO` | TSV 앞단 출력 버퍼 placeholder |
| `HBM3_TSV` | ideal TSV R + C 모델 |
| `HBM3_ARRAY_4X4` | 16개 cell array |
| `HBM3_TILE_4X4` | array + precharge + sense + IO + TSV |

실제 HBM stack, base die, PHY, channel controller는 포함하지 않습니다.
`HBM3_ARRAY_4X4`은 single-ended `BL`만 노출하고, tile의 `BLB`는
precharge/sense용 reference line입니다.

## 3. 회로 구조

```text
WL0..3
  |
  v
+---------------------+
| HBM3_ARRAY_4X4      |  BL0..3
| 16 x HBM3_CELL      |----+--> HBM3_SENSE --> HBM3_IO --> HBM3_TSV --> DQ0..3
+---------------------+    |
                           +--> HBM3_PRECHARGE (VBL, PRE)
```

`HBM3_TSV`는 다음 ideal model입니다.

```spice
.SUBCKT HBM3_TSV TOP BOTTOM VSS
R0 TOP BOTTOM 0.05
C0 BOTTOM VSS 20f
.ENDS
```

- `R0`: TSV series resistance
- `C0`: TSV-to-substrate capacitance
- 실제 TSV는 RLC, keep-out zone, substrate coupling, EM/IR을 포함해야 합니다.

## 4. 사이징

`hbm.py` 기본값:

| 항목 | 값 |
|---|---:|
| Access NMOS W | 150 nm |
| Access NMOS L | 45 nm |
| Storage C | 6 fF (ideal) |
| Precharge PMOS W | 180 nm |
| Sense PMOS/NMOS W | 240 nm |
| Sense tail W | 480 nm |
| TSV R | 0.05 Ω |
| TSV C | 20 fF |
| Array | 4×4 |

HBM은 cell 자체보다 **많은 수의 channel을 얼마나 넓고 짧게 연결하는가**가
핵심입니다. 위 값은 그 구조를 schematic으로 보여주기 위한 축소 모델입니다.

## 5. CDL 예시

`out/04_HBM/HBM3_CELL.cdl`:

```spice
.SUBCKT HBM3_CELL BL WL PLATE VSS
M0 BL WL SN VSS g45n1svt w=0.15u l=0.045u nf=1 m=1
C0 SN PLATE 6f
.ENDS
```

`out/04_HBM/HBM3_TILE_4X4.cdl`의 핵심 구조:

```spice
.SUBCKT HBM3_TILE_4X4 WL0 ... BL0 ... DQ0 ... PRE SAE VBL PLATE VDD VSS
XARR WL0 ... BL0 ... PLATE VSS HBM3_ARRAY_4X4
XPC0 BL0 BLB0 PRE VBL VDD HBM3_PRECHARGE
...
XSA0 BL0 BLB0 SAE VDD VSS HBM3_SENSE
...
XIO0 BL0 TSVIN0 VDD VSS HBM3_IO
XTSV0 TSVIN0 DQ0 VSS HBM3_TSV
...
.ENDS
```

## 6. Virtuoso import

```text
HBM3_CELL → HBM3_PRECHARGE → HBM3_SENSE → HBM3_IO
→ HBM3_TSV → HBM3_ARRAY_4X4 → HBM3_TILE_4X4
```

`HBM3_TSV`의 `R0`/`C0`는 ideal element입니다. PDK 또는 EM extractor가 제공하는
TSV model로 교체해야 합니다. `HBM3_IO`는 placeholder이므로 실제 HBM PHY의
driver/receiver로 교체하기 전에는 timing/level을 신뢰하면 안 됩니다.

## 7. HBM의 핵심 개념

### 7.1 Stack

여러 DRAM die를 수직으로 쌓습니다. 각 die는 TSV를 통해 base die와 연결됩니다.

### 7.2 Wide interface

HBM은 좁고 빠른 DQ 대신 **넓은 병렬 interface**를 사용합니다. 그래서 pin 수가
많고, channel 수가 많으며, 배선 길이와 skew 관리가 중요합니다.

### 7.3 Channel / pseudo-channel

HBM은 여러 channel로 나뉘고, 각 channel은 독립적으로 access할 수 있습니다.
실제 HBM3/HBM3E는 pseudo-channel, bank group, refresh 관리가 복잡하게 얽혀
있습니다. 이 프로젝트는 단일 4×4 tile만 모델링합니다.

### 7.4 TSV

TSV는 die 사이를 수직으로 연결합니다. TSV는 resistance, capacitance, inductance,
keep-out zone, stress, EM을 고려해야 합니다.

## 8. 검증 아이디어

- **TSV RC**: DQ slew/지연에 대한 R/C 영향
- **Read path**: sense → IO → TSV → DQ timing
- **Precharge**: `VBL` settling
- **Sense margin**: SAE 인가 시 BL/BLB 차이
- **Power/IR**: stack 전체 current와 TSV 전류 밀도

실제 HBM 검증에는 stack model, interposer/package model, thermal model,
IBIS/Verilog-A, channel simulation이 필요합니다.

## 9. 한계

- 실제 3D stack, base die, PHY, channel controller가 없습니다.
- TSV는 ideal R+C이며, RLC/EM/keep-out/thermal을 포함하지 않습니다.
- `HBM3_IO`는 inverter placeholder입니다.
- HBM3/HBM3E의 JEDEC timing, refresh, ECC, pseudo-channel protocol을 모델링하지
  않습니다.
- GPDK045는 HBM 공정이 아니므로 retention/refresh/thermal을 예측할 수 없습니다.
- layout/DRC/LVS는 포함하지 않습니다.

## 10. 확장 방향

1. multi-die stack과 TSV array 추가
2. channel/pseudo-channel controller behavioral model 추가
3. TSV RLC + keep-out + substrate coupling model 추가
4. interposer/package channel loss 추가
5. thermal/EM/IR co-simulation
6. HBM3E의 higher bandwidth/power model 비교
