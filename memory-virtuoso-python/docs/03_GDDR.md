# 03. GDDR — GDDR-style 1T1C tile

## 1. 먼저 구분할 것

**GDDR은 메모리 셀의 이름이 아니라 인터페이스/규격 이름입니다.**

- GDDR5, GDDR6, GDDR6X는 JEDEC 그래픽 DRAM 규격입니다.
- 저장 셀 자체는 SDRAM과 같은 **1T1C DRAM cell**입니다.
- GDDR의 차이는 cell topology가 아니라 다음에 있습니다.
  - 높은 DQ 데이터율
  - source-synchronous clocking
  - pre-emphasis/equalization
  - termination/calibration
  - GDDR6X의 PAM4 signaling
  - package/channel 구조

따라서 이 문서의 "GDDR cell"은 **GDDR 규격을 가정한 1T1C 셀과 교육용 tile**을
의미합니다.

## 2. 이 프로젝트가 모델링하는 것

`gddr.py`는 다음을 생성합니다.

| 셀 | 내용 |
|---|---|
| `GDDR6_CELL` | GDDR-style 1T1C storage cell |
| `GDDR6_PRECHARGE` | active-low PMOS precharge/equalize to VBL |
| `GDDR6_SENSE` | cross-coupled sense amplifier |
| `GDDR6_IO` | 단순 DQ 출력 버퍼 placeholder |
| `GDDR6_ARRAY_4X4` | 16개 cell array |
| `GDDR6_TILE_4X4` | array + precharge + sense + DQ buffer |

`GDDR6_TILE_4X4`은 실제 GDDR PHY가 아니라, **cell array에서 DQ pad까지의
개념적 read path**를 보여주는 축소 모델입니다. `GDDR6_ARRAY_4X4`은 single-ended
`BL`만 노출하고, tile의 `BLB`는 precharge/sense용 reference line입니다.

## 3. 회로 구조

```text
WL0..3
  |
  v
+---------------------+
| GDDR6_ARRAY_4X4     |  BL0..3
| 16 x GDDR6_CELL     |--------+-----> GDDR6_SENSE ---> GDDR6_IO ---> DQ0..3
+---------------------+        |
                               +-----> GDDR6_PRECHARGE
                                      (VBL, PRE)
```

각 column은 다음 순서로 동작합니다.

1. `PRE=0`으로 BL/BLB를 `VBL`로 precharge/equalize
2. `WL=1`로 access NMOS on
3. BL 전압 변화
4. `SAE=1`로 sense amp 증폭
5. `GDDR6_IO`가 DQ로 출력

`GDDR6_IO`는 inverter 하나입니다. 실제 GDDR DQ driver는 pre-driver, slew rate
control, termination, equalization, ESD를 포함합니다.

## 4. 사이징

`gddr.py` 기본값:

| 항목 | 값 |
|---|---:|
| Access NMOS W | 150 nm |
| Access NMOS L | 45 nm |
| Storage C | 8 fF (ideal) |
| Precharge PMOS W | 180 nm |
| Sense PMOS/NMOS W | 240 nm |
| Sense tail W | 480 nm |
| DQ buffer PMOS/NMOS | 240/120 nm |
| Array | 4×4 |

SDRAM 문서의 1T1C와 동일한 topology이며, access width와 capacitor 값을
조금 다르게 두어 GDDR-style tile임을 구분했습니다. 이 값은 성능을 의미하지
않습니다.

## 5. CDL 예시

`out/03_GDDR/GDDR6_CELL.cdl`:

```spice
.SUBCKT GDDR6_CELL BL WL PLATE VSS
M0 BL WL SN VSS g45n1svt w=0.15u l=0.045u nf=1 m=1
C0 SN PLATE 8f
.ENDS
```

`out/03_GDDR/GDDR6_TILE_4X4.cdl`:

```spice
.SUBCKT GDDR6_TILE_4X4 WL0 WL1 WL2 WL3 BL0 ... DQ0 ... PRE SAE VBL PLATE VDD VSS
XARR WL0 ... BL0 ... PLATE VSS GDDR6_ARRAY_4X4
XPC0 BL0 BLB0 PRE VBL VDD GDDR6_PRECHARGE
...
XSA0 BL0 BLB0 SAE VDD VSS GDDR6_SENSE
...
XIO0 BL0 DQ0 VDD VSS GDDR6_IO
...
.ENDS
```

`...`는 문서에서 생략한 pin을 의미합니다. 실제 파일은 모든 pin을 명시합니다.

## 6. Virtuoso import

```text
GDDR6_CELL → GDDR6_PRECHARGE → GDDR6_SENSE → GDDR6_IO
→ GDDR6_ARRAY_4X4 → GDDR6_TILE_4X4
```

`C0`는 PDK capacitor로 교체해야 합니다. `GDDR6_IO`는 placeholder이므로 실제
GDDR driver로 교체하기 전에는 timing/level을 신뢰하면 안 됩니다.

## 7. GDDR6와 GDDR6X

- **GDDR6**: NRZ signaling, 높은 DQ rate, 여러 channel 구조.
- **GDDR6X**: PAM4 signaling으로 더 높은 data rate를 목표로 합니다.

PAM4는 한 symbol에 2 bit를 실어 보내므로 TX/RX에 DAC/ADC, linearity,
equalization이 필요합니다. 이 프로젝트는 PAM4를 모델링하지 않습니다.

## 8. 검증 아이디어

- **Read path**: WL/SAE timing에 따른 DQ 출력
- **Precharge**: `VBL` settling
- **Sense margin**: SAE 인가 시 BL/BLB 차이
- **DQ swing**: `GDDR6_IO` 출력 swing
- **Power**: array + sense + IO 전류

실제 GDDR 검증에는 IBIS/Verilog-A 모델, channel loss, package model, jitter,
BER 분석이 필요합니다.

## 9. 한계

- GDDR PHY, PLL, WCK, DQ training, equalization, termination, ESD가 없습니다.
- `GDDR6_IO`는 inverter placeholder입니다.
- 4×4 tile은 교육용 축소 모델이며, 실제 GDDR channel 폭/ prefetch/ bank 구조와
  다릅니다.
- GPDK045는 그래픽 DRAM 공정이 아니므로 retention/refresh를 예측할 수
  없습니다.
- layout/DRC/LVS는 포함하지 않습니다.

## 10. 확장 방향

1. differential DQ와 true output driver 추가
2. pre-emphasis/equalization을 behavioral Verilog-A로 모델링
3. column mux와 burst prefetch 추가
4. GDDR6X PAM4 TX/RX behavioral model 추가
5. channel/package loss를 포함한 IBIS-AMI 검증
