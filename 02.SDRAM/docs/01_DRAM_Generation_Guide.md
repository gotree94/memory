# 1세대 DRAM / SDRAM / DDR 세대별 설계 가이드

## 1. 개요

DRAM(Dynamic Random Access Memory)은 1개의 트랜지스터와 1개의 커패시터로 구성된
1T1C 구조를 기반으로 하는 휘발성 메모리입니다.
본 문서는 세대별 DRAM 기술의 변화와 Virtuoso 설계 방법을 정리합니다.

---

## 2. DRAM 1T1C 셀 기본 구조

### 2.1 회로도

```
         Wordline (WL)
              |
         ┌────┴────┐
         │ Access   │
         │ NMOS     │
         └────┬────┘
              │
         Bitline (BL)
              │
         ┌────┴────┐
         │ Storage  │
         │Capacitor │  ← 데이터 저장 (전하)
         └────┬────┘
              │
            VSS (GND)
```

### 2.2 동작 원리

#### 읽기 동작 (Read)
1. Wordline(WL)을 High로 활성화
2. Access 트랜지스터가 커패시터의 전하를 Bitline으로 전달
3. 센스 앰플리파이어가 Bitline의 미세한 전위 변화를 감지
4. 데이터 판별 및 출력

#### 쓰기 동작 (Write)
1. Wordline(WL)을 High로 활성화
2. Bitline에 데이터 전압 설정
3. Access 트랜지스터를 통해 커패시터에 전하 충/방전

#### 리프레시 동작 (Refresh)
- 커패시터의 전하가 시간에 따라 누설됨
- 일정 주기마다 모든 셀을 리프레시해야 함
- 일반적으로 64ms 주기 (4K 리프레시)

---

## 3. 세대별 DRAM 비교

### 3.1 1세대 DRAM (1970s)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  8μm ~ 12μm
소자 구조              PMOS / NMOS
게이트 산화막          SiO₂ 50nm
동작 전압              5V
셀 구조                1T1C (Planar)
커패시터                평면 (Planar)
가둠 길이              8μm
데이터 접근 시간       ~350ns
인터페이스             비동식
대표 칩                Intel 1103 (1Kbit)
패키징                 DIP
```

**특징:**
- 최초의 상용 DRAM
- 평면 커패시터 구조
- 면적이 넓어 밀도가 낮음
- 비동기식 인터페이스

### 3.2 EDO DRAM (1990s)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  600nm ~ 1μm
소자 구조              CMOS
게이트 산화막          SiO₂ 10nm
동작 전압              3.3V ~ 5V
셀 구조                1T1C (Trench/Stacked)
커패시터                트렌치 / 초기 스택
가둠 길이              600nm
데이터 접근 시간       ~40ns (Column)
인터페이스             EDO (데이터 출력 유지)
패키징                 SIMM, DIP
```

**특징:**
- 데이터 출력 상태 유지 기술 (Extended Data Out)
- FPM 대비 10~15% 성능 향상
- 초기 입체 커패시터 도입

### 3.3 SDRAM (1990s 후반)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  250nm ~ 350nm
소자 구조              CMOS
게이트 산화막          SiO₂ 8nm
동작 전압              3.3V
셀 구조                1T1C (Stacked Cylinder)
커패시터                실린더형 스택 (Cylinder)
가둠 길이              350nm
속도                   100 ~ 166MHz
데이터 레이트           PC100/PC133
CAS 레이턴시           2~3 CLK
버스트 길이            2, 4, 8
대역폭                 최대 1.06 GB/s
패키징                 DIMM, SIMM
```

**특징:**
- 최초의 동기식 DRAM (Synchronous DRAM)
- 시스템 클럭과 동기화된 동작
- 파이프라인 동작 지원
- 브릿지 칩 연동

### 3.4 DDR (DDR1, 2000)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  180nm ~ 250nm
소자 구조              CMOS
게이트 산화막          SiO₂ 5nm
동작 전압              2.5V
셀 구조                1T1C (Advanced Stacked MIM)
커패시터                MIM (Metal-Insulator-Metal) 연구
가둠 길이              180nm
속도                   200 ~ 266MHz
데이터 레이트           DDR200 ~ DDR266
CAS 레이턴시           2~3 CLK
버스트 길이            2, 4, 8
대역폭                 1.6 ~ 2.1 GB/s
프리페치               2n-prefetch
패키징                 DIMM (184핀)
표준                   JEDEC
```

