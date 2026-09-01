# =============================================================================
# 메모리 설계 자동화 통합 흐름 제어 (Tcl)
# Memory Design Automation - Unified Flow Controller
#
# 역할:
#   Virtuoso / Genus / Innovus / Spectre / PVS 등 Cadence 툴의
#   배치-라우팅-검증-시뮬레이션 흐름을 단일 Tcl 프레임워크로 제어한다.
#
# 언어 조합:
#   - Tcl      : 툴 실행/흐름 제어 (CAD flow 표준)
#   - SKILL    : Virtuoso 레이아웃/스케마틱 객체 생성 (fonts폴더의 .skill)
#   - Python   : 파라미터 생성/파싱, 파형 분석, 리포트
#   - OA C++   : 초대규모 자동화 (선택)
#
# 사용:
#   virtuoso -replay flow/run_flow.tcl
#   또는 CIW에서  load("flow/run_flow.tcl")
# =============================================================================

# -----------------------------------------------------------------------------
# 0. 환경 구성
# -----------------------------------------------------------------------------
set library_name        "memory_lib"
set tech_library        "gsclib045"       ; # Cadence 45nm 표준 셀 라이브러리
set run_directory       [pwd]

# Cadence 45nm 학습 PDK (GPDK045 + gsclib045)
set pdk_root            "C:/Users/Administrator/Desktop/memory"
set giolib_oa_dir       "$pdk_root/GPDK045/giolib045_v3.3/oa22"
set gsclib_oa_dir       "$pdk_root/gsclib045_all_v4.8/GSCLIB045/oa22"
set giolib_lef          "$pdk_root/GPDK045/giolib045_v3.3/lef/giolib045.lef"
set giolib_cdl          "$pdk_root/GPDK045/giolib045_v3.3/cdl/giolib045.cdl"
set gsclib_lib_name     "gsclib045"       ; # 표준 셀 OA 라이브러리
set giolib_lib_name     "giolib045"       ; # IO/PAD OA 라이브러리
set gpdk_device_names   {g45p1svt g45n1svt g45p2svt g45n2svt}

# 메모리 타입별 기본 설정 (GDDR/HBM은 어레이/패키징 중심)
set memory_types {
    {sram   01.SRAM   "sram_6t_65nm"        2048  128}
    {sdram  02.SDRAM  "dram_bcat_65nm"      8192  8}
    {gddr   03.GDDR   "gddr6_array"         4096  16}
    {hbm    04.HBM    "hbm3e_stack"         16    16}
}

# -----------------------------------------------------------------------------
# 0.5 PDK 환경 초기화 (Virtuoso CDB/OA 라이브러리 붙임)
# -----------------------------------------------------------------------------
proc flow_init_pdk {} {
    global gsclib_oa_dir giolib_oa_dir gsclib_lib_name giolib_lib_name
    global giolib_lef giolib_cdl

    puts {==> [PDK] Initializing Cadence 45nm learning PDK}

    # OA 라이브러리 경로 등록
    puts "    - gsclib045 (std cells) : $gsclib_oa_dir"
    puts "    - giolib045 (IO pads)   : $giolib_oa_dir"

    # 라이브러리 매니저(cds.lib)에 추가
    #   setenv CADENCE_CDS_LIB_PATH "$gsclib_oa_dir $giolib_oa_dir"
    #   dbgLibSetPath(list($gsclib_oa_dir $giolib_oa_dir))
    puts "    (OA path registration deferred to Virtuoso CDS.lib)"

    # LEF / CDL 소스 (P&R abstract / LVS netlist 용)
    puts "    - LEF source: $giolib_lef"
    puts "    - CDL source: $giolib_cdl"
    puts "    - Devices   : g45p1svt g45n1svt g45p2svt g45n2svt (gpdk045)"
}

; # LVS/CDL 소스 매핑
proc flow_lvs_source {{cell {PADANALOG}}} {
    global giolib_cdl
    puts "    LVS netlist source: $giolib_cdl ($cell)"
}

