# 10T SRAM 셀 설계 가이드 (Full Dual-Port)

## 1. 개요

10T SRAM은 6T 기본 셀에 **2개의 독립적인 읽기/쓰기 포트**를 추가하여
완전한 듀얼 포트(Full Dual-Port) 동작이 가능한 메모리 셀입니다.

---

## 2. 10T SRAM 셀 구조

### 2.1 회로도

```
         VDD                    VDD
         |                       |
        [M1]                    [M2]        ← Pull-Up PMOS
         |                       |
         +------ Q --------------+------ Q_bar ------+
         |                       |                    |
        [M3]                    [M4]                [M5]              [M6]
         |                       |                    |                 |
        BL_A                   BLB_A               BL_B             BLB_B
         ↑                       ↑                    ↑                 ↑
      (WL_A)                  (WL_A)              (WL_B)           (WL_B)
         |                       |                    |                 |
         +--- Port A Pass-Gate --+---- Port B Pass-Gate ---+

         ← Port A (읽기/쓰기) →   ← Port B (읽기/쓰기) →
```

### 2.2 트랜지스터 구성

| 트랜지스터 | 타입 | 역할 |
|-----------|------|------|
| M1, M2 | PMOS | Pull-Up (Q, Q_bar를 VDD로 유지) |
| M3, M4 | NMOS | Port A Pass-Gate (WL_A 제어) |
| M5, M6 | NMOS | Port B Pass-Gate (WL_B 제어) |

**참고:** 10T 구조에서는 기본 6T의 Pull-Down 트랜지스터(M5, M6)가
Port B Pass-Gate로 대체됩니다. 각 포트가 독립적으로 읽기/쓰기를 수행합니다.

### 2.3 동작 원리

#### Port A 쓰기 동작
1. WL_A를 High로 활성화
2. BL_A/BLB_A에 반대 데이터 설정
3. Port A Pass-Gate를 통해 Q/Q_bar 노드에 데이터 기록

#### Port B 읽기 동작
1. WL_B를 High로 활성화
2. Q/Q_bar 노드가 BL_B/BLB_B의 전위를 결정
3. Port A와 독립적으로 동시 읽기 가능

#### 동시 읽기/쓰기
- Port A에서 쓰기 동작 중 Port B에서 읽기 동작 가능
- 두 포트가 물리적으로 분리되어 동시 동작 지원

### 2.4 6T vs 8T vs 10T 비교

| 특성 | 6T | 8T | 10T |
|------|----|----|-----|
| 트랜지스터 수 | 6 | 8 | 10 |
| 포트 수 | 1 | 1+1 (읽기 전용) | 2 (완전 듀얼) |
| 읽기/쓰기 동시 | 불가 | 읽기만 가능 | 읽기/쓰기 모두 가능 |
| 면적 | 1x | 1.4x | 1.8x |
| 전력 | 1x | 1.3x | 1.6x |
| 라우팅 복잡도 | 낮음 | 중간 | 높음 |
| 주요 활용 | 일반 캐시 | L1 캐시 | 레지스터 파일, RF |

---

## 3. 세대별 10T SRAM 설계

### 3.1 4세대 (65nm)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  65nm CMOS
동작 전압              1.1V
셀 높이                360nm
셀 폭                  252nm
면적                   0.0907μm²
λ                      70nm

트랜지스터 폭:
  PU (M1, M2)          210nm (3λ)
  Port A PG (M3, M4)   105nm (1.5λ)
  Port B PG (M5, M6)   105nm (1.5λ)

SNM                    300mV
읽기 전류              280μA
쓰기 마진              400mV
누설 전류              2.0nA/cell
데이터 접근 시간       420ps
```

**설계 특징:**
- 두 포트의 Pass-Gate가 독립적으로 동작
- WL_A와 WL_B가 수직으로 분리되어 배선
- BL_A/BLB_A와 BL_B/BLB_B가 별도의 Metal 레이어 사용

### 3.2 5세대 (14nm FinFET)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  14nm FinFET
동작 전압              0.75V
셀 높이                72nm
셀 폭                  52nm
면적                   3,744nm²

Fin 개수:
  PU (M1, M2)         3 fins
  Port A PG (M3, M4)  1.5 fins
  Port B PG (M5, M6)  1.5 fins

SNM                    220mV
읽기 전류              380μA
쓰기 마진              290mV
누설 전류              0.2nA/cell
데이터 접근 시간       70ps
```

**설계 특징:**
- FinFET 구조에서 두 포트의 Pass-Gate가 독립적
- Fin 개수 최적화를 통한 면적/전력 트레이드오프
- High-k Metal Gate 적용으로 누설 전류 최소화

