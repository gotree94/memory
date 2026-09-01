# SRAM 세대별 발전 및 셀 구조 비교 정리

## 1. 개요
SRAM(Static Random Access Memory)의 세대별 발전 과정과 셀 구조(Cell Structure)의 변화를 정리한 문서입니다. SRAM 셀은 **면적(Density) 축소, 노이즈 마진(SNM) 확보, 누설 전류(Leakage Current) 최소화**를 목표로 발전해 왔습니다.

---

## 2. 세대별 SRAM 비교 종합표

| 세대 | 공정 / 시기 | 소자 재료 및 구조 | 셀 구조 (Cell Structure) | 속도 | 동작 전압 | 밀도 | 패키징 | 제어 방식 및 주요 특징 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1세대** | 5μm ~ 10μm PMOS / NMOS<br>(1970s) | 알루미늄 게이트,<br>SiO₂ 게이트 산화막 | **4T + 2R / Early 6T**<br>- 4T + 2-Resistor (Poly Load)<br>- 초기 6-Transistor | 50 ~ 100ns | 5V | 수십 Kbit | DIP | **비동기식**<br>고저항(R) 사용으로 면적을 줄였으나 대기 전력(mW) 소모가 큼 |
| **2세대** | 1μm ~ 2μm CMOS<br>(1980s) | 폴리실리콘 게이트,<br>SiO₂ | **Full CMOS 6T (Planar)**<br>- PMOS Load 6T 정착 | 15 ~ 35ns | 5V / 3.3V | 수 Mbit | SOP, QFP | **비동기식 / 동기식 혼용**<br>Full CMOS 정착으로 대기 전력 소모 대폭 감소 및 안정성(SNM) 증가 |
| **3세대** | 350nm ~ 500nm CMOS<br>(1990s) | 폴리실리콘 게이트,<br>SiO₂ | **High-Density Thin-CELL 6T**<br>- 세로형 Thin-CELL 레이아웃 | 5 ~ 15ns | 3.3V | 수 Mbit ~ 16 Mbit | TSOP, BGA | **동기식 위주**<br>프로세서 칩 온다이 캐시(On-chip Cache)용으로 주류 활용 |
| **4세대** | 45nm ~ 130nm CMOS<br>(2000s~) | High-k 메탈 게이트 도입 시작 | **Low-Leakage 6T / Multi-port (8T, 10T)**<br>- Dual-VT 및 읽기/쓰기 분리 셀 | 1 ~ 5ns | 1.0V ~ 1.2V | 수十 Mbit | WLCSP, Die 중첩 | **동기식**<br>프로세서 L1/L2/L3 캐시 메모리 사용, 대기 누설 전류 제어 기술 적용 |
| **5세대** | 7nm ~ 22nm FinFET<br>(2010s~현재) | Hi-k 메탈 게이트,<br>FinFET / GAA 구조 | **3D FinFET / GAA 6T & 3D Stacked**<br>- 입체 게이트 및 3D TSV 적층 | 0.2 ~ 2ns | 0.7V ~ 0.9V | 100 Mbit 이상 | 3D 적층, TSV | **동기식 (고속 내장 캐시)**<br>프로세서 내장 고밀도 캐시, AMD 3D V-Cache 등 3D 적층 구조 확대 |

---

## 3. SRAM 셀 구조(Cell Structure) 세부 분석

### 1) 1세대: 4T + 2R 및 Early 6T
* **4T + 2R (Resistor Load):**
  * PMOS 트랜지스터 2개 대신 고저항 폴리실리콘(Poly Resistor) 2개를 칩 상단 레이어에 배치하여 면적을 극단적으로 줄인 방식입니다.
  * **단점:** 대기 상태(Standby Mode)에서도 저항을 통해 전류가 계속 흘러 **대기 전력 소비(Leakage/Standby Current)**가 매우 컸습니다.
* **Early 6T:**
  * 6개의 평면 트랜지스터(2 PU PMOS, 2 PD NMOS, 2 PG NMOS)를 사용하여 안정성이 뛰어났으나 면적이 커 밀도가 낮았습니다.

### 2) 2세대 ~ 3세대: Full CMOS 6T & Thin-CELL
* **Full CMOS 6T 표준화:**
  * 4T+2R의 누설 전류 문제를 극복하기 위해 2개의 Pull-up(PMOS), 2개의 Pull-down(NMOS), 2개의 Pass-gate(NMOS)로 구성된 **Full CMOS 6T**가 산업 표준으로 자리잡았습니다.
  * 노이즈 마진(SNM, Static Noise Margin)이 크게 개선되어 신뢰성이 확보되었습니다.
* **Thin-CELL 레이아웃 (3세대):**
  * 온칩(On-chip) 캐시 메모리 적용을 위해 Cell 레이아웃을 세로로 길게 배치하는 **Thin-CELL 디자인**을 도입하여 금속 배선 길이를 줄이고 칩 내 적층 밀도를 대폭 향상시켰습니다.

### 3) 4세대: Multi-port (8T/10T) 및 Low-Leakage 6T
* **8T / 10T 셀 구조:**
  * 프로세서 고속화에 따라 읽기(Read)와 쓰기(Write) 동작을 독립적으로 수행해야 하는 요구가 발생했습니다.
  * 기존 6T 셀에 Read Port 트랜지스터를 추가한 **8T SRAM** 및 Dual-Port 지원 **10T SRAM** 구조가 L1/L2 캐시에 채택되었습니다.
* **Ultra Low-Leakage 기술:**
  * Sub-100nm 미세공정 진입에 따른 단채널 효과(Short Channel Effect) 및 문턱전압 산란을 극복하기 위해 **Dual-VT(Variable Threshold)** 및 Power-Gating 트랜지스터 기술이 접목되었습니다.

### 4) 5세대: 3D FinFET / GAA 6T 및 3D-Stacked SRAM
* **FinFET / GAA (Gate-All-Around) 6T:**
  * 2D 평면(Planar) 구조의 누설 전류 한계를 극복하기 위해 3차원 입체 채널인 **FinFET** 구조를 6T 셀에 적용했습니다.
  * 최근 3nm 이하 공정에서는 채널 4면을 모두 감싸는 **GAA(MBCFET)** 기반 SRAM 셀이 개발되어 저전압(Sub-0.8V) 고속 동작을 구현합니다.
* **3D-Stacked SRAM (TSV 기술):**
  * 로직 프로세서 다이(Die) 위에 SRAM 캐시 다이를 TSV(Through-Silicon Via)로 실리콘 직접 접합(Direct Bonding)하는 **3D V-Cache** 기술이 실용화되었습니다.

---

## 4. SRAM 셀 레이아웃 특징 비교 (2D vs 3D)

* **2D Planar Layout (2세대~4세대):**
  * 수평 평면 상에 N-Well, P-Substrate, Poly Gate, Active Area, Metal 1/2 배선이 배치되는 구조.
  * 공정이 미세화될수록 셀 간 간섭 및 전류 누설 한계에 직면.
* **3D FinFET/GAA Layout (5세대~현재):**
  * 실리콘 Fin(지느러미)을 수직으로 세우고 High-k Metal Gate가 입체적으로 감싸는 구조.
  * 상부층에 다층 금속 배선(M1~M6+)이 수직 Contact 및 Via로 복합 연결되어 면적 대비 극대화된 밀도와 집적도를 제공.
