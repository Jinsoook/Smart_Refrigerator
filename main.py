"""
스마트 냉장고 관리 시스템 — GUI 진입점
"""

import customtkinter as ctk
import matplotlib
from matplotlib import font_manager
from gui.app import SmartFridgeApp
from fridge import Fridge


def setup_korean_font() -> None:
    """matplotlib에 한글 폰트를 설정.

    OS별 우선순위 목록에서 시스템에 실제로 설치된 첫 번째 폰트를
    자동으로 선택해 적용, 못 찾으면 경고만 출력
    """
    candidates = [
        "Malgun Gothic",
        "AppleGothic",
        "NanumGothic",
        "Noto Sans CJK KR",
        "Noto Sans CJK JP",
        "Noto Sans KR",
        "Noto Serif CJK JP",
    ]

    # 시스템에 설치된 폰트 이름 집합
    installed = {f.name for f in font_manager.fontManager.ttflist}

    # 우선순위대로 가용 폰트 탐색
    for font in candidates:
        if font in installed:
            matplotlib.rcParams["font.family"] = font
            matplotlib.rcParams["axes.unicode_minus"] = False  # 마이너스 부호 깨짐 방지
            print(f"  ✅ 한글 폰트 설정 완료: {font}")
            return

    print("  ⚠️ 한글 폰트를 찾지 못했습니다. 차트 한글이 깨질 수 있습니다.")


def main() -> None:
    """CTk 테마를 설정하고 앱을 실행합니다."""
    setup_korean_font()  # 한글 폰트 먼저 설정
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    fridge = Fridge()
    app = SmartFridgeApp(fridge)
    app.mainloop()


if __name__ == "__main__":
    main()
