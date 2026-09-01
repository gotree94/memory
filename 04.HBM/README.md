# HBM 세대별 발전 및 3D 적층 셀 아키텍처 비교 정리

## 1. 개요
HBM(High Bandwidth Memory) 세대별 발전 과정과 적층 아키텍처(TSV, Base Die, MR-MUF 등)의 기술적 변화를 정리한 문서입니다. HBM은 개별 DRAM 코어 다이(Core Die)의 1T1C 셀 구조 위에 **TSV(수직 관통 전극), Microbump, Base Die(로직 다이)** 및 Advanced Packaging 기술을 유기적으로 결합하여 AI/HPC용 초고대역폭을 구현합니다.

---

## 2. 세대별 HBM (HBM1 ~ HBM3E) 비교 종합표

| 세대 | 공정 / 시기 | 적층 및 패키징 | 셀 구조 및 TSV 아키텍처 기술 | 핀당 속도 | 대역폭 (스택당) | 최대 용량 (스택당) | 주요 특징 및 인터페이스 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HBM (1세대)** | 28nm<br>(2013) | 2.5D 실리콘 인터포저<br>TSV + Microbump | **1T1C (BCAT) + 4-Hi TSV Core Die**<br>- 1024-bit 넓은 I/O 패키징 연동<br>- Base Die(Buffer Die) 최초 적용 | 1.0 Gbps | 128 GB/s | 1 GB (4Gb x4) | 최초의 3D 적층 메모리, 1024-bit 버스 폭 |
| **HBM2** | 20nm ~ 28nm<br>(2016) | 2.5D 인터포저<br>TSV + Microbump | **1T1C (Advanced BCAT) + 4/8-Hi TSV**<br>- Pseudo Channel (2x512-bit) 구조<br>- 신뢰성 강화 패키징 및 Thermal Shield | 2.0 Gbps | 256 GB/s | 2 ~ 8 GB | Pseudo Channel 도입으로 버스 효율 향상, ECC 지원 |
| **HBM2E** | 10nm급 (1x/1y)<br>(2020) | Advanced 2.5D<br>TSV + Advanced Bump | **1T1C (10nm BCAT) + 4/8/12-Hi TSV**<br>- 12-Hi 적층 고집적 다이 시그널링<br>- 범프 간격(Pitch) 미세화 기술 적용 | 3.2 ~ 3.6 Gbps | 460 ~ 600 GB/s | 4 ~ 24 GB | 초고속/고용량 AI 가속기용 확장, thermal dissipation 강화 |
| **HBM3** | 10nm급 (1α/EUV)<br>(2022) | 2.5D / 3D 인터포저<br>Advanced Bump / NCF | **1T1C (EUV-BCAT) + 8/12/16-Hi TSV**<br>- On-Die ECC (ODECC) 내장<br>- 16-channel 독립 아키텍처 (16x64-bit) | 6.4 Gbps+ | 819 GB/s ~ 1 TB/s | 8 ~ 64 GB | 16개 채널 아키텍처, 온다이 ECC 통한 고신뢰성 확보 |
| **HBM3E** | 10nm급 (1α/1β)<br>(2024~현재) | Advanced 2.5D<br>MR-MUF / Advanced NCF | **1T1C (EUV-BCAT/VCT) + 8/12-Hi TSV**<br>- Base Die에 로직/Custom 기능 통합<br>- 방열 특성 극대화 (Liquid Epoxy/MR-MUF) | 8.0 ~ 9.2 Gbps+ | 1.15 ~ 1.2 TB/s | 24 ~ 48 GB | MR-MUF 및 최첨단 NCF 패키징으로 방열 성능 2.5배 향상 |

---

## 3. HBM 세대별 셀 구조(Cell Structure) 및 3D 적층 아키텍처 세부 분석

### 1) HBM1 / HBM2: TSV와 Base Die(로직 다이) 기반 3D 적층의 시작
* **Core Die 1T1C & TSV (Through-Silicon Via):**
  * 각 DRAM 코어 다이는 표준 DRAM과 동일한 1T1C 셀 구조(BCAT 게이트 + HAR 스택 커패시터)를 가지지만, 다이 표면을 수천 개의 **TSV 관통 홀**로 파내어 상하 수직 연결을 형성합니다.
* **Base Die (Buffer/Logic Die) 역할:**
  * 맨 아래 위치한 Base Die가 PHY 인터페이스 및 메모리 컨트롤러와의 통신을 중계하여, 1024-bit의 극도로 넓은 데이터 통로(Parallel I/O)를 구동합니다.
* **Pseudo Channel (HBM2):**
  * 1024-bit I/O를 2개의 512-bit Pseudo Channel로 분할하여 Command/Address 효율성을 높였습니다.

### 2) HBM2E / HBM3: 12-Hi/16-Hi 고단 적층 및 채널 구조 개편
* **16-Channel Architecture (HBM3):**
  * HBM3부터는 버스 구조가 **16개 독립 채널 (채널당 64-bit, 총 1024-bit)**로 더욱 세분화되어, 다중 AI 워크로드의 병렬 액세스 효율이 극대화되었습니다.
* **On-Die ECC (ODECC) 도입:**
  * 셀 미세화 및 고단 적층에 따른 비트 에러율 증가를 극복하기 위해 DRAM 코어 다이 내부에 자체 에러 정정 복구(ODECC) 회로를 내장했습니다.

### 3) HBM3E: 방열 소재 패키징 혁신 (MR-MUF / Advanced NCF) 및 Custom Base Die
* **MR-MUF (Mass Reflow Molded Underfill) 및 Advanced NCF:**
  * 12-Hi 이상의 고단 적층 시 발생하는 방열 및 칩 휨(Warpage) 문제를 해결하기 위해, 칩 사이에 액상 에폭시 물질을 주입해 한 번에 에폭시 몰딩을 굳히는 **MR-MUF** 및 열전도성이 향상된 NCF(Non-Conductive Film) 소재가 적용되었습니다.
* **Customized Base Die (차세대 HBM4 진화의 초석):**
  * DRAM 공정이 아닌 파운드리 첨단 로직 공정(5nm/3nm 등) 기반의 Base Die를 설계하여, 메모리 내부에서 AI 연산을 직접 수행하거나 고효율 전력 관리 기능을 통합합니다.

---

## 4. HBM 3D 적층 및 인터포저 패키징 구조 특징

* **2.5D Silicon Interposer Packaging:**
  * GPU/NPU 가속기와 HBM 스택을 실리콘 인터포저 위에 수평 배치하고, 초미세 재배선층(RDL)을 통해 1024개 이상의 초고속 신호선으로 물리 연결.
* **TSV + Microbump Integration:**
  * 칩당 수천 개의 TSV 전극 구멍을 형성하고, 미세 마이크로범프(Microbump)를 통해 상하 4~12개의 DRAM 다이를 수직으로 전기 연결.
* **Thermal & Mechanical Stacking Evolution:**
  * HBM3E부터는 칩 두께가 극도로 얇아지면서 수직 방열 경로(Thermal Pass) 확보와 칩 변형을 막는 **Advanced Packaging 소재 및 공정 기술**이 HBM 경쟁력의 핵심 요소로 자리잡음.
