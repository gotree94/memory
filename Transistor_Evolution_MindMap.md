# CMOS / SRAM / Logic 트랜지스터 발전 Mind Map

> 핵심 관점: **"어떤 문제(한계)를 해결하기 위해 어떤 형상으로 바뀌었나"** + **"회사별 동세대 구현 분류"**
>
> 참고: 삼성 공식 발표 기준으로도 `Planar → FinFET → GAA → MBCFET` 흐름을 제시

---

## 1. 개요: 트랜지스터 형상(Architecture) 발전

```
   트랜지스터 형상 발전 (문제 → 형상변경 → 회사별 구현)
      │
      ▼
   Planar FET (평면, 1면 게이트 제어)
      │
      ▼
   Scaled Planar FET (미세화)
      │
      ▼  Gate Leakage 문제 → Gate Stack 재료 혁신 (High-k + Metal)
      │
      ▼
   FinFET (3면 게이트 제어)
      │
      ▼  Short Channel Effect / 미세화 한계
      │
      ▼
   GAAFET (4면 게이트 제어)
      │
      ├── Nanowire GAA
      └── Nanosheet GAA ── 회사별 구현 분기
```

---

## 2. 단계별 상세: 문제 → 해결 → 회사별 구현

### 【1단계】 Planar FET (평면 구조)
- 게이트가 채널의 **1면만** 제어하는 평면 구조
- 전통적인 CMOS에서부터 사용된 기본 구조

### 【2단계】 Scaled Planar → High-k Metal Gate
| 항목 | 내용 |
|------|------|
| **한계(문제)** | 미세화로 게이트 절연막이 얇아지며 **Gate Leakage(누설전류)** 발생 |
| **해결(변경)** | 형상은 그대로 두고 **게이트 재료/스택을 혁신** |
| **변화** | `SiO₂ + Poly` → `High-k(예: HfO₂) + Metal Gate` |
| **회사별 도입** | 인텔 45nm에서 최초 도입 → 이후 파운드리 경쟁적으로 32/28nm 채택 |

> ⚠️ **중요**: High-k Metal Gate는 **형상 세대가 아니라 Gate Stack(재료) 혁신**입니다.
> `Planar → HKMG → FinFET`으로 그리면 마치 HKMG가 3D의 다음 형상인 것처럼 보이지만,
> 실제로는 **게이트 재료 축**이 형상 축과 **직교하며 병렬 적용**됩니다.
>
> 예) Intel: 45nm에서 High-k + Metal Gate 도입 → 이후 22nm에서 Tri-Gate(FinFET)로 전환

### 【3단계】 FinFET (3면 게이트)
| 항목 | 내용 |
|------|------|
| **한계(문제)** | Planar 구조의 **Short Channel Effect(SCE, 채널 제어력 상실)** |
| **해결(변경)** | 채널을 **Fin(입체 지느러미)** 구조로 바꿔 게이트가 **3면을 감쌈** |
| **채널 제어면** | 1면 → **3면** (3-side gating) |
| **회사별 명칭** | 일반 FinFET / 인텔 **Tri-Gate**(22nm, 2011) / 삼성·TSMC FinFET(14/16nm) |

### 【4단계】 GAAFET (4면 게이트) — 세대 분기점
| 항목 | 내용 |
|------|------|
| **한계(문제)** | FinFET도 미세화 한계 → 채널 제어력/구동전류 부족 |
| **해결(변경)** | 게이트가 채널을 **4면 전체로 감쌈** (Gate-All-Around) |
| **채널 제어면** | 3면 → **4면** |
| **GAA 두 갈래** | ① Nanowire(좁은 와이어, 구동전류 약함) ② **Nanosheet(넓은 시트, 전류↑)** |

### 【5단계】 Nanosheet 구현 — 회사별 경쟁
```
                 GAAFET (4면 Gate)
                    │
         ┌──────────┴──────────┐
         │                     │
    Nanowire GAA         Nanosheet GAA
   (좁은↔구동전류 약함)    (넓은 시트, 전류↑)
         │                     │
         │     ┌───────────────┴───────────────┐
         │     ▼                               ▼
         │  ┌─────────────────────┐      ┌────────────────────┐
         └─▶│  **MBCFET™**        │      │  **RibbonFET**      │
            │  (삼성, 나노시트     │      │  (인텔, 나노시트     │
            │   다층 적층으로       │      │   리본)             │
            │   구동전류 해결)     │      │                     │
            └─────────────────────┘      └────────────────────┘
```

