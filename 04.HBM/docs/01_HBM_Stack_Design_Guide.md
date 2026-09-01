# HBM 메모리 3D 적층 설계 가이드

## 1. 개요

HBM(High Bandwidth Memory)은 AI/HPC 가속기를 위한 초고대역폭 3D 적층 메모리입니다.
개별 DRAM 코어 다이(Core Die) 위에 **TSV, Microbump, Base Die, 실리콘 인터포저** 패키징 기술을
결합하여 1TB/s급 대역폭을 구현합니다.

---

## 2. HBM 세대별 비교

### 2.1 종합 비교표

| 항목 | HBM1 | HBM2 | HBM2E | HBM3 | HBM3E |
|------|------|------|-------|------|-------|
| **년도** | 2013 | 2016 | 2020 | 2022 | 2024 |
| 공정 | 28nm | 20~28nm | 10nm | 10nm(EUV) | 10nm(1α/β) |
| 적층 | 4-Hi | 4/8-Hi | 4/8/12-Hi | 8/12/16-Hi | 8/12-Hi |
| 채널 | 8x128-bit | Pseudo 2x512 | Pseudo 2x512 | 16x64-bit | 16x64-bit |
| 버스 | 1024-bit | 1024-bit | 1024-bit | 1024-bit | 1024-bit |
| 핀당 속도 | 1.0 Gbps | 2.0 Gbps | 3.6 Gbps | 6.4 Gbps | 9.2 Gbps |
| 대역폭 | 128 GB/s | 256 GB/s | 600 GB/s | 1,000 GB/s | 1,200 GB/s |
| 용량 | 1 GB | 2~8 GB | 4~24 GB | 8~64 GB | 24~48 GB |
| ECC | - | 지원 | 지원 | ODECC | ODECC |
| 패키징 | TSV+Bump | +Thermal | Adv. Bump | NCF | **MR-MUF** |

### 2.2 3D 적층 구조

```
        ┌─────────────────────────────┐
        │  Core Die 3 (DRAM)    ┌───┐ │
        │  ┌────────────────────┼TSV│ │
        │  │ 1T1C Cell Array    ├───┤ │
        │  └────────────────────┼TSV│ │
        └───────────────────────┼───┼─┘
        ┌───────────────────────┼───┼─┐
        │  Core Die 2 (DRAM)    ├───┤ │
        │  ┌────────────────────┼TSV│ │
        │  │ 1T1C Cell Array    ├───┤ │
        │  └────────────────────┼TSV│ │
        └───────────────────────┼───┼─┘
        ┌───────────────────────┼───┼─┐
        │  Core Die 1 (DRAM)    ├───┤ │
        │  ┌────────────────────┼TSV│ │
        │  │ 1T1C Cell Array    ├───┤ │
        │  └────────────────────┼TSV│ │
        └───────────────────────┼───┼─┘
        ┌───────────────────────┼───┼─┐
        │  Core Die 0 (DRAM)    ├───┤ │
        │  ┌────────────────────┼TSV│ │
        │  │ 1T1C Cell Array    ├───┤ │
        │  └────────────────────┼TSV│ │
        └───────────────────────┼───┼─┘
             ════════════════════╪═══╪════
             Microbump           │   │
        ┌───────────────────────┼───┼────┐
        │  Base Die (Logic)     ├───┤    │
        │  PHY │ Controller │   └───┘    │
        └──────────────┬─────────────────┘
                       ↓
           [Silicon Interposer]
                       ↓
             [Package Substrate]
```

---

## 3. 세대별 설계 파라미터

### 3.1 HBM1 (2013)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  28nm
적층                  4-Hi
다이 두께             50μm
TSV 지름              10μm
TSV 피치              40μm
TSV/다이              5,000
Microbump 피치        40μm
채널                  8 x 128-bit
버스                  1024-bit
데이터 레이트          1.0 Gbps/pin
대역폭                128 GB/s
용량                  1 GB (4Gb x 4)
패키징                2.5D 실리콘 인터포저
```

**핵심 기술:**
- 최초의 3D 적층 메모리
- 1024-bit 극대역 폭 I/O
- Base Die (Buffer Die) 최초 적용

### 3.2 HBM2 (2016)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  20~28nm
적층                  4~8-Hi
다이 두께             40μm
TSV 지름              8μm
TSV 피치              36μm
TSV/다이              6,000
채널                  Pseudo 2x512-bit
데이터 레이트          2.0 Gbps/pin
대역폭                256 GB/s
용량                  2~8 GB
ECC                   지원
```

