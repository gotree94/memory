# GDDR 메모리 세대별 발전 및 셀 구조 비교 정리

## 1. 개요
GDDR(Graphics Double Data Rate) SDRAM 세대별 발전 과정과 셀 구조(Cell Structure)의 기술적 변화를 정리한 문서입니다. GDDR 메모리는 일반 DDR 메모리와 동일하게 **1개 트랜지스터 + 1개 커패시터(1T1C)** 기본 구조를 공유하지만, 고대역폭 그래픽/AI 처리를 위해 **초고속 I/O 기술, 멀티 채널화 및 PAM4 시그널링** 기술에 최적화되어 발전해 왔습니다.

---

## 2. 세대별 GDDR (GDDR5 / GDDR6 / GDDR6X) 비교 종합표

| 세대 | 공정 / 시기 | 소자 재료 및 구조 | 셀 구조 (Cell Structure) 및 핵심 기술 | 데이터 레이트 | 동작 전압 | 인터페이스 / 대역폭 | 패키징 | 주요 특징 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GDDR5** | 60nm ~ 90nm<br>(2008) | Poly Gate / Early High-k,<br>Planar CMOS | **1T1C (Advanced Cylinder Cap + RCAT)**<br>- 고속 액세스용 8n-prefetch<br>- WCK/CK 분리 클럭 회로 | 4 ~ 6 Gbps<br>(per pin) | 1.5V | 4n/8n prefetch, Pseudo-QDR<br>108 ~ 192 GB/s (256~384-bit) | BGA (170-ball) | WCK(차동 데이터 클럭) 도입, 에러 감지(EDC) 기능 제공 |
| **GDDR6** | 10nm ~ 14nm<br>(2018) | High-k 메탈 게이트,<br>FinFET/Deep BCAT | **1T1C (Deep BCAT + Ultra HAR Cap)**<br>- Dual 16-bit Subchannel 분리<br>- Low-leakage 셀 어레이 | 8 ~ 16 Gbps<br>(per pin) | 1.25V ~ 1.35V | 16n prefetch, Pseudo-QDR<br>256 ~ 672 GB/s | BGA (180-ball) | 독립된 듀얼 32-bit(16-bit x2) 채널 구조, 저전력 VDD/VDDQ 모드 지원 |
| **GDDR6X**| 8nm ~ 10nm<br>(2020) | High-k 메탈 게이트,<br>Advanced FinFET | **1T1C (EUV-BCAT + PAM4 Driver Integration)**<br>- PAM4 Multi-level I/O 트랜지스터<br>- 초고속 노이즈 억제 설계 | 19 ~ 21 Gbps+<br>(per pin) | 1.2V ~ 1.35V | PAM4 (4-Level Signal), 16n prefetch<br>1,000 GB/s 이상 (1 TB/s) | BGA (180-ball) | NRZ 대신 PAM4 시그널링 최초 도입, 동일 주파수 대비 2배 데이터 전송 |

---

## 3. GDDR 세대별 셀 구조(Cell Structure) 및 I/O 기술 세부 분석

### 1) GDDR5: 고속 액세스를 위한 8n-Prefetch 및 WCK 클럭 분리
* **1T1C Cell & RCAT (Recess Channel Array Transistor):**
  * 기본 1T1C 셀 어레이는 표준 DRAM과 유사하지만, 그래픽 처리 특성상 병렬 데이터 액세스 속도를 극대화하기 위해 **8n-Prefetch 코어** 및 고밀도 실린더 커패시터가 결합되었습니다.
* **WCK / CK 구조:**
  * 커맨드/어드레스용 클럭(CK)과 데이터 전송용 고속 차동 클럭(WCK)을 이원화하여 핀당 4~6 Gbps의 초고속 데이터 전송 속도를 달성했습니다.

### 2) GDDR6: 듀얼 채널(Dual Subchannel) 독립 구조 및 Deep BCAT
* **Deep BCAT & Ultra HAR Capacitor:**
  * 10nm급 미세 공정이 적용되면서 셀 트랜지스터의 누설 전류 극복을 위해 **BCAT(Buried Channel Array Transistor)**가 완전히 정착되었습니다.
* **Dual 16-bit Subchannel 레이아웃:**
  * 기존 단일 32-bit 채널 구조에서 **2개의 독립된 16-bit 서브채널(Subchannel)** 구조로 변경되었습니다.
  * 셀 어레이가 독립된 2개의 채널로 나뉘어 커맨드/어드레스 라인을 효율화하고, 메모리 접근 효율성 및 대역폭 유연성을 대폭 향상시켰습니다.

### 3) GDDR6X: PAM4 (Pulse Amplitude Modulation 4) 시그널링 및 초고속 I/O
* **PAM4 Multi-Level Signal I/O:**
  * 기존의 0과 1만을 전송하던 2-Level NRZ(Non-Return-to-Zero) 방식 대신, 4개의 전압 레벨(00, 01, 10, 11)을 활용해 **1주기당 2비트의 데이터를 전송하는 PAM4 기술**을 고속 그래픽 메모리에 최초로 적용했습니다.
* **I/O 드라이버 회로 및 노이즈 억제 셀 설계:**
  * PAM4 신호 도입에 따라 신호 간 전압 차이(Eye Diagram Margin)가 줄어들므로, 셀 어레이 주변부 I/O 회로의 노이즈 감쇄 기술 및 기계적 스위칭 속도를 향상시킨 초고속 트랜지스터 노드가 통합되었습니다.

---

## 4. GDDR 메모리 레이아웃 및 아키텍처 특징 비교

* **GDDR5 Architecture:**
  * 단일 32-bit 데이터 버스 구조.
  * 고주파 동작으로 인한 발열 및 비트라인/어드레스 라인 간 신호 간섭(Crosstalk) 제어가 셀 주변 회로 레이아웃의 핵심 과제.
* **GDDR6 / GDDR6X Architecture:**
  * 칩 내부를 좌/우 2개의 독립 채널(Channel A/B)로 물리적 분리.
  * GDDR6X는 PAM4 트랜시버(Transceiver) 회로 공간 배치 및 고속 패키징 기술을 도입하여 핀당 20 Gbps 이상의 초고속 데이터 대역폭(1 TB/s+)을 실현.
