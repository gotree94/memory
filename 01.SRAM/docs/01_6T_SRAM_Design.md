# 6T SRAM 셀 설계 가이드

## 1.��要

6T SRAM은 6개의 트랜지스터로 구성된 가장 기본적인 SRAM 셀 구조입니다.
Virtuoso에서의 자동화된 설계 방법과 각 세대별 특징을 정리합니다.

---

## 2. 6T SRAM 셀 구조

### 2.1 회로도

```
         VDD           VDD
         |              |
        [M1]           [M2]        ← Pull-Up PMOS (가장자리 결함)
         |              |
         +------ Q -----+----- Q_bar ------+
         |              |                   |
        [M3]           [M4]               [M5]            [M6]
         |              |                   |               |
        BL             BLB                VSS             VSS
         ↑              ↑
    Pass-Gate       Pass-Gate            ← Pass-Gate NMOS
    (WL = Wordline)
```

### 2.2 트랜지스터 역할

| 트랜지스터 | 타입 | 역할 |
|-----------|------|------|
| M1, M2 | PMOS | Pull-Up (Q/Q_bar를 VDD로 유지) |
| M3, M4 | NMOS | Pass-Gate (Wordline 활성화 시 BL/BLB와 연결) |
| M5, M6 | NMOS | Pull-Down (Q/Q_bar를 VSS로 유지) |

### 2.3 동작 원리

#### 읽기 동작 (Read)
1. Wordline(WL)을 High로 활성화
2. BL과 BLB를 사전 충전(Precharge) 상태로 유지
3. 셀 내부의 Q 또는 Q_bar 노드가 BL/BLB의 전위를 결정
4. 센스 앰플리파이어가 미세한 전위차를 감지하여 데이터 판별

#### 쓰기 동작 (Write)
1. BL과 BLB에 반대 데이터 설정 (예: BL=1, BLB=0)
2. Wordline(WL)을 High로 활성화
3. Pass-Gate 트랜지스터를 통해 셀 내부 노드의 전위를 강제로 변경
4. Pull-Up/Pull-Down 트랜지스터의 전력 비율(PU:PD 비율)에 의해 새 데이터가 저장

---

## 3. 세대별 6T SRAM 설계 파라미터

### 3.1 1세대 (5μm)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  5μm PMOS/NMOS
게이트 산화막          SiO₂ 100nm
동작 전압              5V
셀 높이                40μm (8λ)
셀 폭                  20μm (4λ)
면적                   800μm²
λ (가둠 길이)          5μm
트랜지스터 폭 (PU)     10μm (2λ)
트랜지스터 폭 (PD)     10μm (2λ)
트랜지스터 폭 (PG)     5μm (1λ)
SNM                    800mV
데이터 접근 시간       50ns
누설 전류              1μA/cell
패키징                 DIP
```

### 3.2 2세대 (1μm)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  1μm CMOS
게이트 산화막          SiO₂ 20nm
동작 전압              5V → 3.3V
셀 높이                8μm (8λ)
셀 폭                  4μm (4λ)
면적                   32μm²
λ                      1μm
트랜지스터 폭 (PU)     2μm (2λ)
트랜지스터 폭 (PD)     2μm (2λ)
트랜지스터 폭 (PG)     1.5μm (1.5λ)
SNM                    650mV
데이터 접근 시간       15ns
누설 전류              100nA/cell
패키징                 SOP, QFP
```

**주요 변경사항:**
- 4T+2R → Full CMOS 6T 전환
- 대기 전력 대폭 감소
- CMOS 논리 호환 가능

### 3.3 3세대 (350nm)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  350nm CMOS
게이트 산화막          SiO₂ 8nm
동작 전압              3.3V
셀 높이                1.4μm (3.5λ)
셀 폭                  0.8μm (2λ)
면적                   1.12μm²
λ                      200nm
트랜지스터 폭 (PU)     0.7μm (3.5λ)
트랜지스터 폭 (PD)     0.7μm (3.5λ)
트랜지스터 폭 (PG)     0.5μm (2.5λ)
SNM                    450mV
데이터 접근 시간       5ns
누설 전류              10nA/cell
패키징                 TSOP, BGA
```

**주요 변경사항:**
- Thin-CELL 레이아웃 도입 (세로형)
- 온칩 캐시 메모리 적용
- 면적 대폭 축소

### 3.4 4세대 (65nm)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  65nm CMOS
게이트 산화막          SiO₂/HfO₂ 혼합 2.5nm (EOT)
동작 전압              1.1V
셀 높이                360nm (5λ)
셀 폭                  140nm (2λ)
면적                   0.0504μm²
λ                      70nm
트랜지스터 폭 (PU)     210nm (3λ)
트랜지스터 폭 (PD)     140nm (2λ)
트랜지스터 폭 (PG)     105nm (1.5λ)
SNM                    250mV
데이터 접근 시간       500ps
누설 전류              1nA/cell
패키징                 WLCSP
```