---

## 4. 10T SRAM 포트 설계 상세

### 4.1 포트 분리 배선 전략

```
Metal 레이어 구성:

M1: VDD, VSS rail
M2: Q, Q_bar 노드 (내부 연결)
M3: Port A (WL_A, BL_A, BLB_A)
M4: Port B (WL_B, BL_B, BLB_B)

포트 간 간섭 최소화:
- Port A와 Port B의 Metal 레이어가 서로 다른 층에 배치
- Crosstalk 최소화를 위한 적절한 Metal 간격 유지
```

### 4.2 포트 독립성 검증

```
동시 동작 시뮬레이션 시나리오:

1. Port A 쓰기 + Port B 읽기
   - WL_A = High, WL_B = High
   - BL_A = 1, BLB_A = 0 (데이터 '1' 쓰기)
   - BL_B/BLB_B = Precharge 상태
   - Port B에서 Q/Q_bar 데이터를 독립적으로 읽기

2. Port A 읽기 + Port B 쓰기
   - 시나리오 1과 반대

3. Port A 쓰기 + Port B 쓰기
   - 두 포트에서 동시에 다른 데이터 쓰기
   - 쓰기 충돌 시 해당 셀 데이터 미정의 상태 가능
   - 메모리 컨트롤러에서 쓰기 충돌 방지 필요
```

### 4.3 레지스터 파일 구현

```
10T SRAM의 주요 활용: 레지스터 파일 (Register File)

레지스터 파일 특성:
- 읽기/쓰기 동시 동작 필요
- 낮은 레이턴시 (<100ps)
- 높은 대역폭
- 포트 수: 2포트~6포트

구현 예시:
- 마이크로프로세서 레지스터 파일
- GPU 레지스터 파일
- DSP MAC 유닛
```

---

## 5. Virtuoso 10T SRAM 설계

### 5.1 SKILL 스크립트 실행

```skill
; Virtuoso CIW에서 실행

; 1. 10T 셀 생성
sram10TGenerate("sram_lib" "my_10t_65nm" "65nm")

; 2. 10T 어레이 생성 (32 워드 x 8 비트, 레지스터 파일)
sram10TArray("sram_lib" "my_10t_65nm" 32 8)
```

### 5.2 레이아웃 설계 가이드

```
셀 영역 분할:

[상단 1/3] Port B 영역
  - WL_B: 수평 배선 (Metal 4)
  - BL_B, BLB_B: 수직 배선 (Metal 4)

[중단 1/3] 셀 코어
  - Q, Q_bar 노드 (Metal 2)
  - 트랜지스터 배치

[하단 1/3] Port A 영역
  - WL_A: 수평 배선 (Metal 3)
  - BL_A, BLB_A: 수직 배선 (Metal 3)
```

### 5.3 라우팅 고려사항

```
배선 우선순위:
1. VDD/VSS rail (M1) - 가장 우선
2. Q, Q_bar 노드 (M2) - 셀 내부 연결
3. Port A 배선 (M3) - WL_A, BL_A, BLB_A
4. Port B 배선 (M4) - WL_B, BL_B, BLB_B

간섭 방지:
- 동일 방향 배선 간 최소 간격 유지
- 수평/수직 배선 교차점 Via 사용
- Shield 배선으로 노이즈 차단
```

---

## 6. 10T SRAM의 장단점

### 장점
- 완전한 듀얼 포트 동작 (읽기/쓰기 동시)
- 포트 간 독립성 보장
- 레지스터 파일 구현 가능
- 높은 대역폭

### 단점
- 6T 대비 약 80% 면적 증가
- 높은 전력 소비
- 라우팅 복잡도 높음 (4개 Metal 레이어 필요)
- 쓰기 충돌 관리 필요

---

## 7. 응용 분야

### 7.1 마이크로프로세서 레지스터 파일

```
일반적인 구성:
- 워드 수: 32~128 (레지스터 수)
- 비트 수: 32~64 (데이터 폭)
- 포트 수: 2~6
- 접근 시간: <100ps

예시:
- ARM Cortex-A 시리즈
- Intel x86 코어
```

### 7.2 GPU 레지스터 파일

```
GPU 특성:
- 매우 높은 병렬성
- 대규모 레지스터 파일 필요
- 10T SRAM 기반 구현

예시:
- NVIDIA CUDA 코어
- AMD RDNA 유닛
```

---

## 8. 참고 자료

- IEEE ISSCC: "A 10T Full-Dual-Port SRAM"
- Register File Design (MICRO Conference)
- Cadence Virtuoso Advanced Node Design Guide
