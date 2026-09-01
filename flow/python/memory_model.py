# =============================================================================
# 메모리 설계 자동화 - 공용 파라미터/성능 모델 (Python)
# Memory Design Automation - Common Parameter & Performance Model
#
# 이 모듈은 SKILL/Tcl로 생성된 레이아웃의 전기적 파라미터를 정의하고,
# 성능(속도/전력/면적)을 예측하는 공용 모델을 제공한다.
# =============================================================================

from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

try:
    from cadence45 import CADENCE_45NM, CAD45_PERIPH_MAP
    _HAS_CAD45 = True
except ImportError:
    _HAS_CAD45 = False


@dataclass
class MemoryTech:
    """메모리 공통 기술 노드"""
    node_nm: float
    vdd: float
    vth: float
    min_pitch_nm: float
    gate_length_nm: float


@dataclass
class PerfMetrics:
    """성능 지표"""
    access_time_s: float      # 데이터 접근 시간
    data_rate_Gbps: float     # 핀당 데이터 레이트
    bandwidth_GB_s: float     # 대역폭
    density_Mbit_mm2: float   # 밀도
    power_mW: float           # 소비 전력
    area_um2: float           # 셀 면적
    leakage_nW: float         # 누설

    def to_dict(self) -> dict:
        return asdict(self)