**주요 변경사항:**
- High-k 메탈 게이트 점진적 도입
- Dual-VT 기술 적용
- Power-Gating 기술 활용

### 3.5 5세대 (14nm FinFET)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  14nm FinFET
게이트 산화막          Hi-k 1.0nm (EOT)
동작 전압              0.75V
셀 높이                72nm
셀 폭                  30nm
면적                   2,160nm²
Fin 개수 (PU)         3 fins (42nm)
Fin 개수 (PD)         2 fins (28nm)
Fin 개수 (PG)         1.5 fins (21nm)
SNM                    180mV
데이터 접근 시간       100ps
누설 전류              0.1nA/cell
패키징                 3D 적층, TSV
```

**주요 변경사항:**
- FinFET 3D 구조 채택
- 입체 게이트 구조로 누설 전류 대폭 감소
- AMD 3D V-Cache 등 3D 적층 적용

---

## 4. SNM (Static Noise Margin) 설계

### 4.1 SNM 정의

SNM은 SRAM 셀이 안정적으로 데이터를 유지할 수 있는 최대 노이즈 전압입니다.

```
SNM = min(VNL, VNR)

VNL: Low에 대한 노이즈 마진
VNR: High에 대한 노이즈 마진
```

### 4.2 SNM 향상 방법

| 방법 | 설명 | 적용 세대 |
|------|------|----------|
| PU:PD 비율 최적화 | PMOS:NMOS 폭 비율 조정 | 전 세대 |
| Dual-VT | 높은 VT 트랜지스터 사용 | 4세대~ |
| Body Biasing | 기판 전압 제어 | 5세대~ |
| FinFET | 입체 채널로 제어력 향상 | 5세대~ |

---

## 5. Virtuoso 설계 자동화

### 5.1 SKILL 스크립트 실행

```skill
; Virtuoso CIW에서 실행

; 1. 싱글 셀 생성
sram6TGenerate("sram_lib" "my_6t_65nm" "65nm")

; 2. 어레이 생성 (64 워드 x 8 비트)
sram6TPlaceAndRoute("sram_lib" "my_6t_65nm" 64 8)

; 3. Python 제너레이터 실행
; $ python sram_cell_generator.py
```

### 5.2 Python 파라미터 제너레이터

```bash
# 실행 방법
cd 01.SRAM/scripts
python sram_cell_generator.py

# 생성되는 파일:
# - generated/sram_6t_*.skill (각 세대별 SKILL 코드)
# - generated/sram_cell_configs.json (파라미터 설정)
# - generated/sram_design_kit.json (전체 설계 키트)
```

### 5.3 레이아웃 검증

```skill
; DRC 실행
techRunDRC(cv nil nil)

; LVS 실행 (스케마틱 vs 레이아웃 비교)
techRunLVS(cv schematicCV nil)

; 전기적 시뮬레이션
; spectre 또는 hspice로 셀 특성 분석
```

---

## 6. 주요 설계 고려사항

### 6.1 면적 vs 속도 트레이드오프

```
면적 최소화:          속도 최대화:
- PU:PD 비율 ↑        - PU:PD 비율 ↓
- 셀 폭 ↓             - 트랜지스터 폭 ↑
- 가둠 길이 최소      - 배선 저항 최소화
```

### 6.2 전력 소비 최적화

```
동적 전력: P_dyn = C × V² × f
정적 전력: P_stat = I_leak × V

저전력 설계 전략:
1. 전압 스케일링 (VDD ↓)
2. 누설 전류 제어 (Multi-VT, Power Gating)
3. 클럭 게이팅
```

### 6.3 신뢰성 고려사항

- BTI (Bias Temperature Instability)
- HCI (Hot Carrier Injection)
- 전기적 점멸 (Electromigration)
- NBTI (Negative BTI) - PMOS

---

## 7. 참고 자료

- SRAM Cell Design Optimization (ISSCC)
- FinFET SRAM Design (IEDM)
- 3D V-Cache Technology (AMD)
- Virtuoso Layout Suite User Guide (Cadence)
