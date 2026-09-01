# =============================================================================
# 메모리 설계 자동화 - 파이프라인 오케스트레이터 (Python)
# Memory Design Pipeline Orchestrator
#
# 이 스크립트는 전체 자동화 파이프라인을 Python에서 조율한다:
#   1. 파라미터 설정 생성 (JSON)
#   2. Virtuoso SKILL 실행 (레이아웃 생성)
#   3. Tcl 흐름 실행 (DRC/LVS/시뮬레이션)
#   4. 성능 모델 분석
#   5. 리포트 생성
#
# 언어 조합:
#   - Python : 오케스트레이션 / 데이터 / 성능 모델
#   - SKILL  : Virtuoso 레이아웃 생성 (호출)
#   - Tcl    : Cadence 흐름 제어 (호출)
# =============================================================================

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Optional

# 공용 모델 import
sys.path.insert(0, str(Path(__file__).parent))
from memory_model import MemoryPerformanceModel

# 프로젝트 루트
ROOT = Path(__file__).resolve().parent.parent.parent

# Cadence 45nm 학습 라이브러리 상대 경로 (프로젝트 루트 기준)
GPDK045_DIR = Path("GPDK045/giolib045_v3.3")
GSCLIB045_DIR = Path("gsclib045_all_v4.8/GSCLIB045")


def detect_cadence_45nm() -> Optional[dict]:
    """GPDK045(giolib045) + gsclib045 학습 라이브러리 존재 여부 확인"""
    giolib_oa = ROOT / GPDK045_DIR / "oa22" / "giolib045"
    gsclib_oa = ROOT / GSCLIB045_DIR / "oa22" / "gsclib045"

    info = {
        "node_nm": 45.0,
        "pdk": "GPDK045",
        "io_lib": "giolib045",
        "std_cell_lib": "gsclib045",
        "io_lib_oa": str(giolib_oa) if giolib_oa.is_dir() else None,
        "std_cell_oa": str(gsclib_oa) if gsclib_oa.is_dir() else None,
        "installed": giolib_oa.is_dir() and gsclib_oa.is_dir(),
    }
    return info


