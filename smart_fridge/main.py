"""
스마트 냉장고 관리 시스템 v2.0 — GUI 진입점

실행:
    cd smart_fridge
    python3 main.py
"""

import customtkinter as ctk
from gui.app import SmartFridgeApp
from fridge import Fridge


def main() -> None:
    """CTk 테마를 설정하고 앱을 실행합니다."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    fridge = Fridge()
    app = SmartFridgeApp(fridge)
    app.mainloop()


if __name__ == "__main__":
    main()
