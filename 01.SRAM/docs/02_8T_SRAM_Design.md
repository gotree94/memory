# 8T SRAM 셀 설계 가이드 (Dual-Port)

## 1. 개요

8T SRAM은 6T 기본 셀에 **읽기 전용 포트(Read Port)**를 추가하여
읽기/쓰기 동시 동작이 가능한 고속 메모리 셀입니다.

---

## 2. 8T SRAM 셀 구조

### 2.1 회로도

```
                        Q_bar
                          |
    VDD       VDD         |
    |         |           |
   [M1]      [M2]        [M7]      ← Read Port NMOS (RP_WL 제어)
    |         |           |
    +----Q----+----Q_bar--+---- RBL (Read Bitline)
    |         |           |
   [M3]      [M4]       [M8]      ← Read Buffer NMOS
    |         |           |
   BL        BLB         VSS
    ↑          ↑
   (WL)      (WL)

    ← 6T 기본 셀 →    ← 읽기 포트 →
```

### 2.2 트랜지스터 구성

| 트랜지스터 | 타입 | 역할 |
|-----------|------|------|
| M1, M2 | PMOS | Pull-Up (6T 기본) |
| M3, M4 | NMOS | Pass-Gate Write (6T 기본) |
| M5, M6 | NMOS | Pull-Down (6T 기본) |
| M7 | NMOS | Read Pass-Gate (RP_WL 제어) |
| M8 | NMOS | Read Buffer (Q_bar → RBL 연결) |

### 2.3 동작 원리

#### 쓰기 동작 (Write)
- 기존 6T와 동일하게 동작
- WL을 High로 설정하여 BL/BLB에서 Q/Q_bar로 데이터 기록

#### 읽기 동작 (Read)
1. RP_WL (Read Port Wordline)을 High로 활성화
2. Q_bar 노드가 M7, M8를 통해 RBL(Read Bitline)의 전위를 결정
3. **읽기 동작이 셀 내부 노드(Q, Q_bar)에 영향을 주지 않음**
4. 쓰기 동작과 독립적으로 동시 읽기 가능

### 2.4 6T vs 8T 비교

| 특성 | 6T SRAM | 8T SRAM |
|------|---------|---------|
| 트랜지스터 수 | 6 | 8 |
| 읽기/쓰기 동시 | 불가 | 가능 |
| 읽기 데이터 무결성 | 셀 노드 간섭 발생 | 셀 노드 간섭 없음 |
| 읽기 속도 | 읽기-쓰기 분리 필요 | 즉시 읽기 가능 |
| 면적 | 기준 (1x) | 약 1.4x |
| 전력 | 기준 | 읽기 전력 추가 |
| 주요 활용 | 일반 캐시 | L1 캐시, 고속 캐시 |

---

## 3. 세대별 8T SRAM 설계

### 3.1 4세대 (65nm)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  65nm CMOS
동작 전압              1.1V
셀 높이                360nm
셀 폭                  196nm
면적                   0.0706μm²
트랜지스터 폭 (PU)     210nm (3λ)
트랜지스터 폭 (PD)     140nm (2λ)
트랜지스터 폭 (PG)     105nm (1.5λ)
트랜지스터 폭 (RP)     105nm (1.5λ)
SNM                    280mV
읽기 전류              250μA
쓰기 마진              380mV
누설 전류              1.5nA/cell
데이터 접근 시간       450ps
```

**설계 특징:**
- 읽기 포트 트랜지스터는 셀 크기와 동일한 VT 사용
- RBL(Read Bitline)은 별도의 Metal 4 레이어 사용
- 읽기/쓰기 포트가 물리적으로 분리되어 노이즈 내성 향상

### 3.2 5세대 (14nm FinFET)

```
파라미터              값              비고
──────────────────────────────────────────
공정                  14nm FinFET
동작 전압              0.75V
셀 높이                72nm
셀 폭                  40nm
면적                   2,880nm²
Fin 개수 (PU)         3 fins
Fin 개수 (PD)         2 fins
Fin 개수 (PG)         1.5 fins
Fin 개수 (RP)         1.5 fins
SNM                    200mV
읽기 전류              350μA
쓰기 마진              270mV
누설 전류              0.15nA/cell
데이터 접근 시간       80ps
```

**설계 특징:**
- FinFET 구조에서 읽기 포트 트랜지스터도 FinFET 적용
- 읽기 전용 포트의 게이트 길이를 최소화하여 고속 동작
- Low-VT 트랜지스터를 읽기 포트에 적용하여 전류 특성 향상

---

## 4. 8T SRAM 읽기 포트 설계 상세

### 4.1 읽기 포트 트랜지스터 크기 결정

```
읽기 포트 설계 고려사항:

1. M7 (Read Pass-Gate):
   - Q_bar 노드와 RBL을 연결
   - 크기가 작을수록 셀 면적 감소
   - 하지만 너무 작으면 읽기 전류 부족
   - 권장: PG 트랜지스터와 동일 크기 또는 약간 작게

2. M8 (Read Buffer):
   - RBL을 VSS로 드라이브
   - M7보다 크게 설계하여 읽기 전류 확보
   - 권장: PD 트랜지스터와 동일 크기
```

### 4.2 읽기 전력 소모 분석

```
읽기 동작 시 전력:

P_read = VDD × I_read + C_RBL × VDD² × f

I_read: 읽기 동작 시 흐르는 전류
C_RBL: Read Bitline 커패시턴스
f: 읽기 동작 빈도

8T의 장점:
- 읽기 포트가 분리되어 I_read가 일정
- 셀 내부 노드 간섭으로 인한 추가 전력 없음
```

---

## 5. Virtuoso 8T SRAM 설계

### 5.1 SKILL 스크립트 실행

```skill
; Virtuoso CIW에서 실행

; 1. 8T 셀 생성
sram8TGenerate("sram_lib" "my_8t_65nm" "65nm")

; 2. 8T 어레이 생성 (128 워드 x 32 비트)
sram8TArray("sram_lib" "my_8t_65nm" 128 32)
```

### 5.2 레이아웃 레이어 구성

```
Metal 1 (M1): VDD, VSS rail, 수평 배선
Metal 2 (M2): Wordline (WL), Q, Q_bar 노드
Metal 3 (M3): Bitline (BL, BLB) - 쓰기용
Metal 4 (M4): Read Bitline (RBL) - 읽기 전용
Poly: Wordline, 트랜지스터 게이트
```

### 5.3 시뮬레이션 검증

```
읽기 동작 시뮬레이션 파라미터:
- Precharge 시간: ~100ps
- RP_WL 활성화 시간: ~50ps
- RBL 충/방전 시간: ~200ps
- 읽기 윈도우: ~300ps

쓰기 동작 시뮬레이션 파라미터:
- WL 활성화 시간: ~100ps
- 데이터 전이 시간: ~150ps
- 쓰기 윈도우: ~250ps
```

---

## 6. 8T SRAM의 장단점

### 장점
- 읽기/쓰기 동시 동작 가능
- 읽기 동작이 셀 데이터에 영향 없음 (unread destructive)
- 고속 읽기 동작
- 읽기 안정성 향상

### 단점
- 6T 대비 약 30~40% 면적 증가
- 추가 전력 소비 (읽기 포트)
- 라우팅 복잡도 증가 (추가 Metal 레이어 필요)

---

## 7. 참고 자료

- IEEE ISSCC: "An 8T SRAM for Read-Port Optimization"
- Cadence Virtuoso Memory Design Guide
- Low Power SRAM Design (IEDM)