**특징:**
- DDR (Double Data Rate): 클럭의 양쪽 에지에서 데이터 전송
- 2n-prefetch로 데이터 수집 효율 향상
- 기존 SDRAM 대비 2배 대역폭

### 3.5 DDR2 (2003)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  90nm ~ 130nm
소자 구조              CMOS
게이트 산화막          Low-k 다이얼렉트릭
동작 전압              1.8V
셀 구조                1T1C (MIM Capacitor)
커패시터                MIM 정착
가둠 길이              90nm
속도                   400 ~ 667MHz
데이터 레이트           DDR2-400 ~ DDR2-667
CAS 레이턴시           4~6 CLK
버스트 길이            4, 8
대역폭                 3.2 ~ 5.3 GB/s
프리페치               4n-prefetch
패키징                 DIMM (240핀)
```

**특징:**
- 4n-prefetch로 데이터 수집 효율 대폭 향상
- On-die Termination (ODT) 도입
- Fly-by 구조로 신호 무결성 개선
- MIM 커패시터 구조 정착

### 3.6 DDR3 (2007)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  65nm ~ 90nm
소자 구조              CMOS / Hi-k
게이트 산화막          High-k 메탈 게이트 (후반)
동작 전압              1.5V (1.35V LPDDR3)
셀 구조                1T1C (BCAT / Early BCAT)
트랜지스터             BCAT (Buried Channel Array Transistor)
커패시터                HAR Stacked
가둠 길이              65nm
속도                   800 ~ 1600MHz
데이터 레이트           DDR3-800 ~ DDR3-1600
CAS 레이턴시           7~11 CLK
버스트 길이            8
대역폭                 6.4 ~ 12.8 GB/s
프리페치               8n-prefetch
패키징                 DIMM (240핀)
```

**특징:**
- BCAT (매립형 채널 트랜지스터) 도입
- 단채널 효과(Short Channel Effect) 극복
- ZQ Calibration 도입
- Reset 초기화 핀 추가

### 3.7 DDR4 (2012)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  20nm ~ 30nm
소자 구조              High-k Metal Gate
동작 전압              1.2V
셀 구조                1T1C (Deep BCAT + HAR Stacked Cap)
트랜지스터             BCAT 표준화
커패시터                High Aspect Ratio Stacked
가둠 길이              30nm
속도                   1600 ~ 3200MHz
데이터 레이트           DDR4-1600 ~ DDR4-3200
CAS 레이턴시           11~19 CLK
버스트 길이            8 (BC4: 4, OTF 8)
대역폭                 12.8 ~ 25.6 GB/s
프리페치               8n-prefetch (Bank Group)
패키징                 DIMM (288핀)
```

**특징:**
- Bank Group 도입으로 쓰기 성능 향상
- VDDQ 독립 전원으로 노이즈 감소
- CRC/Parity로 데이터 무결성 보장
- FinFET 점진적 적용

### 3.8 DDR5 (2020)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  10nm급 (1α, 1β, 1γ)
소자 구조              FinFET, EUV 리소그래피
동작 전압              1.1V
셀 구조                1T1C (EUV-BCAT / VCT & Ultra HAR)
트랜지스터             VCT (Vertical Channel Transistor) 연구
커패시터                Ultra-HAR Pillar (종횡비 40~50:1)
가둠 길이              14nm
속도                   3200 ~ 6400MHz+
데이터 레이트           DDR5-3200 ~ DDR5-6400
CAS 레이턴시           14~22 CLK
버스트 길이            8, 16
대역폭                 25.6 ~ 51.2 GB/s (단일 채널)
프리페치               16n-prefetch
패키징                 DIMM (288핀), SO-DIMM (262핀)
온다이 ECC             있음 (ODECC)
```

**특징:**
- EUV 리소그래피 본격 적용
- VCT (수직 채널 트랜지스터) 연구
- On-die ECC로 데이터 무결성 보장
- PMIC (Power Management IC) 모듈 내장
- Dual 32-bit subchannel 구조

---

## 4. 커패시터 기술 변화

### 4.1 커패시터 타입 비교

