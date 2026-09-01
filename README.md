# 메모리 세대별 비교 분석

## 목차
1. [개요](#개요)
2. [SRAM 세대별 비교](#sram-세대별-비교)
3. [DRAM / DDR 세대별 비교](#dram--ddr-세대별-비교)
4. [Graphics 메모리 비교](#graphics-메모리-비교)
5. [HBM (High Bandwidth Memory) 비교](#hbm-high-bandwidth-memory-비교)
6. [Low-Power DRAM 비교](#low-power-dram-비교)
7. [차세대 비휘발성 메모리 비교](#차세대-비휘발성-메모리-비교)
8. [종합 비교 테이블](#종합-비교-테이블)
9. [설계 자동화 아키텍처 (SKILL + Tcl + Python)](#설계-자동화-아키텍처-skill--tcl--python)

---

## 개요

메모리 기술은 1970년대 초반부터 현재까지 수십 년에 걸쳐 발전해 왔으며, 공정 미세화, 신소재 도입, 새로운 구조의 셀 설계, 고속 인터페이스, 첨단 패키징 기술 등을 통해 지속적으로 성능이 향상되어 왔다. 본 문서는 주요 메모리 세대별 기술적 차이를 정리한다.

---

## SRAM 세대별 비교

### 1세대 SRAM (1970s)

| 항목 | 내용 |
|------|------|
| **세대** | 1세대 SRAM |
| **제조 공정** | 5μm ~ 10μm PMOS / NMOS |
| **소자 재료** | 알루미늄 게이트, SiO₂ 게이트 산화막 |
| **셀 구조** | 6-트랜지스터 (6T) 또는 4-트랜지스터 + 2 저항 |
| **속도** | 약 50~100ns (access time) |
| **동작 전압** | 5V |
| **소비 전력** | 높음 (mW 수준) |
| **밀도** | 수십 Kbit 수준 |
| **패키징** | DIP (Dual In-line Package) |
| **제어 방식** | 비동기식 (Asynchronous) |

### 2세대 SRAM (1980s)

| 항목 | 내용 |
|------|------|
| **세대** | 2세대 SRAM |
| **제조 공정** | 1μm ~ 2μm CMOS |
| **소자 재료** | 폴리실리콘 게이트, SiO₂ |
| **속도** | 15~35ns |
| **동작 전압** | 5V (3.3V 동작 지원 시작) |
| **밀도** | 수 Mbit 수준 |
| **패키징** | SOP, QFP |
| **제어 방식** | 비동기식 / 동기식 혼용 |

### 3세대 SRAM (1990s)

| 항목 | 내용 |
|------|------|
| **세대** | 3세대 SRAM |
| **제조 공정** | 350nm ~ 500nm CMOS |
| **속도** | 5~15ns |
| **동작 전압** | 3.3V |
| **밀도** | 수 Mbit ~ 16 Mbit |
| **패키징** | TSOP, BGA |
| ** 특징** | 칩 온다이 캐시 (on-chip cache)로 주류 사용 |

### 4세대 SRAM (2000s~)

| 항목 | 내용 |
|------|------|
| **세대** | 4세대 SRAM |
| **제조 공정** | 45nm ~ 130nm CMOS |
| **속도** | 1~5ns |
| **동작 전압** | 1.0V ~ 1.2V |
| **밀도** | 수十 Mbit |
| **패키징** | WLCSP,Die 중첩 |
| ** 특징** | 프로세서 L1/L2/L3 캐시 메모리로 사용 |

### 5세대 SRAM (2010s~현재)

| 항목 | 내용 |
|------|------|
| **세대** | 5세대 SRAM |
| **제조 공정** | 7nm ~ 22nm FinFET |
| **소자 재료** | Hi-k 메탈 게이트, FinFET 구조 |
| **속도** | 0.2~2ns |
| **동작 전격** | 0.7V ~ 0.9V |
| **밀도** | 100 Mbit 이상 |
| **패키징** | 3D 적층, TSV |
| ** 특징** | 프로세서 내장 캐시, 비volaility 활용 고려 |

### SRAM 세대별 핵심 변화 요약

```
세대    공정          전압     속도      특징
1세대   5~10μm       5V      50~100ns  비동기 DIP
2세대   1~2μm        5V      15~35ns   CMOS 전환
3세대   350~500nm    3.3V    5~15ns    칩 내장 캐시
4세대   45~130nm     1.0~1.2V 1~5ns    프로세서 캐시
5세대   7~22nm       0.7~0.9V 0.2~2ns  FinFET 고밀도
```

---

## DRAM / DDR 세대별 비교

### 1세대 DRAM (1970s)

| 항목 | 내용 |
|------|------|
| **세대** | 1세대 DRAM (일반) |
| **제조 공정** | 8μm ~ 12μm |
| **소자 재료** | Al 게이트, SiO₂ 산화막 |
| **셀 구조** | 1T1C (1 트랜지스터 + 1 커패시터) |
| **속도** | ~350ns (random access) |
| **동작 전격** | 5V |
| **인터페이스** | 비동기식 |
| **대역폭** | 낮음 |
| **패키징** | DIP |
| **대표 칩** | Intel 1103 (1Kbit) |

### EDO DRAM (1990s)

| 항목 | 내용 |
|------|------|
| **세대** | EDO (Extended Data Out) DRAM |
| **제조 공정** | 600nm ~ 1μm |
| **속도** | ~40ns (column access) |
| **동작 전격** | 3.3V ~ 5V |
| **인터페이스** | EDO (데이터 출력 유지) |
| **대역폭** | FPM 대비 10~15% 향상 |
| **패키징** | SIMM, DIP |

### SDRAM (1990s 후반)

| 항목 | 내용 |
|------|------|
| **세대** | SDRAM (Synchronous DRAM) |
| **제조 공정** | 250nm ~ 350nm |
| **소자 재료** | 폴리실리콘 게이트, SiO₂ |
| **속도** | 100~166MHz (PC66~PC133) |
| **동작 전격** | 3.3V |
| **인터페이스** | 동기식 (시그널 클럭 동기화) |
| **대역폭** | 최대 1.06 GB/s (PC133) |
| **버스트 길이** | 2, 4, 8, 59 ( bursts) |
| **패키징** | DIMM, SIMM |
| ** 특징** | 브리지 칩 연동, 파이프라인 동작 |

### DDR (2000)

| 항목 | 내용 |
|------|------|
| **세대** | DDR (DDR1) |
| **제조 공정** | 180nm ~ 250nm |
| **소자 재료** | 폴리실리콘 게이트, SiO₂ |
| **속도** | 200~266MHz (DDR200~266) |
| **동작 전격** | 2.5V |
| **인터페이스** | DDR (양쪽 에지에서 데이터 전송) |
| **대역폭** | 1.6~2.1 GB/s |
| **CAS 레이턴시** | 2~3 CLK |
| **버스트 길이** | 2, 4, 8 |
| **패키징** | DIMM (184핀) |
| **표준** | JEDEC |

### DDR2 (2003)

| 항목 | 내용 |
|------|------|
| **세대** | DDR2 |
| **제조 공정** | 90nm ~ 130nm |
| **소자 재료** | low-k 다이얼렉트릭 도입 |
| **속도** | 400~667MHz (DDR2-400~667) |
| **동작 전격** | 1.8V |
| **인터페이스** | DDR + 온다이 시리얼라이저 |
| **대역폭** | 3.2~5.3 GB/s |
| **CAS 레이턴시** | 4~6 CLK |
| **버스트 길이** | 4, 8 |
| **패키징** | DIMM (240핀) |
| ** 특징** | 컨트롤러 온보드 통합, 사일런스 프리 플라이 레벨 |

### DDR3 (2007)

| 항목 | 내용 |
|------|------|
| **세대** | DDR3 |
| **제조 공정** | 65nm ~ 90nm |
| **소자 재료** | Hi-k 메탈 게이트 도입 (후반부) |
| **속도** | 800~1600MHz (DDR3-800~1600) |
| **동작 전격** | 1.5V (1.35V LPDDR3) |
| **인터페이스** | DDR + 8n- prefetch |
| **대역폭** | 6.4~12.8 GB/s |
| **CAS 레이턴시** | 7~11 CLK |
| **버스트 길이** | 8 |
| **패키징** | DIMM (240핀) |
| ** 특징** | Resets 초기화, ZQ 캘리브레이션 도입 |

### DDR4 (2012)

| 항목 | 내용 |
|------|------|
| **세대** | DDR4 |
| **제조 공정** | 20nm ~ 30nm |
| **소자 재료** | Hi-k 메탈 게이트, FinFET 점진적 도입 |
| **속도** | 1600~3200MHz (DDR4-1600~3200) |
| **동작 전격** | 1.2V |
| **인터페이스** | DDR + 8n-prefetch |
| **대역폭** | 12.8~25.6 GB/s |
| **CAS 레이턴시** | 11~19 CLK |
| **버스트 길이** | 8 (BC4 : 4, OTF 8) |
| **패키징** | DIMM (288핀), micro-DIMM |
| ** 특징** |�� defect 관리 개선, VDDQ 독립供电 |

### DDR5 (2020)

| 항목 | 내용 |
|------|------|
| **세대** | DDR5 |
| **제조 공정** | 10nm ~ 20nm (1α, 1β 공정) |
| **소자 재료** | FinFET, EUV 리소그래피 적용 |
| **속도** | 3200~6400MHz (DDR5-3200~6400) |
| **동작 전격** | 1.1V |
| **인터페이스** | DDR + 16n- prefetch |
| **대역폭** | 25.6~51.2 GB/s (단일 채널) |
| **CAS 레이턴시** | 14~22 CLK |
| **버스트 길이** | 8, 16 |
| **패키징** | DIMM (288핀), SO-DIMM (262핀) |
| **온다이 ECC** | 있음 (ODECC) |
| ** 특징** | 채널당 2 랭크, On-die ECC, 향상된 RAS |

### DRAM / DDR 세대별 핵심 변화 요약

```
세대      공정         전압     클럭        대역폭      특징
1세대     8~12μm      5V      비동기       극히 낮음   비동기 1T1C
EDO       600nm~1μm   3.3~5V  비동기       낮음        EDO 처리
SDRAM     250~350nm   3.3V    100~166MHz   1GB/s       동기식 전환
DDR       180~250nm   2.5V    200~266MHz   2GB/s       양에지 전송
DDR2      90~130nm    1.8V    400~667MHz   5GB/s       온다이 시리얼
DDR3      65~90nm     1.5V    800~1600MHz  12GB/s      8n-prefetch
DDR4      20~30nm     1.2V    1600~3200MHz 25GB/s      고속 고밀도
DDR5      10~20nm     1.1V    3200~6400MHz 51GB/s      온다이 ECC
```

---

## Graphics 메모리 비교

### GDDR5 (2008)

| 항목 | 내용 |
|------|------|
| **제조 공정** | 60nm ~ 90nm |
| **동작 전격** | 1.5V |
| **데이터 레이트** | 4~6 Gbps (per pin) |
| **대역폭** | 108~192 GB/s (256~384-bit bus) |
| **인터페이스** | GDDR5 (4n prefetch, QDR) |
| **패키징** | BGA |
| ** 특징** | WCK2C/2T 클럭 구조, QDR 데이터 전송 |

### GDDR6 (2018)

| 항목 | 내용 |
|------|------|
| **제조 공정** | 10nm ~ 14nm |
| **동작 전격** | 1.25V ~ 1.35V |
| **데이터 레이트** | 8~16 Gbps (per pin) |
| **대역폭** | 256~672 GB/s |
| **인터페이스** | GDDR6 (16n prefetch, QDR) |
| **패키징** | BGA |
| ** 특징** | 듀얼 32-bit 채널 구조 |

### GDDR6X (2020)

| 항목 | 내용 |
|------|------|
| **제조 공정** | 8nm ~ 10nm |
| **동작 전격** | 1.2V ~ 1.35V |
| **데이터 레이트** | 19~21 Gbps (per pin) |
| **대역폭** | 1,000 GB/s 이상 |
| **인터페이스** | PAM4 시그널링 |
| **패키징** | BGA |
| ** 특징** | PAM4 (Pulse Amplitude Modulation) 도입 |

### Graphics 메모리 세대별 핵심 변화

```
세대      공정        전압      데이터레이트    대역폭      특징
GDDR5     60~90nm    1.5V      4~6Gbps       192GB/s    QDR
GDDR6     10~14nm    1.3V      8~16Gbps      672GB/s    듀얼채널
GDDR6X    8~10nm     1.3V      19~21Gbps     1TB/s      PAM4
```

---

## HBM (High Bandwidth Memory) 비교

### HBM (1세대, 2013)

| 항목 | 내용 |
|------|------|
| **제조 공정** | 28nm |
| **적층 방식** | TSV (Through-Silicon Via) |
| **스택 높이** | 4 Hi (4 데드 적층) |
| **용량** | 1GB (4Gbit x 4) |
| **대역폭** | 128GB/s |
| **인터페이스** | 1024-bit |
| **패키징** | 2.5D 실리콘 인터포저 + TSV |
| ** 특징** | 최초 3D 적층 메모리 |

### HBM2 (2016)

| 항목 | 내용 |
|------|------|
| **제조 공정** | 20nm ~ 28nm |
| **적층 방식** | TSV |
| **스택 높이** | 4 Hi, 8 Hi |
| **용량** | 2~8GB |
| **대역폭** | 256GB/s |
| **인터페이스** | 1024-bit, 2Gbps per pin |
| **패키징** | 2.5D 인터포저 |
| ** 특징** | ECC 지원, 고신뢰성 |

### HBM2E (2020)

| 항목 | 내용 |
|------|------|
| **제조 공정** | 10nm ~ 20nm |
| **적층 방식** | TSV |
| **스택 높이** | 4 Hi, 8 Hi, 12 Hi |
| **용량** | 4~24GB |
| **대역 pornografia** | 460~600GB/s |
| **인터페이스** | 3.2~3.6 Gbps per pin |
| **패키징** | 2.5D 인터포저 |
| ** 특징** | 고용량, 고대역폭 |

### HBM3 (2022)

| 항목 | 내용 |
|------|------|
| **제조 공정** | 10nm 미만 (EUV 적용) |
| **적층 방식** | TSV |
| **스택 높이** | 8 Hi, 12 Hi, 16 Hi |
| **용량** | 8~64GB |
| **대역폭** | 819GB/s ~ 1TB/s |
| **인터페이스** | 6.4 Gbps per pin, 1024/2048-bit |
| **패키징** | 2.5D / 3D 인터포저 |
| ** 특징** | ECC 온다이, 고밀도 적층 |

### HBM3E (2024)

| 항목 | 내용 |
|------|------|
| **제조 공정** | 1α~1β nm |
| **적층 방식** | TSV |
| **스택 높이** | 8 Hi, 12 Hi |
| **용량** | 24~48GB (스택당) |
| **대역폭** | 1.15~1.2TB/s |
| **인터페이스** | 8~9.2 Gbps per pin |
| **패키징** | 2.5D 인터포저 |
| ** 특징** | AI/HPC 가속기 특화 |

### HBM 세대별 핵심 변화

```
세대    공정        적층     용량        대역폭       특징
HBM     28nm       4 Hi    1GB         128GB/s     최초 3D
HBM2    20~28nm    4~8 Hi  2~8GB       256GB/s     ECC
HBM2E   10~20nm    4~12 Hi 4~24GB      600GB/s     고밀도
HBM3    <10nm      8~16Hi  8~64GB      1TB/s       2048-bit
HBM3E   1α~1βnm    8~12Hi  24~48GB     1.2TB/s     AI 특화
```

---

## Low-Power DRAM 비교

### LPDDR (2003)

| 항목 | 내용 |
|------|------|
| **세대** | LPDDR (DDR 기반) |
| **동작 전격** | 1.8V |
| **대역폭** | 1.6~2.1 GB/s |
| **패키징** | POP (Package on Package), FBGA |
| ** 특징** | 모바일 최적화, 저전력 모드 |

### LPDDR2 (2009)

| 항목 | 내용 |
|------|------|
| **세대** | LPDDR2 |
| **동작 전격** | 1.2V (I/O), 1.8V (core) |
| **대역폭** | 3.2~6.4 GB/s |
| **패키징** | FBGA, POP |
| ** 특징** | 저전력 대기 모드,.variable refresh |

### LPDDR3 (2012)

| 항목 | 내용 |
|------|------|
| **세대** | LPDDR3 |
| **동작 전격** | 1.2V |
| **대역폭** | 6.4~12.8 GB/s |
| **패키징** | FBGA |
| ** 특징** | 듀얼 채널, write CRC |

### LPDDR4 (2014)

| 항목 | 내용 |
|------|------|
| **세대** | LPDDR4 |
| **동작 전격** | 1.1V (VDD2), 1.8V (VDDQ) |
| **대역폭** | 13.9~25.6 GB/s |
| **패키징** | FBGA, PoP |
| ** 특징** | 듀얼 16-bit 채널, 16n-burst |

### LPDDR4X (2017)

| 항목 | 내용 |
|------|------|
| **세대** | LPDDR4X |
| **동작 전격** | 0.6V (VDDQ) |
| **대역폭** | 25.6~34.1 GB/s |
| **패키징** | FBGA |
| ** 특징** | VDDQ 전압 대폭 절감 |

### LPDDR5 (2020)

| 항목 | 내용 |
|------|------|
| **세대** | LPDDR5 |
| **동작 전격** | 1.05V (VDD2), 0.5V (VDDQ) |
| **대역폭** | 25.6~51.2 GB/s |
| **패키징** | FBGA |
| ** 특징** | 가변 클럭, WCK2CK 모드,Bank 그룹 |

### LPDDR5X (2022)

| 항목 | 내용 |
|------|------|
| **세대** | LPDDR5X |
| **동작 전격** | 1.05V / 0.5V |
| **대역폭** | 51.2~68.3 GB/s |
| **데이터 레이트** | 8533Mbps |
| **패키징** | FBGA |
| ** 특징** | 고속 확장, AI 모바일 특화 |

### LPDDR 세대별 핵심 변화

```
세대      전압      대역폭       특징
LPDDR     1.8V     2GB/s       최초 모바일
LPDDR2    1.2V     6GB/s       저전력 모드
LPDDR3    1.2V     12GB/s      듀얼채널
LPDDR4    1.1V     25GB/s      듀얼16-bit
LPDDR4X   0.6V     34GB/s      VDDQ 절감
LPDDR5    1.0V     51GB/s      가변클럭
LPDDR5X   1.0V     68GB/s      AI 특화
```

---

## 차세대 비휘발성 메모리 비교

### MRAM (Magnetoresistive RAM)

| 항목 | 내용 |
|------|------|
| **원리** | MTJ (Magnetic Tunnel Junction)의 편향 방향에 의한 저항 변화 |
| **소자 구조** | Free layer / Barrier (MgO) / Fixed layer |
| **속도** | ~10ns (read/write) |
| **내구성** | 10¹⁵ cycles 이상 |
| **데이터 유지** | 비휘발성 (전원 제거 시 데이터 유지) |
| **동작 전격** | 0.9V ~ 1.8V |
| **공정** | 22nm ~ 40nm |
| **패키징** | 표준 CMOS 호환 패키지 |
| **적용** | 임베디드 메모리, IoT, SSD 캐시 |
| **장점** | 높은 내구성, 낮은 레이턴시, 낮은 전력 |
| **단점** | 밀도 한계, 높은 제조 비용 |

### ReRAM (Resistive RAM)

| 항목 | 내용 |
|------|------|
| **원리** | 산화물 내 필라멘트 형성/파괴에 의한 저항 변화 |
| **소자 구조** | MIM (Metal-Insulator-Metal) 구조 |
| **속도** | ~10ns (write), ~100ns (reset) |
| **내구성** | 10⁶ ~ 10¹² cycles |
| **데이터 유지** | 비휘발성 |
| **동작 전격** | 1.0V ~ 3.0V |
| **공정** | 28nm ~ 90nm |
| **패키징** | 표준 CMOS 호환 |
| **적용** | RRAM 기반 NVM, Neuromorphic |
| **장점** | 단순 구조, 고밀도 가능 |
| **단점** | 변동성(variability) 이슈 |

### PCM (Phase Change Memory)

| 항목 | 내용 |
|------|------|
| **원리** | GST (Ge₂Sb₂Te₅)의 결정상/비정상 상태 변화 |
| **소자 구조** | Heater / GST / Top electrode |
| **속도** | ~50ns (write), ~100ns (reset) |
| **내구성** | 10⁸ ~ 10¹² cycles |
| **데이터 유지** | 비휘발성 |
| **동작 전격** | 1.0V ~ 3.0V |
| **공정** | 45nm ~ 90nm |
| **패키징** | 표준 CMOS 호환 |
| **적용** | Intel Optane, Storage Class Memory |
| **장점** | 높은 밀도, 다중 레벨 셀 가능 |
| **단점** | 높은 쓰기 전력 |

### FeRAM (Ferroelectric RAM)

| 항목 | 내용 |
|------|------|
| **원리** | 강유전체 (PZT, HfO₂)의 잔류 편극에 의한 데이터 저장 |
| **소자 구조** | 강유전체 커패시터 또는 강유전체 트랜지스터 (FeFET) |
| **속도** | ~50ns (read/write) |
| **내구성** | 10¹⁰ ~ 10¹⁴ cycles |
| **데이터 유지** | 비휘발성 |
| **동작 전격** | 1.0V ~ 3.0V |
| **공정** | 28nm ~ 130nm (HfO₂ 기반은 28nm 이하) |
| **패키징** | 표준 CMOS 호환 |
| **적용** | 자동차, IoT, MCU 내장 메모리 |
| **장점** | 낮은 전력, 높은 내구성 |
| **단점** | 밀도 한계, 편극 피로 |

### 차세대 메모리 종합 비교

```
기술     원리              속도      내구성         밀도    전력    주요적용
MRAM     MTJ 편향          ~10ns     10¹⁵          중간    낮음    임베디드
ReRAM    필라멘트          ~10ns     10⁶~10¹²      높음    중간    NVM
PCM      상 변화           ~50ns     10⁸~10¹²      높음    높음    Storage
FeRAM    강유전 편극       ~50ns     10¹⁰~10¹⁴    중간    낮음    IoT/Auto
```

---

## 종합 비교 테이블

### 주요 메모리 기술 종합 비교

| 기술 | 밀도 | 속도 | 전력 | 내구성 | 비휘발성 | 비용 | 주요 활용 |
|------|------|------|------|--------|----------|------|----------|
| **SRAM** | 낮음 | 매우 빠름 | 높음 | 무한 | 휘발성 | 높음 | CPU 캐시 |
| **DRAM** | 높음 | 빠름 | 중간 | 무한 | 휘발성 | 중간 | 시스템 메모리 |
| **DDR5** | 매우 높음 | 매우 빠름 | 낮음 | 무한 | 휘발성 | 중간 | 차세대 시스템 |
| **LPDDR5X** | 높음 | 빠름 | 매우 낮음 | 무한 | 휘발성 | 중간 | 모바일/AI |
| **HBM3E** | 매우 높음 | 매우 빠름 | 중간 | 무한 | 휘발성 | 높음 | AI/HPC |
| **GDDR6X** | 높음 | 매우 빠름 | 중간 | 무한 | 휘발성 | 중간 | GPU |
| **MRAM** | 중간 | 빠름 | 매우 낮음 | 매우 높음 | 비휘발성 | 높음 | 임베디드 |
| **ReRAM** | 높음 | 빠름 | 낮음 | 중간 | 비휘발성 | 중간 | NVM |
| **PCM** | 높음 | 중간 | 높음 | 높음 | 비휘발성 | 중간 | Storage |
| **FeRAM** | 중간 | 중간 | 매우 낮음 | 높음 | 비휘발성 | 중간 | IoT/Auto |

### 공정 미세화에 따른 주요 변화

```
연도    공정          주요 기술적 변화
1970    10μm+        첫 상용 DRAM/SRAM
1985    1μm          CMOS 전환 가속
1995    350nm        SDRAM 등장
2000    180nm        DDR 도입
2003    130nm        DDR2, 저전력 기술 시작
2007    90nm         DDR3, Hi-k 도입
2012    50nm         DDR4
2015    30nm         FinFET 도입
2020    10~14nm      DDR5, HBM3, EUV 리소그래피
2024    <10nm        HBM3E, 차세대 NVM 상용화
```

---

## 참고 자료

- JEDEC Standards (DDR, LPDDR, HBM specifications)
- IEEE IEDM, ISSCC 논문
- Cadence Virtuoso memory design documentation
- Samsung, SK Hynix, Micron 기술 백서

---

## 설계 자동화 아키텍처 (SKILL + Tcl + Python)

본 프로젝트의 `01.SRAM` ~ `04.HBM` 각 폴더에는 Virtuoso 메모리 설계 자동화 스크립트가
**언어별 역할 분담**으로 구성되어 있습니다.

### 언어 조합 및 담당 영역

| 역할 | 언어 | 파일 위치 |
|------|------|-----------|
| 레이아웃/스케마틱 객체 생성 (셀, 어레이, I/O, TSV) | **SKILL** | 각 폴더 `scripts/*.skill` |
| 셀 파라미터 계산 + 설정 JSON 생성 | **Python** | 각 폴더 `scripts/*_generator.py` |
| DRC/LVS/시뮬레이션 툴 흐름 제어 | **Tcl** | `flow/tcl/run_flow.tcl` |
| 파이프라인 오케스트레이터 (전체 자동화) | **Python** | `flow/python/pipeline_orchestrator.py` |
| 성능 예측/스케일링 모델 | **Python** | `flow/python/memory_model.py` |
| 대규모 배치 자동화 (100만+ 셀, 선택) | **C++ (OA)** | `flow/oa_cpp/sram_oa_layout.cpp` |

### 전체 파이프라인 실행

```bash
# 전 메모리 타입 (SRAM/SDRAM/GDDR/HBM) 65nm 기준 파이프라인 실행
python flow/python/pipeline_orchestrator.py --type all --node 65

# 특정 타입만
python flow/python/pipeline_orchestrator.py --type sram --node 14
```

> 실행 시 각 폴더의 Python 제너레이터가 설정 JSON을 생성하고, Tcl 흐름이
> 검증 단계를 오케스트레이션하며, 성능 모델이 리포트를 만듭니다.
> 실제 레이아웃 생성은 Virtuoso CIW에서 SKILL 함수를 호출해야 합니다.

### 메모리 타입별 워크플로우 문서

- `01.SRAM/docs/04_Workflow_Languages.md`
- `02.SDRAM/docs/02_Workflow_Languages.md`
- `03.GDDR/docs/02_Workflow_Languages.md`
- `04.HBM/docs/02_Workflow_Languages.md`

### Cadence 45nm 학습 PDK 연동 (GPDK045 + gsclib045)

프로젝트 루트에 설치된 Cadence 학습 라이브러리를 기준으로 스크립트를 구성했습니다.

| 라이브러리 | 내용 | 쓰임 |
|-----------|------|------|
| `GPDK045/giolib045_v3.3` | OA `giolib045` IO/PAD 셀 (PADDI/DO/DB/BONDPAD52 등), `cdl/giolib045.cdl`, `lef/giolib045.lef` | 메모리 I/O 링, LVS/LEF 소스, gpdk045 디바이스명 |
| `gsclib045_all_v4.8/GSCLIB045` | OA `gsclib045` 표준 셀 69종 (NAND/NOR/BUF/DFF/LATCH/MUX/DLY) | 디코더, 워드라인 드라이버, 레지스터, 컬럼 mux |
| 디바이스 모델 | `g45p1svt` / `g45n1svt` (1.0V), `g45p2svt` / `g45n2svt` (2.5V) | 비트셀/셀 트랜지스터 네이밍 |

- SKILL 초기화: `flow/skill/cad45_init.skill` (라이브러리 오픈 + 셀/패드 인벤토리)
- 주변회로 매핑: `flow/skill/cad45_periph.skill` (메모리 블록 → gsclib045 std cell)
- 파이썬 카탈로그: `flow/python/cadence45.py` → 각 `generated/cadence45.json`

SKILL 예시 (Virtuoso CIW):
```skill
load("flow/skill/cad45_init.skill")
load("flow/skill/cad45_periph.skill")
cad45PeriphPlan("sram")          ; 블록→표준셀 매핑 확인
cad45CellExists("DFFQX1")        ; gsclib045 DFF 존재 확인
sram6TGenerate("sram_lib" "cell6t_45" "45nm")   ; GPDK045 기반 생성
```

파이프라인은 라이브러리 존재를 자동 검출해 리포트(`flow/reports/pipeline_report.json`)에
`cadence_45nm_learning_pdk` 블록으로 기록합니다.

### 디렉토리 구조

```
memory/
├── README.md                     (본 문서 - 세대별 비교 + 자동화 아키텍처)
├── GPDK045/                      Cadence 45nm 학습 PDK (giolib045 I/O)
├── gsclib045_all_v4.8/           Cadence 45nm 표준 셀 라이브러리 (gsclib045)
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

*본 문서는 메모리 기술의 세대별 주요 차이를 정리한 것이며, 실제 제조사별 차이 및 최신 기술 동향은 별도의 조사가 필요합니다.*
