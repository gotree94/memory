# 02. SDRAM — 1T1C cell과 8x8 tile

## 1. 개요

SDRAM의 저장 셀은 **1T1C**입니다. access transistor 1개와 storage capacitor
1개로 이루어집니다.

```text
             WL
              |
  BL --- M0 --+--- SN --- C0 --- PLATE
                    |
                   VSS (M0 bulk)
```

- `WL=1`이면 M0가 켜져 BL과 SN이 연결됩니다.
- `C0`에 전하가 저장됩니다.
- `PLATE`는 cell plate 전압입니다.
- 읽기는 SN의 전하를 BL로 공유시키는 **destructive read**입니다.
- 읽은 뒤 sense amplifier가 값을 복원해야 합니다.

## 2. 왜 1T1C인가

DRAM은 SRAM보다 셀 면적이 작아야 하므로 cross-coupled inverter를 쓰지 않습니다.
대신 capacitor에 전하를 저장합니다.

| 항목 | SRAM 6T | DRAM 1T1C |
|---|---|---|
| 저장 방식 | cross-coupled latch | capacitor charge |
| 셀 소자 | 6 transistors | 1 transistor + 1 capacitor |
| 속도 | 빠름 | 상대적으로 느림 |
| refresh | 불필요 | 필요 |
| 공정 | logic/CMOS | DRAM capacitor 공정 |

GPDK045는 **로직 PDK**이므로 deep-trench/stack capacitor가 없습니다. 이
프로젝트의 `C0`는 `10f` ideal capacitor이며, retention/refresh를 예측하는
용도가 아닙니다.

## 3. 사이징

`sdram.py` 기본값:

| 항목 | 값 | 비고 |
|---|---:|---|
| Access NMOS W | 180 nm | `DRAM1T1C` |
| Access NMOS L | 45 nm | GPDK045 |
| Storage C | 10 fF | ideal |
| Precharge PMOS W | 180 nm | active-low |
| Sense PMOS/NMOS W | 240 nm | tail 480 nm |
| Array | 8×8 | 64 cells |

실제 DRAM은 capacitor capacitance를 크게 하고 access transistor의 off-leakage를
줄여 retention을 확보합니다. 위 값은 교육용입니다.

## 4. 동작

### 4.1 Precharge

`DRAM_PRECHARGE`는 active-low PMOS 3개로 BL/BLB를 `VBL`로 precharge하고
equalize합니다.

```text
PRE=0  -> PMOS on  -> BL/BLB = VBL
PRE=1  -> PMOS off
```

NMOS pass gate를 쓰면 `VBL - Vth`까지만 충전되므로, 이 모델은 PMOS를 사용합니다.
실제 SDRAM은 `VBL = VDD/2` generator와 reference scheme이 필요합니다.

### 4.2 Read

1. BL/BLB를 `VBL`로 precharge합니다.
2. `WL=1`로 access NMOS를 켭니다.
3. SN의 전하가 BL로 공유되어 BL 전압이 미세하게 변합니다.
4. `SAE=1`로 sense amp를 켜 BL/BLB 차이를 full swing으로 증폭합니다.
5. 증폭된 값을 다시 SN에 restore합니다.

### 4.3 Write

1. BL/BLB에 쓸 값을 인가합니다.
2. `WL=1`로 access NMOS를 켭니다.
3. BL 전압이 SN capacitor를 충전/방전합니다.
4. `WL=0`으로 닫으면 값이 저장됩니다.

### 4.4 Refresh

capacitor는 leakage로 전하를 잃습니다. SDRAM은 주기적으로 read + restore를
수행합니다. 이 프로젝트에는 refresh controller가 없습니다.

## 5. 생성되는 셀

| 셀 | 내용 |
|---|---|
| `DRAM1T1C` | 1T1C storage cell |
| `DRAM_PRECHARGE` | active-low PMOS precharge/equalize to VBL |
| `DRAM_SENSE` | cross-coupled sense amp + SAE tail |
| `SDRAM_ARRAY_8X8` | 64개 1T1C cell |
| `SDRAM_TILE_8X8` | array + 8 precharge + 8 sense amp |

`SDRAM_ARRAY_8X8`은 single-ended `BL`만 노출합니다. `SDRAM_TILE_8X8`의 `BLB`는
precharge/sense용 reference line이며 array cell에는 연결되지 않습니다.

CDL In 순서:

```text
DRAM1T1C → DRAM_PRECHARGE → DRAM_SENSE → SDRAM_ARRAY_8X8 → SDRAM_TILE_8X8
```

## 6. CDL 예시

`out/02_SDRAM/DRAM1T1C.cdl`:

```spice
.SUBCKT DRAM1T1C BL WL PLATE VSS
M0 BL WL SN VSS g45n1svt w=0.18u l=0.045u nf=1 m=1
C0 SN PLATE 10f
.ENDS
```

`out/02_SDRAM/SDRAM_TILE_8X8.cdl`의 핵심 구조:

```spice
.SUBCKT SDRAM_TILE_8X8 WL0 ... WL7 BL0 ... BL7 BLB0 ... BLB7 PRE SAE VBL PLATE VDD VSS
XARR WL0 ... WL7 BL0 ... BL7 PLATE VSS SDRAM_ARRAY_8X8
XPC0 BL0 BLB0 PRE VBL VDD DRAM_PRECHARGE
...
XSA0 BL0 BLB0 SAE VDD VSS DRAM_SENSE
...
.ENDS
```

`...`는 문서에서 생략한 pin을 의미합니다. 생성 파일은 한 줄에 한 instance를
사용하며, 실제 pin은 모두 명시됩니다.

## 7. Virtuoso import

```text
File > Import > CDL
Input File: out/02_SDRAM/DRAM1T1C.cdl
Target Library: MEMORY45
```

`C0`가 `cap` 또는 `mimcap`으로 매핑되는지 확인하세요. PDK에 MIM/MOM capacitor가
있다면 `C0`를 해당 소자로 교체하고 capacitance를 다시 설정해야 합니다.
`PLATE`, `VBL`은 전압원/testbench에서 인가합니다.

## 8. Spectre 검증 아이디어

- **Charge sharing**: WL pulse 후 BL 전압 변화량 `ΔV = Ccell/(Ccell+CBL) × (VSN - VBL)`
- **Sense margin**: SAE 인가 시점의 BL/BLB 차이
- **Restore**: sense 후 SN이 full swing으로 복원되는지
- **Retention**: WL=0에서 SN droop (ideal C에서는 leakage 모델이 없으므로
  PDK 소자 leakage를 별도로 봐야 함)
- **Power**: precharge/sense/refresh 전류

## 9. 한계

- GPDK045에는 실제 DRAM capacitor가 없습니다. `C0`는 ideal element입니다.
- `VBL=VDD/2` generator, reference cell, row/column decoder, refresh controller가
  없습니다.
- 1T1C의 destructive read/restore를 schematic 수준에서만 보여줍니다.
- layout/DRC/LVS는 포함하지 않습니다. DRAM bitcell은 로직 PDK의 DRC로
  그대로 검증할 수 없습니다.
- SDRAM 표준의 timing/command protocol(JEDEC)은 모델링하지 않습니다.