| 타입 | 시기 | 구조 | 종횡비 | 장점 | 단점 |
|------|------|------|--------|------|------|
| Planar | 1세대 | 평면 | 1:1 | 단순 | 면적 넓음 |
| Trench | EDO | 기판 내부 파기 | 5~10:1 | 면적 절감 | 공정 복잡 |
| Stacked Cylinder | SDRAM~DDR2 | 기판 위 적층 | 15~25:1 | 밀도 향상 | 높이 제한 |
| MIM | DDR2~DDR3 | Metal-Insulator-Metal | 25~40:1 | 누설 전류 감소 | 공정 비용 |
| BCAT+HAR | DDR3~DDR4 | 매립형 트랜지스터 | 40~100:1 | 단채널 극복 | 공정 어려움 |
| Ultra-HAR Pillar | DDR5 | 초고층 필러 | 100~160:1 | 극미세 대응 | EUV 필요 |

### 4.2 커패시턴스 vs 면적 트레이드오프

```
커패시턴스 공식:
C = ε₀ × εr × A / d

ε₀: 진공 유전율
εr: 유전체 상대 유전율
A: 커패시터 면적
d: 유전체 두께

미세화에 따른 변화:
- A ↓ (면적 감소) → C ↓
- 이를 보완하기 위해:
  1. εr ↑ (High-k 소재 적용)
  2. d ↓ (유전체 두께 감소)
  3. 입체 구조로 유효 면적 ↑
```

---

## 5. Virtuoso DRAM 설계

### 5.1 SKILL 스크립트 실행

```skill
; Virtuoso CIW에서 실행

; 1. Planar DRAM (1세대)
dramCreatePlanar("dram_lib" "dram_1st_8um" "8um")

; 2. Stacked Cylinder DRAM (SDRAM)
dramCreateStackedCylinder("dram_lib" "dram_sdr_350nm" "350nm")

; 3. BCAT DRAM (DDR3)
dramCreateBCAT("dram_lib" "dram_ddr3_65nm" "65nm")

; 4. Pillar DRAM (DDR5)
dramCreatePillar("dram_lib" "dram_ddr5_14nm" "14nm")

; 5. 어레이 생성 (8K 워드 x 8비트, 8뱅크)
dramCreateArray("dram_lib" "dram_ddr3_65nm" "layout" 8192 8 8)
```

### 5.2 Python 제너레이터 실행

```bash
# 실행 방법
cd 02.SDRAM/scripts
python dram_cell_generator.py

# 생성되는 파일:
# - generated/dram_planar_8000nm.skill
# - generated/dram_stacked_cylinder_350nm.skill
# - generated/dram_bcat_65nm.skill
# - generated/dram_pillar_14nm.skill
# - generated/dram_cell_configs.json
```

### 5.3 레이아웃 검증

```skill
; DRC 실행
techRunDRC(cv nil nil)

; LVS 실행
techRunLVS(cv schematicCV nil)

; RC 추출 및 시뮬레이션
techExtractRC(cv nil)
```

---

## 6. 주요 설계 고려사항

### 6.1 리프레시 주기 vs 전력

```
리프레시 주기에 따른 전력 소모:

P_refresh = C × V² × N / T_refresh

C: 커패시턴스
V: 전압
N: 전체 셀 수
T_refresh: 리프레시 주기

DDR5: 32ms 리프레시 → 전력 절감
기존: 64ms 리프레시
```

### 6.2 센스 마진 최적화

```
센스 마진 = V_read - V_threshold

증가 방법:
1. 커패시턴스 ↑ (HAR 커패시터)
2. 접근 트랜지스터 크기 최적화
3. 센스 앰플리파이어 감도 향상
```

### 6.3 타이밍 파라미터

```
주요 타이밍:
- tRCD: RAS-to-CAS Delay (월 활성화 → 읽기/쓰기 명령)
- tCAS: CAS Latency (읽기 명령 → 데이터 출력)
- tRP: Row Precharge time (월 비활성화 시간)
- tRC: Row Cycle time (tRCD + tRP)

최신 DDR5:
- tRCD = 17.5ns
- tCAS = 17.5ns
- tRP = 17.5ns
```

---

## 7. 참고 자료

- JEDEC Standards (DDR, LPDDR, HBM)
- IEEE IEDM, ISSCC 논문
- Cadence Virtuoso Memory Design Guide
- Samsung, SK Hynix, Micron 기술 백서