class MemoryPerformanceModel:
    """세대별 메모리 성능 예측 모델"""

    # 기술 노드 스케일링 법칙
    # (45nm 는 Cadence GPDK045 / gsclib045 학습 라이브러리 대응 노드)
    TECH = {
        "sram": {
            5000: MemoryTech(5000, 5.0, 0.8, 5000, 5000),
            1000: MemoryTech(1000, 5.0, 0.7, 1000, 1000),
            350:  MemoryTech(350, 3.3, 0.5, 400, 350),
            65:   MemoryTech(65, 1.1, 0.35, 180, 65),
            45:   MemoryTech(45, 1.1, 0.32, 130, 45),
            14:   MemoryTech(14, 0.75, 0.25, 48, 14),
        },
        "dram": {
            8000: MemoryTech(8000, 5.0, 0.8, 8000, 8000),
            600:  MemoryTech(600, 3.3, 0.5, 600, 600),
            350:  MemoryTech(350, 3.3, 0.5, 400, 350),
            65:   MemoryTech(65, 1.5, 0.35, 80, 65),
            45:   MemoryTech(45, 1.2, 0.32, 70, 45),
            14:   MemoryTech(14, 1.1, 0.25, 24, 14),
        },
        "sdram": {
            8000: MemoryTech(8000, 5.0, 0.8, 8000, 8000),
            600:  MemoryTech(600, 3.3, 0.5, 600, 600),
            350:  MemoryTech(350, 3.3, 0.5, 400, 350),
            65:   MemoryTech(65, 1.5, 0.35, 80, 65),
            45:   MemoryTech(45, 1.2, 0.32, 70, 45),
            14:   MemoryTech(14, 1.1, 0.25, 24, 14),
        },
        "gddr": {
            65:   MemoryTech(65, 1.5, 0.4, 90, 70),
            45:   MemoryTech(45, 1.35, 0.35, 66, 45),
            12:   MemoryTech(12, 1.25, 0.25, 24, 12),
        },
        "hbm": {
            45:   MemoryTech(45, 1.1, 0.32, 40, 45),
            28:   MemoryTech(28, 1.0, 0.3, 40, 28),
            10:   MemoryTech(10, 0.9, 0.25, 28, 10),
        },
    }

    # 공정 스케일링 법칙 (Dennard 近似)
    SCALING = {
        "speed":   1.0,   # 속도는 1/sqrt(s) 비례 (전압 스케일링 보상)
        "area":    0.5,   # 면적은 (node/ref)^2
        "power":   0.7,   # 전력은 V^2 × f 비례
        "leakage": 1.0,   # 누설은 지수적 증가 (근사)
    }

    @staticmethod
    def _reference():
        """기준 기술 노드 (65nm)"""
        return MemoryTech(65, 1.1, 0.35, 180, 65)

    @staticmethod
    def _nearest(lst: List[float], target: float) -> float:
        """주어진 목록에서 target과 가장 가까운 값을 반환"""
        if not lst:
            return target
        return min(lst, key=lambda x: abs(x - target))

    def compute(self, mem_type: str, node_nm: float) -> PerfMetrics:
        """주어진 메모리 타입과 노드에 대한 성능 예측"""
        ref = self._reference()
        # 가장 가까운 지원 노드 선택 (테이블에 없는 노드 대체)
        avail = sorted(self.TECH[mem_type].keys())
        actual = self._nearest(avail, node_nm)
        tech = self.TECH[mem_type][actual]

        # 스케일링 팩터 계산
        s = ref.node_nm / tech.node_nm  # 미세화 비율

        # 면적 스케일링
        area_um2 = self._base_area(mem_type) * (tech.node_nm / ref.node_nm) ** 2

        # 속도 스케일링 (전압 고려)
        speed_s = 1.0 / (s * (tech.vdd / ref.vdd))
        access_s = self._base_access(mem_type) * speed_s

        # 대역폭 (메모리 타입별 I/O 가정)
        data_rate = self._base_datarate(mem_type) * s
        bandwidth = data_rate * self._bus_width(mem_type) / 8

        # 전력 (V²×f)
        power = self._base_power(mem_type) * (tech.vdd/ref.vdd) ** 2 * (1/speed_s)

        # 누설 (지수 근사)
        leakage = self._base_leakage(mem_type) * (1.5 ** (s / 2))

        return PerfMetrics(
            access_time_s=access_s,
            data_rate_Gbps=round(data_rate, 2),
            bandwidth_GB_s=round(bandwidth, 1),
            density_Mbit_mm2=round(self._base_density(mem_type) * s ** 2, 1),
            power_mW=round(power, 2),
            area_um2=round(area_um2, 4),
            leakage_nW=round(leakage, 2),
        )

    # ---------- 기준값 (65nm 기준) ----------
    # t: sram, dram, sdram, gddr, hbm
    def _base_area(self, t):
        return {"sram": 0.05, "dram": 0.12, "sdram": 0.12,
                "gddr": 0.15, "hbm": 0.2}.get(t, 0.12)

    # ---------- Cadence 45nm 학습 라이브러리 카탈로그 ----------
    @staticmethod
    def cadence_45nm_catalog() -> dict:
        """GPDK045/giolib045 + gsclib045 학습 라이브러리 메타데이터"""
        catalog = {"node_nm": 45.0, "tech": "gpdk045"}
        if _HAS_CAD45:
            catalog.update(CADENCE_45NM)
            catalog["periph_map"] = CAD45_PERIPH_MAP
        else:
            catalog["status"] = "cadence45.py meta unavailable"
        return catalog

    def _base_access(self, t):
        return {"sram": 500e-12, "dram": 10e-9, "sdram": 10e-9,
                "gddr": 8e-9, "hbm": 8e-9}.get(t, 10e-9)

    def _base_datarate(self, t):
        return {"sram": 8.0, "dram": 1.6, "sdram": 1.6,
                "gddr": 8.0, "hbm": 3.2}.get(t, 1.6)

    def _bus_width(self, t):
        return {"sram": 32, "dram": 8, "sdram": 8,
                "gddr": 32, "hbm": 1024}.get(t, 8)

    def _base_power(self, t):
        return {"sram": 0.5, "dram": 0.2, "sdram": 0.2,
                "gddr": 1.0, "hbm": 2.0}.get(t, 0.2)

    def _base_leakage(self, t):
        return {"sram": 1.0, "dram": 0.5, "sdram": 0.5,
                "gddr": 0.6, "hbm": 0.4}.get(t, 0.5)

    def _base_density(self, t):
        return {"sram": 3.2, "dram": 1.5, "sdram": 1.5,
                "gddr": 2.5, "hbm": 2.0}.get(t, 1.5)


def main():
    """성능 모델 데모 출력"""
    model = MemoryPerformanceModel()
    print("=" * 70)
    print("Memory Performance Model - Scaling Demo")
    print("=" * 70)

    # Cadence 45nm 학습 PDK 카탈로그 확인
    cat = model.cadence_45nm_catalog()
    print(f"\n[Cadence 45nm Learning PDK] "
          f"{cat.get('pdk_dir')}/giolib045 + "
          f"{cat.get('stdcell_dir')}/gsclib045")
    print(f"  OA libs: {cat.get('oa_libs')}")
    print(f"  Devices: {cat.get('devices')}")

    for mem_type in ["sram", "dram"]:
        print(f"\n### {mem_type.upper()} ###")
        for node in sorted(model.TECH[mem_type].keys()):
            m = model.compute(mem_type, node)
            print(f"  {node:>5}nm : access={m.access_time_s*1e9:8.2f}ns  "
                  f"rate={m.data_rate_Gbps:6.2f}Gbps  "
                  f"BW={m.bandwidth_GB_s:7.1f}GB/s  "
                  f"area={m.area_um2:8.4f}um2  "
                  f"leak={m.leakage_nW:8.1f}nW")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
