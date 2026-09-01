# =============================================================================
# Cadence 45nm 학습 PDK (GPDK045 + gsclib045) 공용 메타데이터 (Python)
# Common metadata for Cadence 45nm learning libraries
#
# 모든 메모리 타입 제너레이터(01.SRAM~04.HBM)가 산출물에 이 카탈로그를
# 포함하도록 하는 공용 모듈. (flow/python 아래 위치)
# =============================================================================

import json
from pathlib import Path

CADENCE_45NM = {
    "vendor": "Cadence",
    "node_nm": 45.0,
    "pdk_dir": "GPDK045",                       # 프로젝트 루트 기준
    "stdcell_dir": "gsclib045_all_v4.8",        # 프로젝트 루트 기준
    "tech_name": "gpdk045",
    "oa_libs": ["giolib045", "gsclib045"],
    "devices": ["g45p1svt", "g45n1svt", "g45p2svt", "g45n2svt"],
    "pads": [
        "BONDPAD52", "PADANALOG", "PADDB", "PADDI", "PADDO", "PADDOZ",
        "PADVDD", "PADVDD25", "PADVDDIOR", "PADVSS", "PADVSS25", "PADVSSIOR",
    ],
    "std_cells": [
        "ADDFHXL", "ADDFX1", "AND2XL", "AND3XL", "AO21XL", "AOI211X4",
        "AOI21X2", "AOI222X4", "AOI22X1", "AOI22X2", "AOI31X4", "AOI32X2",
        "AOI33X1", "AOI33X2", "BUFX20", "BUFX6", "CLKMX2X8", "CLKXOR2X4",
        "DFFHQX1", "DFFHQX2", "DFFQXL", "DFFSRXL", "DLY1X4", "DLY2X4",
        "DLY4X1", "EDFFTRX1", "FILL64", "FSWX1", "INVXL",
        "LSLH_ISONH_X1_TO_ON", "MX2X1", "MX2X2", "MX3X1", "MXI2X1",
        "NAND2X8", "NAND4X6", "NOR2BX1", "NOR2BX2", "NOR2X4", "NOR3BX2",
        "NOR3X2", "NOR4BBX1", "NOR4BX4", "NOR4X1", "NOR4X2", "OA21X4",
        "OAI22XL", "OAI2BB1X4", "OAI2BB2X4", "OAI33XL", "OR4X8",
        "RDFFNQX1", "RDFFNRX1", "RDFFNSRQX1", "SDFF4RX2", "SDFFNSRXL",
        "SDFFQX4", "SDFFRX2", "SDFFSRHQX8", "SDFFSX1", "SDFFX4",
        "SEDFFHQX4", "SEDFFX1", "SPDFF4RX1", "TBUFX6", "TLATNCAX2",
        "TLATNSRX1", "TLATSRX2", "XNOR2XL",
    ],
    "relative_paths": {
        "giolib_oa": "GPDK045/giolib045_v3.3/oa22",
        "giolib_lef": "GPDK045/giolib045_v3.3/lef/giolib045.lef",
        "giolib_cdl": "GPDK045/giolib045_v3.3/cdl/giolib045.cdl",
        "gsclib_oa": "gsclib045_all_v4.8/GSCLIB045/oa22",
        "gs_user_guide": "gsclib045_all_v4.8/doc/GSCLIB045_user_guide.pdf",
    },
}

# 메모리 블록 -> gsclib045 표준 셀 매핑 (주변회로 구현용)
CAD45_PERIPH_MAP = {
    "addr_decoder": ["NAND2X8", "NOR2X4", "INVXL", "AND2XL"],
    "wordline_driver": ["BUFX20", "TBUFX6", "BUFX6"],
    "register_ff": ["DFFQX1", "SDFFQX4", "DFFHQX1", "DFFQXL"],
    "column_mux": ["MX2X1", "MXI2X1", "MX3X1"],
    "timing_delay": ["DLY1X4", "DLY2X4", "DLY4X1"],
    "clock_net": ["CLKMX2X8", "CLKXOR2X4", "INVXL"],
    "sense_amp_logic": ["TLATSRX2", "INVXL", "NAND4X6"],
}


def write_cadence45_meta(output_dir: Path) -> Path:
    """각 제너레이터의 generated 폴더에 cadence45.json 작성"""
    out = Path(output_dir)
    out.mkdir(exist_ok=True)
    meta = {
        "cadence_45nm": CADENCE_45NM,
        "cad45_periph_map": CAD45_PERIPH_MAP,
    }
    path = out / "cadence45.json"
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    return path