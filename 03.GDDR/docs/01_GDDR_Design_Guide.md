# GDDR 메모리 설계 가이드

## 1. 개요

GDDR(Graphics Double Data Rate) SDRAM은 그래픽카드와 AI 가속기를 위한 고대역폭 메모리입니다.
일반 DDR과 동일한 1T1C 셀 구조를 공유하지만, **초고속 I/O, 멀티 채널, PAM4 시그널링**을 특징으로 합니다.

---

## 2. GDDR 세대별 비교

### 2.1 종합 비교표

| 항목 | GDDR5 | GDDR6 | GDDR6X |
|------|-------|-------|--------|
| **년도** | 2008 | 2018 | 2020 |
| **공정** | 60~90nm | 10~14nm | 8~10nm |
| **소자** | Planar / Early High-k | High-k / Deep BCAT | EUV-BCAT / FinFET |
| **셀 구조** | 1T1C Cylinder | 1T1C Ultra-HAR | 1T1C PAM4 Driver |
| **시그널링** | NRZ | NRZ | **PAM4** |
| 데이터 레이트 | 4~6 Gbps/pin | 8~16 Gbps/pin | 19~21 Gbps/pin |
| 동작 전압 | 1.5V | 1.25~1.35V | 1.2~1.35V |
| 채널 구조 | 단일 32-bit | 듀얼 16-bit | 듀얼 16-bit |
| 프리페치 | 8n | 16n | 16n |
| 대역폭 | 108~192 GB/s | 256~672 GB/s | 1,000+ GB/s |
| 패키징 | BGA 170 | BGA 180 | BGA 180 |
| 특징 | WCK 클럭, EDC | 저전력 모드 | PAM4, 1TB/s |

### 2.2 셀 구조 비교

모든 GDDR 세대는 1T1C 기본 구조를 공유합니다:

```
     ┌──────────┐
     │ HAR Cap  │  ← 커패시터 (고밀도 확보)
     └────┬─────┘
          │
     BL ──┤
          │
     ┌────┴─────┐
     │ BCAT     │  ← 매립형 채널 트랜지스터
     └────┬─────┘
          │
     WL ──┘
```

---

## 3. 세대별 설계 파라미터

### 3.1 GDDR5 (2008)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  60~90nm
소자 구조              Planar / Early High-k
동작 전압 (VDD)       1.5V
I/O 전압 (VDDQ)       1.5V
셀 구조                1T1C (Advanced Cylinder)
트랜지스터             RCAT (Recess Channel)
데이터 레이트          4~6 Gbps/pin
프리페치               4n/8n
버스 폭                256~384-bit
대역폭                 108~192 GB/s
뱅크 수                16
뱅크 그룹              4
채널 / 시그널링        단일 32-bit / NRZ
패키징                 BGA 170-ball
```

**핵심 기술:**
- **WCK/CK 분리 클럭**: 커맨드/어드레스용 CK와 데이터용 WCK를 이원화
- **EDC (Error Detection Code)**: 데이터 무결성 검사
- **RCAT (Recess Channel Array Transistor)**: 오목형 채널 트랜지스터

### 3.2 GDDR6 (2018)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  10~14nm
소자 구조              High-k / FinFET
동작 전압 (VDD)       1.25V
I/O 전압 (VDDQ)       1.35V
셀 구조                1T1C (Deep BCAT + Ultra HAR)
트랜지스터             Deep BCAT
데이터 레이트          8~16 Gbps/pin
프리페치               16n
버스 폭                단일 스택 기준
대역폭                 256~672 GB/s
뱅크 수                16
뱅크 그룹              4
채널 / 시그널링        듀얼 16-bit / NRZ
패키징                 BGA 180-ball
```

**핵심 기술:**
- **Dual 16-bit Subchannel**: 칩을 2개의 독립 16-bit 채널로 분리
- **Deep BCAT**: 10nm급 누설 전류 극복
- **저전력 VDD/VDDQ 모드**

### 3.3 GDDR6X (2020)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  8~10nm
소자 구조              Advanced FinFET / EUV
동작 전압 (VDD)       1.2V
I/O 전압 (VDDQ)       1.35V
셀 구조                1T1C (EUV-BCAT + PAM4)
데이터 레이트          19~21 Gbps/pin
시그널링               PAM4 (4-Level)
대역폭                 1,000+ GB/s
뱅크 수                16
뱅크 그룹              4
채널 / 시그널링        듀얼 16-bit / PAM4
패키징                 BGA 180-ball
```

**핵심 기술:**
- **PAM4 시그널링**: 동일 주파수에서 2배 데이터 전송
- **EUV-BCAT**: 극자외선 리소그래피 적용
- **노이즈 억제 설계**: PAM4 눈 마진 보상

---

## 4. I/O 시그널링 기술 비교

### 4.1 NRZ vs PAM4

```
NRZ (GDDR5/GDDR6)              PAM4 (GDDR6X)
─────────────────────          ─────────────────────
  VDD ─┐                     VDD   ─┐  V11 (11)
       ├── 1                     ───┼  V10 (10)  ← Eye 3
  GND ─┘                         ───┼  V01 (01)  ← Eye 2
       1 bit / period              ───┼  V00 (00)  ← Eye 1
                                  GND ─┘
                                  2 bits / period

