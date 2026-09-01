// =============================================================================
// 메모리 설계 자동화 - OpenAccess C++ 레이아웃 생성 예제
// Memory SRAM Cell Layout via OpenAccess C++ API
//
// 용도:
//   백만 개 이상 셀을 다루는 대규모 자동화, 병렬 배치, PDK 규칙 기반
//   레이아웃 생성 시 SKILL보다 높은 성능이 요구될 때 사용한다.
//
// 대상 학습 PDK (C:\Users\Administrator\Desktop\memory 아래):
//   * GPDK045/giolib045_v3.3  -> OA 라이브러리 "giolib045" (IO/PAD)
//   * gsclib045_all_v4.8      -> OA 라이브러리 "gsclib045" (표준 셀)
//   * 디바이스 모델            -> g45p1svt / g45n1svt (gpdk045)
//
// 본 파일은 OpenAccess(OA) 데이터베이스 API를 사용해 6T SRAM 셀을
// 그리는 예제다. 실제 컴파일에는 Cadence OA 헤더(oaDesign.h 등)가 필요:
//
//   cd $CDS_OA_VERSION_INSTALL
//   g++ -I$OPENACCESS_INSTALL/include sram_oa_layout.cpp \
//       -L$OPENACCESS_INSTALL/lib -loa -o oa_layout
//
// 참고: 이것은 참조/교육용 스니펫입니다. 빌드 환경에 맞게 수정 필요.
// =============================================================================

// --- OA 헤더 (Cadence OpenAccess 설치 경로에 존재) ---
#include "oaDesign.h"
#include "oaLib.h"
#include "oaCell.h"
#include "oaBox.h"
#include "oaTextDisplay.h"
#include "oaUser.h"
#include "oaDesignObject.h"
#include "oaInst.h"
#include "oaTech.h"
#include "oaPath.h"
#include "oaRect.h"
#include "oaPolygon.h"
#include <string>
#include <iostream>
using namespace oa;

// =============================================================================
// Cadence 45nm 학습 PDK 라이브러리 경로 (프로젝트 루트 기준)
//   1. giolib045 : GPDK045/giolib045_v3.3/oa22  (IO/PAD 셀)
//   2. gsclib045 : gsclib045_all_v4.8/GSCLIB045/oa22 (표준 셀)
// cds.lib 등록 대신 oaLib::find() 로 접근할 수 있도록 라이브러리 설정을
// Virtuoso LIB_PATH(cdb/sl 파일) 또는 OA 라이브러리 기술 파일로 먼저 등록한다.
// =============================================================================
static const char* CAD45_GIO_LIB   = "giolib045";
static const char* CAD45_GSC_LIB   = "gsclib045";
static const char* CAD45_TECH_NAME = "gpdk045";

// gsclib045 표준 셀 예 (주변회로용):
//   addr_decoder : NAND2X8 / NOR2X4 / AND2XL / INVXL
//   wordline buf : BUFX20 / TBUFX6 / BUFX6
//   register     : DFFQX1 / SDFFQX4 / DFFHQX1
//   column mux   : MX2X1 / MXI2X1 / MX3X1
//   timing delay : DLY1X4 / DLY2X4 / DLY4X1
// giolib045 PAD 셀 예:
//   PADDI / PADDO / PADDOZ / PADDB / BONDPAD52 / PADVDD / PADVSS

// =============================================================================
// 6T SRAM 셀 레이아웃 생성기
// =============================================================================
class SramOaLayout {
public:
    SramOaLayout(const char* libName, const char* cellName,
                 double cellW_um, double cellH_um)
        : lib_(libName), cell_(cellName),
          w_(cellW_um), h_(cellH_um), tech_(oaTechPtr()) {}

    // 레이아웃 생성
    bool create() {
        // 1. 라이브러리 열기
        oaLibPtr lib = oaLib::find(oaLibName(lib_));
        if (lib.isNull()) {
            std::cerr << "ERROR: library " << lib_ << " not found\n";
            return false;
        }

        // 2. 셀 뷰 생성 (layout)
        oaDesignPtr design;
        try {
            design = oaDesign::open(
                oaLib::find(lib_), oaCellName(cell_),
                oaViewName("layout"), oaWrite);
        } catch (const oaException& e) {
            std::cerr << "OA open failed: " << e.getMsg() << "\n";
            return false;
        }
        if (design.isNull()) return false;

        // 3. 레이아웃 객체 생성
        createWellAndActive(*design);
        createPolyGates(*design);
        createMetalNets(*design);

        // 4. 저장
        design->save();
        std::cout << "Saved: " << lib_ << "/" << cell_ << "/layout\n";
        return true;
    }

private:
    const char* lib_;
    const char* cell_;
    double w_;
    double h_;

    // --- N-Well + Active ---
    void createWellAndActive(oaDesign& d) {
        // N-Well: 상단 1/3
        oaBox wellBox(0, (int)(h_*2/3 * 1000), (int)(w_*1000), (int)(h_*1000));
        oaRect::create(d, oaNWellLayer::get(), oa::ab(), wellBox);

        // Active: PMOS 영역
        oaBox actBox((int)(w_*0.4*1000), (int)(h_*0.7*1000),
                     (int)(w_*0.6*1000), (int)(h_*0.9*1000));
        oaRect::create(d, oaActiveLayer::get(), oa::ab(), actBox);
    }

    // --- Poly Gate (Wordline + 트랜지스터 게이트) ---
    void createPolyGates(oaDesign& d) {
        // 수평 Wordline
        oaBox wlBox(0, (int)(h_*0.5*1000), (int)(w_*1000), (int)(h_*0.52*1000));
        oaRect::create(d, oaPolyLayer::get(), oa::ab(), wlBox);

        // 수직 폴리 (왼쪽 트랜지스터)
        oaBox pgLeft((int)(w_*0.3*1000), 0,
                     (int)(w_*0.32*1000), (int)(h_*0.4*1000));
        oaRect::create(d, oaPolyLayer::get(), oa::ab(), pgLeft);
    }

    // --- Metal 1 배선 ---
    void createMetalNets(oaDesign& d) {
        // VDD rail (상단)
        oaBox vddBox(0, (int)(h_*0.95*1000), (int)(w_*1000), (int)(h_*1000));
        oaRect::create(d, oaMetal1Layer::get(), oa::ab(), vddBox);

        // VSS rail (하단)
        oaBox vssBox(0, 0, (int)(w_*1000), (int)(h_*0.05*1000));
        oaRect::create(d, oaMetal1Layer::get(), oa::ab(), vssBox);

        // 지상 텍스트 라벨
        oaTextDisplay::create(d, oaTextLayer::get(), oa::ab(),
            oaText("VDD"), oaPoint((int)(w_/2*1000), (int)(h_*0.97*1000)));
    }
};

// =============================================================================
// 어레이 생성 (BV: 본 파일 단독 빌드 시 뷰 생성 예시)
// =============================================================================
int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: oa_layout <lib> <cell> [w_um] [h_um]\n";
        return 1;
    }
    const char* lib = argv[1];
    const char* cell = argv[2];
    // 기본값: Cadence GPDK045 45nm SRAM 비트셀 치수
    double w = argc > 3 ? atof(argv[3]) : 0.11;   // 45nm (GPDK045)
    double h = argc > 4 ? atof(argv[4]) : 0.27;

    // OA 데이터베이스 초기화
    oaInit();
    oaDesign::beginSession();

    SramOaLayout gen(lib, cell, w, h);
    bool ok = gen.create();

    oaDesign::endSession();
    return ok ? 0 : 1;
}