class MemoryPipeline:
    """메모리 설계 자동화 파이프라인"""

    MEMORY_TYPES = {
        "sram":  {"dir": "01.SRAM",  "skill": "sram_cell_generator.py"},
        "sdram": {"dir": "02.SDRAM", "skill": "dram_cell_generator.py"},
        "gddr":  {"dir": "03.GDDR",  "skill": "gddr_cell_generator.py"},
        "hbm":   {"dir": "04.HBM",   "skill": "hbm_stack_generator.py"},
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: dict = {}

    def log(self, msg: str):
        prefix = "[PIPE]" if self.verbose else ""
        print(f"{prefix} {msg}")

    # ------------------------------------------------------------------
    # 1. 파라미터 생성 (각 폴더의 Python 제너레이터 실행)
    # ------------------------------------------------------------------
    def step_generate_parameters(self, mem_type: str) -> Path:
        """각 메모리 폴더의 SKILL 생성기를 실행"""
        cfg = self.MEMORY_TYPES[mem_type]
        script = ROOT / cfg["dir"] / "scripts" / cfg["skill"]
        generated = ROOT / cfg["dir"] / "scripts" / "generated"

        self.log(f"[1/5] Generating parameters for {mem_type}")
        if not script.exists():
            self.log(f"    WARN: {script} not found - skipping")
            return generated

        # 각 제너레이터는 main()에서 SKILL + JSON을 생성
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, cwd=str(ROOT / cfg["dir"])
        )

        if result.returncode == 0:
            self.log(f"    OK - files in {generated.name}/")
        else:
            self.log(f"    ERROR: {result.stderr[:200]}")

        return generated

    # ------------------------------------------------------------------
    # 2. Virtuoso SKILL 실행 (레이아웃 생성)
    # ------------------------------------------------------------------
    def step_run_virtuoso(self, mem_type: str) -> bool:
        """Virtuoso 배치 실행 (예: virtuoso -replay)"""
        # 실제 배치 서버에서는 skippable; 여기서는 스텁
        self.log(f"[2/5] Running Virtuoso layout for {mem_type}")
        skill_files = list((ROOT / self.MEMORY_TYPES[mem_type]["dir"]
                            / "scripts").glob("*.skill"))
        self.log(f"    Detected {len(skill_files)} SKILL generators")
        return True

    # ------------------------------------------------------------------
    # 3. Tcl 흐름 실행 (DRC/LVS/시뮬레이션)
    # ------------------------------------------------------------------
    def step_run_tcl_flow(self, mem_type: str) -> bool:
        """Tcl 통합 흐름 실행"""
        self.log(f"[3/5] Running Tcl flow for {mem_type}")
        tcl = ROOT / "flow" / "tcl" / "run_flow.tcl"
        if not tcl.exists():
            self.log("    WARN: run_flow.tcl not found")
            return False

        result = subprocess.run(
            ["tclsh", str(tcl)],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        if result.returncode == 0 and self.verbose:
            print(result.stdout)
        return result.returncode == 0

    # ------------------------------------------------------------------
    # 4. 성능 모델 분석
    # ------------------------------------------------------------------
    def step_analyze(self, mem_type: str, node_nm: float) -> dict:
        """성능 모델 기반 예측"""
        self.log(f"[4/5] Analyzing {mem_type} @ {node_nm}nm")
        model = MemoryPerformanceModel()
        metrics = model.compute(mem_type, node_nm)
        return metrics.to_dict()

    # ------------------------------------------------------------------
    # 5. 리포트 생성
    # ------------------------------------------------------------------
    def step_report(self, data: dict, output: Path):
        """통합 리포트 JSON 생성"""
        self.log(f"[5/5] Writing report to {output}")

        report = {
            "project": "Memory Design Automation",
            "language_stack": {
                "layout_generation": "SKILL",
                "flow_control": "Tcl",
                "param_and_analytics": "Python",
                "large_scale": "OA C++",
            },
            "cadence_45nm_learning_pdk": detect_cadence_45nm(),
            "results": data,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                          encoding="utf-8")

    # ------------------------------------------------------------------
    # 통합 실행
    # ------------------------------------------------------------------
    def run(self, mem_type: str, node_nm: float, output: Optional[Path] = None):
        all_results = {}

        if mem_type == "all":
            targets = list(self.MEMORY_TYPES.keys())
        else:
            targets = [mem_type]

        for mt in targets:
            self.log(f"\n----- Processing memory type: {mt} -----")
            self.step_generate_parameters(mt)
            self.step_run_virtuoso(mt)
            self.step_run_tcl_flow(mt)
            metrics = self.step_analyze(mt, node_nm)
            all_results[mt] = metrics

        out = output or (ROOT / "flow" / "reports" / "pipeline_report.json")
        self.step_report(all_results, out)
        self.log("\nPipeline completed.")

        # 콘솔 요약
        pdk = detect_cadence_45nm()
        print("\n=== Performance Summary ===")
        if pdk and pdk["installed"]:
            print(f"  Cadence 45nm PDK: giolib045 + gsclib045 (installed)")
        else:
            print(f"  Cadence 45nm PDK: not found (samples run in offline mode)")
        for mt, metrics in all_results.items():
            print(f"  {mt:>7}: access={metrics['access_time_s']*1e9:8.2f}ns  "
                  f"BW={metrics['bandwidth_GB_s']:8.1f}GB/s")
        print(f"\nReport: {out}")


def main():
    parser = argparse.ArgumentParser(description="Memory Design Pipeline")
    parser.add_argument("--type", default="all",
                        choices=["all", "sram", "sdram", "gddr", "hbm"])
    parser.add_argument("--node", type=float, default=65, help="tech node (nm)")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "flow" / "reports" / "pipeline_report.json")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    pipe = MemoryPipeline(verbose=args.verbose)
    pipe.run(args.type, args.node, args.output)


if __name__ == "__main__":
    main()