반송 주파수 동일 시:
- NRZ:   1 bit/cycle
- PAM4:  2 bits/cycle → 2배 대역폭
```

### 4.2 PAM4 레벨 설계

```
PAM4 4-레벨 매핑 (MSB/LSB):
  00 → V00 = VSS (0V)
  01 → V01 = Vswing/3
  10 → V10 = 2×Vswing/3
  11 → V11 = Vswing

레퍼런스 전압:
  VREF1 = Vswing/6 (00 vs 01 판별)
  VREF2 = Vswing/2 (01 vs 10 판별)
  VREF3 = 5×Vswing/6 (10 vs 11 판별)

눈 마진 감소 문제:
  NRZ:   Eye = Vswing (전 스윙)
  PAM4:  Eye = Vswing/3 (스윙의 1/3)
  → 노이즈 억제 설계 필수
```

---

## 5. 채널 아키텍처 비교

### 5.1 GDDR5: 단일 32-bit 채널

```
┌─────────────────────────────────┐
│                                 │
│      ┌───────────────────┐      │
│      │   Bank 0..15      │      │
│      │   (32-bit)        │      │
│      └───────────────────┘      │
│                                 │
│  DQ[0:31] ─── 1채널             │
│  DQS, WCK                       │
└─────────────────────────────────┘
```

### 5.2 GDDR6/GDDR6X: 듀얼 16-bit 채널

```
┌──────────────────────────────────────┐
│                                      │
│  ┌────────────────┬────────────────┐ │
│  │  Channel A     │  Channel B     │ │
│  │  (16-bit)      │  (16-bit)      │ │
│  │  A_DQ[0:15]    │  B_DQ[0:15]    │ │
│  │  A_CMD/ADDR    │  B_CMD/ADDR    │ │
│  │  A_WCK         │  B_WCK         │ │
│  └────────────────┴────────────────┘ │
│           ← 물리적 분리 벽 →          │
└──────────────────────────────────────┘

장점:
- 채널별 독립 커맨드/어드레스 → 버스 효율 향상
- 병렬 액세스 가능 → 대역폭 유연성
- 한 채널 로딩 중 다른 채널 동작 가능
```

---

## 6. Virtuoso 설계 자동화

### 6.1 SKILL 스크립트 실행

```skill
; Virtuoso CIW에서 실행

; 1. GDDR5 어레이 (16뱅크, 4뱅크그룹, 32-bit)
gddrCreateArray("gddr_lib" "gddr5_array" "GDDR5" 16 4 32)

; 2. GDDR6 듀얼 채널
gddrCreateArray("gddr_lib" "gddr6_array" "GDDR6" 16 4 16)
gddrCreateDualChannel("gddr_lib" "gddr6_channels" 16)

; 3. GDDR6X PAM4 I/O 회로
gddrCreatePAM4IO("gddr_lib" "gddr6x_pam4_io")

; 4. GDDR6 NRZ I/O 회로
gddrCreateIOCircuit("gddr_lib" "gddr6_io" "GDDR6")

; 5. 클럭 트리 (2 PLL, 4 WCK)
gddrCreateClockTree("gddr_lib" "gddr_clock" 2 4)
```

### 6.2 Python 제너레이터 실행

```bash
cd 03.GDDR/scripts
python gddr_cell_generator.py
```

생성 파일:
```
generated/
├── gddr_gddr5_array.skill
├── gddr_gddr5_io_driver.skill
├── gddr_gddr6_array.skill
├── gddr_gddr6_io_driver.skill
├── gddr_gddr6x_array.skill
├── gddr_gddr6x_io_driver.skill
├── pam4_encoder.skill
└── gddr_configs.json
```

---

## 7. 성능 분석 모델

### 7.1 대역폭 계산

```
대역폭 = 데이터레이트 × 버스폭 / 8

GDDR5:  6 Gbps × 256-bit / 8 = 192 GB/s
GDDR6: 16 Gbps × 336-bit / 8 = 672 GB/s
GDDR6X: 21 Gbps × 384-bit / 8 = 1,008 GB/s
```

### 7.2 눈 다이어그램 마진

```
신호 품질 지표 (Eye Margin):

NRZ GDDR6:
  Vswing = 0.6V
  Eye = 0.6V (전 스윙)

PAM4 GDDR6X:
  Vswing = 0.5V
  Eye = 0.5V / 3 = 0.167V (스윙의 1/3)
  → NRZ 대비 3배 작은 마진 → 노이즈 제어 필수
```

---

## 8. 참고 자료

- JEDEC GDDR5/GDDR6/GDDR6X Standards
- "GDDR6X: PAM4 for Graphics" (NVIDIA/Micron)
- Cadence Virtuoso SerDes Design Guide
- IEEE ISSCC GDDR 논문