**핵심 기술:**
- **Pseudo Channel**: 1024-bit를 2x512-bit로 분할
- 버스 효율 및 Command/Address 효율성 향상
- Thermal Shield 패키징

### 3.3 HBM2E (2020)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  10nm (1x/1y)
적층                  4/8/12-Hi
다이 두께             35μm
TSV 지름              6μm
TSV 피치              32μm
TSV/다이              8,000
데이터 레이트          3.6 Gbps/pin
대역폭                600 GB/s
용량                  4~24 GB
패키징                Advanced 2.5D
```

**핵심 기술:**
- 12-Hi 고집적 적층
- 범프 간격(Pitch) 미세화
- 초고속/고용량 AI 가속기용

### 3.4 HBM3 (2022)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  10nm (1α/EUV)
적층                  8/12/16-Hi
다이 두께             30μm
TSV 지름              5μm
TSV 피치              28μm
TSV/다이              10,000
채널                  16 x 64-bit
데이터 레이트          6.4 Gbps/pin
대역폭                819 GB/s ~ 1 TB/s
용량                  8~64 GB
ECC                   On-Die ECC (ODECC)
패키징                NCF
```

**핵심 기술:**
- **16 채널 아키텍처** (채널당 64-bit)
- **On-Die ECC** 내장
- NCF(Non-Conductive Film) 패키징

### 3.5 HBM3E (2024)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  10nm (1α/1β)
적층                  8/12-Hi
다이 두께             25μm
TSV 지름              4μm
TSV 피치              25μm
TSV/다이              12,000
채널                  16 x 64-bit
데이터 레이트          9.2 Gbps/pin
대역폭                1.15 ~ 1.2 TB/s
용량                  24~48 GB
패키징                MR-MUF
```

**핵심 기술:**
- **MR-MUF** (Mass Reflow Molded Underfill)
- 방열 성능 2.5배 향상
- **Custom Base Die** (파운드리 로직 공정 기반)

---

## 4. 채널 아키텍처 비교

### 4.1 HBM1: 8채널

```
                    1024-bit (8 x 128-bit)
┌─────────────────────────────────────────────┐
│  CH0   CH1   CH2   CH3   CH4   CH5   CH6   CH7 │
│  128b  128b  128b  128b  128b  128b  128b  128b │
└─────────────────────────────────────────────┘
        각 채널: 128-bit 데이터 + 독립 CMD/ADDR
```

### 4.2 HBM2/HBM2E: Pseudo Channel

```
        1024-bit = 2 x Pseudo Channel (512-bit)
┌───────────────────────────────────────┐
│  PCH0 (512-bit)      PCH1 (512-bit)   │
│  ┌──────────┐        ┌──────────┐     │
│  │ 4x128-bit│        │ 4x128-bit│     │
│  └──────────┘        └──────────┘     │
└───────────────────────────────────────┘
  장점: 읽기/쓰기 동시, 대기배터 감소
```

### 4.3 HBM3/HBM3E: 16채널

```
        1024-bit = 16 x 64-bit
┌──────────────────────────────────────────────┐
│ CH0 CH1 CH2 CH3 ... CH12 CH13 CH14 CH15      │
│ 64b 64b 64b 64b      64b   64b   64b   64b   │
└──────────────────────────────────────────────┘
  16개 독립 채널 → 다중 워크로드 병렬 액세스
  AI 학습/추론 병렬성 극대화
```

---

## 5. TSV 설계

### 5.1 TSV 구조

```
     ┌──────────────────┐
     │   Metal Pad      │
     ├──────────────────┤
     │   Copper Fill    │  ← Cu 전극
     ├──────────────────┤
     │   Insulation     │  ← SiO₂/바리어 (전기 격리)
     ├──────────────────┤
     │                  │
     │   Silicon Die    │  ← 실리콘 기판 관통
     │                  │
     └──────────────────┘

