# 01. SRAM — 6T bitcell과 8x8 tile

## 1. 개요

SRAM은 cross-coupled inverter로 bit를 저장하고, access transistor로 bitline에
연결하는 메모리입니다. 이 프로젝트는 가장 기본적인 **6T SRAM bitcell**과
교육용 **8x8 array/tile**을 Python으로 CDL 생성합니다.

6T 셀의 6개 transistor:

| 소자 | 역할 |
|---|---|
| MP0, MP1 | pull-up PMOS, cross-coupled inverter |
| MN0, MN1 | pull-down NMOS, cross-coupled inverter |
| MN2, MN3 | access NMOS, WL로 BL/BLB 연결 |

## 2. 회로도

```text
             VDD                     VDD
              |                       |
            MP0                     MP1
              |                       |
   BL -- MN2 --+------ Q === QB ------+-- MN3 -- BLB
              |                       |
            MN0                     MN1
              |                       |
             VSS                     VSS
```

- `Q`와 `QB`가 저장 노드입니다.
- `WL=1`이면 MN2/MN3가 켜져 BL/BLB와 Q/QB가 연결됩니다.
- `WL=0`이면 셀은 cross-coupled inverter만으로 값을 유지합니다.

## 3. 사이징

`sram.py`의 기본값:

| 소자 | W | L | 이유 |
|---|---:|---:|---|
| Pull-down MN0/MN1 | 240 nm | 45 nm | read 중 Q를 VSS로 강하게 잡아 flip 방지 |
| Pull-up MP0/MP1 | 120 nm | 45 nm | PMOS 이동도 보상, cell ratio 확보 |
| Access MN2/MN3 | 180 nm | 45 nm | writeability와 read stability의 절충 |

β ratio(대략 pull-down/access)는 `240/180 = 1.33`입니다. 실제 셀은
cell ratio `β_pd/β_access ≈ 1.2~2.0`, pull-up ratio `β_pu/β_access ≈ 1.0~1.5`
범위에서 Monte Carlo로 조정합니다. 위 값은 교육용 출발점일 뿐입니다.

## 4. 읽기/쓰기 동작

### 4.1 Standby

- `WL=0`
- access NMOS off
- cross-coupled inverter가 Q/QB를 유지
- leakage가 retention 시간을 결정

### 4.2 Read

1. BL/BLB를 precharge/equalize합니다 (`SRAM_PRECHARGE`).
2. `WL=1`로 access NMOS를 켭니다.
3. Q=0인 쪽 bitline이 access NMOS + pull-down을 통해 방전됩니다.
4. BL/BLB의 작은 차이를 sense amplifier가 증폭합니다.
5. `SAE=1`로 sense amp tail을 켜면 cross-coupled latch가 full swing으로
   증폭합니다.

Read 중 Q=0 노드는 access NMOS와 pull-down NMOS가 VDD→BL→Q→VSS 경로를
만들 수 있습니다. pull-down이 충분히 강해야 Q가 1로 flip되지 않습니다.

### 4.3 Write

1. BL/BLB에 쓸 값을 강제로 인가합니다.
2. `WL=1`로 access NMOS를 켭니다.
3. access NMOS가 cross-coupled inverter의 feedback을 이겨 Q/QB를 뒤집습니다.
4. `WL=0`으로 닫으면 새 값이 유지됩니다.

Write margin은 access NMOS가 pull-up PMOS보다 충분히 강해야 확보됩니다.

## 5. 생성되는 셀

| 셀 | 내용 |
|---|---|
| `SRAM6T` | 6T bitcell |
| `SRAM_PRECHARGE` | BL/BLB precharge + equalize |
| `SRAM_SENSE` | cross-coupled sense amp + SAE tail |
| `SRAM_ARRAY_8X8` | 64개 bitcell, WL/BL/BLB pin |
| `SRAM_TILE_8X8` | array + 8 precharge + 8 sense amp |

`SRAM_TILE_8X8`은 `SRAM_ARRAY_8X8`을 `XARR`로 참조합니다. 따라서 CDL In에서는
`SRAM6T → SRAM_PRECHARGE → SRAM_SENSE → SRAM_ARRAY_8X8 → SRAM_TILE_8X8`
순서로 import합니다.

## 6. CDL 예시

`out/01_SRAM/SRAM6T.cdl`:

```spice
.SUBCKT SRAM6T BL BLB WL VDD VSS
MP0 Q QB VDD VDD g45p1svt w=0.12u l=0.045u nf=1 m=1
MP1 QB Q VDD VDD g45p1svt w=0.12u l=0.045u nf=1 m=1
MN0 Q QB VSS VSS g45n1svt w=0.24u l=0.045u nf=1 m=1
MN1 QB Q VSS VSS g45n1svt w=0.24u l=0.045u nf=1 m=1
MN2 BL WL Q VSS g45n1svt w=0.18u l=0.045u nf=1 m=1
MN3 BLB WL QB VSS g45n1svt w=0.18u l=0.045u nf=1 m=1
.ENDS
```

Precharge는 active-low PMOS 3개로 구성됩니다.

```spice
.SUBCKT SRAM_PRECHARGE BL BLB PRE VDD
MP0 BL PRE VDD VDD g45p1svt w=0.12u l=0.045u nf=1 m=1
MP1 BLB PRE VDD VDD g45p1svt w=0.12u l=0.045u nf=1 m=1
MP2 BL BLB VDD VDD g45p1svt w=0.12u l=0.045u nf=1 m=1
.ENDS
```

## 7. Virtuoso import

```text
File > Import > CDL
Input File: out/01_SRAM/SRAM6T.cdl
Target Library: MEMORY45
```

`SRAM_TILE_8X8`을 import하려면 `SRAM_ARRAY_8X8`, `SRAM_PRECHARGE`,
`SRAM_SENSE`가 같은 라이브러리에 먼저 있어야 합니다.

## 8. Spectre 검증 아이디어

- **Read margin**: WL pulse 후 BL/BLB 차이를 sense amp 입력 전에 측정
- **Write margin**: BL/BLB를 반대로 구동했을 때 Q/QB가 뒤집히는 최소 시간
- **Hold margin**: WL=0에서 Q/QB가 유지되는지, leakage로 droop이 얼마인지
- **Access disturb**: read 중 Q=0 노드의 bump 전압
- **Power**: read/write/standby 평균 전류

testbench에서는 `SRAM6T`에 `WL`, `BL`, `BLB`를 직접 인가하고, `VDD=1.0 V`
(또는 PDK가 요구하는 전압)로 시작하세요. GPDK045 모델 코너는 `tt`부터
확인하는 것이 일반적입니다.

## 9. 한계

- 6T 셀은 read/write margin이 작고, 실제로는 8T/10T 또는 write-assist가
  사용되는 경우가 많습니다.
- 이 프로젝트에는 row decoder, write driver, column mux, redundancy, ECC가
  없습니다.
- layout/DRC/LVS는 포함하지 않습니다. 45 nm bitcell layout은 별도의
  design-rule 작업이 필요합니다.
- GPDK045는 로직 PDK이므로 실제 SRAM compiler의 bitcell과 동일하지 않습니다.