# -----------------------------------------------------------------------------
# 1. Virtuoso 레이아웃 생성 (SKILL 호출)
# -----------------------------------------------------------------------------
proc flow_run_layout {{type "all"}} {
    global library_name
    global memory_types

    puts {==> [COMPILE] Running Virtuoso layout generation (SKILL)}

    foreach mem $memory_types {
        lassign $mem mtype dir cell rows cols
        if {$type ne "all" && $type ne $mtype} { continue }

        puts "    - Generating $mtype layout: $cell"
        # SKILL 스크립트 로드 및 실행
        set skill_script [file join $dir scripts ...]
        # 실제 환경에서는 CIW에서 dstLoad() 하거나 virtuoso 배치로 실행
        # 예: sram6TGenerate($library_name $cell "65nm")
        #     dramCreateBCAT($library_name $cell "65nm")
        #     gddrCreateArray($library_name $cell "GDDR6" 16 4 16)
        #     hbmGenerateFull($library_name "HBM3E")
        puts "      script: $dir/scripts"
    }
}

# -----------------------------------------------------------------------------
# 2. DRC / LVS 실행 (PVS / Assura)
# -----------------------------------------------------------------------------
proc flow_run_drc_lvs {{cell ""}} {
    global library_name
    puts {==> [VERIFY] Running DRC}
    # techRunDRC(cv nil nil)   또는
    # PVS runset:  pvs_run_drc -design <cell> -rules <tech>.drc.rules
    puts "    DRC not attached to physical tool in this demo."

    puts {==> [VERIFY] Running LVS}
    # techRunLVS(cv schematicCV nil) - 스키매틱 소스: cdl/giolib045.cdl
    flow_lvs_source "PADANALOG"
    puts "    LVS not attached to physical tool in this demo."
}

# -----------------------------------------------------------------------------
# 3. 전기적 시뮬레이션 (Spectre)
# -----------------------------------------------------------------------------
proc flow_run_simulation {mtype netlist} {
    puts "==> \[SIM\] Running Spectre simulation for $mtype"
    # spectre -format psf $netlist
    # 결과: $mtype.raw
    puts "    Input netlist : $netlist"
    # exec spectre $netlist > sim.log 2>&1
}

# -----------------------------------------------------------------------------
# 4. 파형 / 리포트 분석 (Python 호출)
# -----------------------------------------------------------------------------
proc flow_run_analysis {mtype result_dir} {
    puts {==> [ANALYZE] Parsing results via Python}
    # exec python flow/python/analyze_results.py $mtype $result_dir
    # -> 성능 리포트 생성 (SNM, timing, bandwidth 등)
}

# -----------------------------------------------------------------------------
# 5. 통합 실행
# -----------------------------------------------------------------------------
proc flow_run {args} {
    # 인자 파싱
    set type "all"
    set doLayout 1
    set doVerify 1
    set doSim    0

    foreach a $args {
        switch -exact -- $a {
            -type    { set type [lindex $args [expr {[lsearch $args $a] + 1}]] }
            -layout  { set doLayout 1 }
            -nolayout { set doLayout 0 }
            -verify  { set doVerify 1 }
            -noverify { set doVerify 0 }
            -sim     { set doSim 1 }
            default {}
        }
    }

    puts "==========================================================\nMemory Design Automation Flow - Summary"
    puts "  Memory type : $type"
    puts "  PDK         : Cadence 45nm (GPDK045/giolib045 + gsclib045)"
    puts "  Layout      : [expr {$doLayout ? "ON" : "OFF"}]"
    puts "  DRC/LVS     : [expr {$doVerify ? "ON" : "OFF"}]"
    puts "  Simulation  : [expr {$doSim ? "ON" : "OFF"}]"
    puts "=========================================================="

    flow_init_pdk
    if {$doLayout} { flow_run_layout $type }
    if {$doVerify} { flow_run_drc_lvs }
    if {$doSim}    { flow_run_simulation $type "flow/sim/memory.spectre" }
}

# -----------------------------------------------------------------------------
# 6. 진입점
# -----------------------------------------------------------------------------
if {[catch {flow_run -type all -layout -verify} err]} {
    puts "ERROR: $err"
}
puts "Memory Flow completed."