TSV 주요 파라미터:
- 지름(Diameter): 4~10μm
- 피치(Pitch): 25~40μm
- 종횡비: 5~10:1
- 다이 두께: 25~50μm
```

### 5.2 TSV 파라미터와 성능

| 파라미터 | HBM1 | HBM2 | HBM2E | HBM3 | HBM3E |
|----------|------|------|-------|------|-------|
| TSV 지름 | 10μm | 8μm | 6μm | 5μm | 4μm |
| TSV 피치 | 40μm | 36μm | 32μm | 28μm | 25μm |
| TSV/다이 | 5,000 | 6,000 | 8,000 | 10,000 | 12,000 |
| 데이터 | 1Gbps | 2Gbps | 3.6Gbps | 6.4Gbps | 9.2Gbps |

```
TSV 미세화 효과:
- TSV 개수 증가 → 더 넓은 병렬 I/O
- 더 높은 데이터 레이트 가능
- 하지만 기생 커패시턴스/저항 관리 필요
```

---

## 6. 패키징 기술 발전

### 6.1 패키징 방식 비교

| 방식 | 적용 세대 | 특징 |
|------|----------|------|
| TSV + Microbump | HBM1/HBM2 | 기본 3D 적층 |
| Advanced Bump | HBM2E | 미세 피치 범프 |
| NCF (Non-Conductive Film) | HBM3 | 필름형 접착, 휨 감소 |
| **MR-MUF** | HBM3E | 액상 에폭시 일괄 몰딩 |

### 6.2 MR-MUF 장점

```
MR-MUF (Mass Reflow Molded Underfill):
- 고단 층간 빈 공간에 액상 에폭시 일괄 주입
- 한 번에 경화 → 공정 단순화
- 열전도성 향상 (방열 2.5배)
- 칩 휨(Warpage) 억제
- 12-Hi 이상 고단 적층 필수 기술
```

---

## 7. Virtuoso 설계 자동화

### 7.1 SKILL 스크립트 실행

```skill
; Virtuoso CIW에서 실행

; 1. 간단 풀 스택 생성 (권장)
hbmGenerateFull("hbm_lib" "HBM3E")
; → HBM3E_stack, HBM3E_base_die, HBM3E_tsv 자동 생성

; 2. 개별 스택 생성
hbmCreateStack("hbm_lib" "hbm3_stack" "HBM3" 16 16 64)

; 3. Base Die 생성
hbmCreateBaseDie("hbm_lib" "hbm3_base" "HBM3" 16 1024)

; 4. TSV 어레이 생성
hbmCreateTSV("hbm_lib" "hbm3_tsv" 5 28 10000)
```

### 7.2 Python 제너레이터 실행

```bash
cd 04.HBM/scripts
python hbm_stack_generator.py
```

생성 파일:
```
generated/
├── hbm_hbm1_stack.skill
├── hbm_hbm1_base_die.skill
├── hbm_hbm1_tsv.skill
├── hbm_hbm2_stack.skill
├── ... (HBM2, HBM2E, HBM3, HBM3E)
└── hbm_configs.json
```

---

## 8. 성능 분석 모델

### 8.1 대역폭 계산

```
대역폭 = 데이터레이트 × 버스폭 / 8

HBM1:  1.0 Gbps × 1024-bit / 8 = 128 GB/s
HBM2:  2.0 Gbps × 1024-bit / 8 = 256 GB/s
HBM3:  6.4 Gbps × 1024-bit / 8 = 819 GB/s
HBM3E: 9.2 Gbps × 1024-bit / 8 = 1,178 GB/s
```

### 8.2 용량 계산

```
용량 = 다이당 용량 × 다이 수

HBM1:  4Gb × 4 = 16Gb = 1GB (8×1024)
HBM3:  8Gb × 16 = 128Gb = 16GB
HBM3E: 16Gb × 12 = 192Gb = 24GB
```

### 8.3 채널 효율

```
채널 효율 = (채널 수 × 실제 사용 대역폭) / 전체 대역폭

16채널 (HBM3):
- 다중 AI 워크로드 병렬 처리
- 채널 간 독립 → 하나의 채널 로딩이 다른 채널에 영향 없음
```

---

## 9. 참고 자료

- JEDEC HBM Standard (HBM3, HBM3E)
- SK Hynix / Samsung / Micron 기술 백서
- Advanced Packaging: TSV, MR-MUF 기술 논문
- Cadence Virtuoso Advanced Package Design Guide