---

## 3. 회사별 동세대 구현 분류 (Mind Map 핵심)

| 기본 구조 | Samsung | Intel | TSMC |
|-----------|---------|-------|------|
| **Planar** | Planar | Planar (45nm HKMG) | Planar |
| **3D Fin** | FinFET | **Tri-Gate** (22nm) | FinFET (16nm) |
| **GAA Nanowire** | — (초기) | — | GAAFET |
| **GAA Nanosheet** | **MBCFET™** | **RibbonFET** | **Nanosheet FET** |

---

## 4. 핵심 정리: 두 개의 '축'

```
   ┌──────────────────────────────────────────────┐
   │         Gate Stack 축 (재료, 병렬로 적용)       │
   │   SiO₂ + Poly ────► High-k + Metal          │
   └──────────────────────────────────────────────┘
                        │
                        ▼
   ┌──────────────────────────────────────────────┐
   │         구조(형상) 축 (한계→형상변경)           │
   │   Planar → FinFET → GAA                       │
   │              │        │                       │
   │              │        ├─ Nanowire             │
   │              │        └─ Nanosheet ─┬─ MBCFET(삼성)│
   │              │                      └─ RibbonFET(인텔)│
   └──────────────────────────────────────────────┘
```

- **Planar → FinFET → GAA** = 게이트가 채널을 감싸는 **면 수 증가**(1면→3면→4면)로 **채널 제어력 향상** 문제를 해결한 **형상의 진화**
- **High-k Metal Gate** = 그 시기 전체에 **병렬로 적용된 게이트 재료 혁신** (인텔 45nm 최초)
- **GAA 안에서 회사별** = 같은 나노시트 원리를 각사 방식으로 구현 → **삼성 MBCFET™ / 인텔 RibbonFET / TSMC Nanosheet FET**

---

## 5. MBCFET / RibbonFET / Nanosheet — 최신 FAB 업체별 명칭

**Q. FAB을 가진 업체들이 개발한 최신 제조방법인가?**

**A. 네, 맞습니다.** 세 업체 모두 **나노시트 기반 GAA**라는 같은 원리를 자기만의 상품명으로 부르는 것입니다.

| 업체 (FAB 보유) | 상품명 | 공정/양산 시점 |
|----------------|--------|----------------|
| **삼성** (Samsung Foundry) | **MBCFET™** (Multi-Bridge-Channel FET) | 3nm GAA (2022~) |
| **인텔** (Intel) | **RibbonFET** | Intel 20A / 18A (2024~, 준비) |
| **TSMC** | **Nanosheet FET** | N2 (2nm, 2025~ 예정) |

### 핵심 포인트
- **원리는 동일**: FinFET의 채널 4면을 게이트가 감싸는 **GAA(나노시트)** 구조
- **다른 것은 명칭/상표뿐** — 각사가 자체 공정 기술을 마케팅 목적으로 다르게 부름
- 세부 강조점 차이:
  - 삼성 MBCFET: **멀티 브리지 채널**(게이트와 채널이 교대로 다리처럼 적층된 구조) 강조
  - 인텔 RibbonFET: 위·아래 **리본(ribbon) 모양 시트** 강조
  - TSMC Nanosheet: **나노시트**라는 일반적 기술명 그대로 사용

### 정확한 표현 (뉘앙스)
- 나노시트 GAA **자체(원리)** 는 산업계 공통 트렌드(채널 제어 한계 해결책)
- 세 **업체가 각자 독자적으로 양산화(제조방법 구현)** 한 것
- 즉, "최신 제조방법"이라기보다 **"현재의 최첨단 양산 트랜지스터 구조를 각사가 다르게 구현한 것"** 이며, FinFET 이후의 표준 세대

---

## ※ 참고: DRAM은 별개 계통

> ⚠️ 위 내용은 **CMOS/SRAM/Logic** 트랜지스터 발전입니다.
> **DRAM 셀 트랜지스터**는 별도 계통으로, FinFET/GAA와 섞지 않아야 합니다.

```
   DRAM 셀 트랜지스터 (별개 계통)
      │
      ▼
   Planar DRAM transistor
      │
      ▼
   Scaled Planar
      │
      ▼
   RCAT (Recess Channel Array Transistor)
      │
      ▼
   BCAT (Buried Channel Array Transistor)
      │
      ▼
   Deep BCAT
      │
      ▼
   VCT (Vertical Channel Transistor)
      │
      ▼
   차세대 Vertical Gate / 신구조
```
