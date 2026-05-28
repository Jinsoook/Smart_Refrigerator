"""
스마트 냉장고 관리 시스템 v2.0 — 메인 윈도우

사이드바 네비게이션과 콘텐츠 영역을 관리합니다.
모든 View 인스턴스는 한 번만 생성하고 grid()/grid_remove()로 전환합니다.
"""

from __future__ import annotations
import customtkinter as ctk
from fridge import Fridge


class SmartFridgeApp(ctk.CTk):
    """메인 애플리케이션 윈도우.

    Attributes:
        fridge (Fridge): 앱 전역에서 공유되는 냉장고 인스턴스
        views (dict): 뷰 이름 → CTkFrame 인스턴스
        current_view (str): 현재 표시 중인 뷰 이름
    """

    def __init__(self, fridge: Fridge) -> None:
        """앱을 초기화하고 UI를 구성합니다.

        Args:
            fridge: 앱 전역에서 공유할 Fridge 인스턴스
        """
        super().__init__()
        self.fridge = fridge
        self.current_view: str = "dashboard"

        self.title("🧊 스마트 냉장고 시스템 v2.0")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # 전체 레이아웃: 사이드바(col=0) + 콘텐츠(col=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()
        self._create_views()
        self.show_view("dashboard")

    # ── UI 구성 ───────────────────────────────────────────────

    def _build_sidebar(self) -> None:
        """좌측 사이드바(폭 200)를 구성합니다."""
        sb = ctk.CTkFrame(self, width=200, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nswe")
        sb.grid_propagate(False)  # 너비 고정
        sb.grid_rowconfigure(7, weight=1)  # 빈 공간 확장

        # 로고·타이틀
        ctk.CTkLabel(sb, text="🧊", font=ctk.CTkFont(size=42)).grid(
            row=0, column=0, padx=20, pady=(25, 0)
        )
        ctk.CTkLabel(
            sb, text="스마트 냉장고", font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=1, column=0, padx=20, pady=(4, 15))

        ctk.CTkFrame(sb, height=1, fg_color=("gray70", "gray40")).grid(
            row=2, column=0, sticky="ew", padx=15, pady=5
        )

        # 네비게이션 버튼 (뷰 이름, 표시 라벨)
        menu_items = [
            ("dashboard", "🏠  대시보드"),
            ("inventory", "📦  재고관리"),
            ("recipe",    "🍳  요리추천"),
            ("analytics", "📊  통계"),
            ("shopping",  "🛒  장보기"),
        ]
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for row_idx, (view_name, label) in enumerate(menu_items):
            btn = ctk.CTkButton(
                sb,
                text=label,
                font=ctk.CTkFont(size=13),
                anchor="w",
                height=40,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray78", "gray28"),
                command=lambda v=view_name: self.show_view(v),
            )
            btn.grid(row=row_idx + 3, column=0, padx=10, pady=3, sticky="ew")
            self._nav_buttons[view_name] = btn

    def _build_content(self) -> None:
        """우측 콘텐츠 영역 컨테이너를 구성합니다."""
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nswe")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _create_views(self) -> None:
        """모든 View 인스턴스를 한 번만 생성하고 content 영역에 배치합니다."""
        # 순환 import 방지를 위해 지연 import
        from gui.dashboard_view import DashboardView
        from gui.inventory_view import InventoryView
        from gui.recipe_view import RecipeView
        from gui.analytics_view import AnalyticsView
        from gui.shopping_view import ShoppingView

        self.views: dict[str, ctk.CTkFrame] = {
            "dashboard": DashboardView(self.content, self.fridge),
            "inventory": InventoryView(self.content, self.fridge),
            "recipe":    RecipeView(self.content, self.fridge),
            "analytics": AnalyticsView(self.content, self.fridge),
            "shopping":  ShoppingView(self.content, self.fridge),
        }
        # 모든 뷰를 같은 셀에 겹쳐 배치 (show_view에서 토글)
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nswe")

    # ── 뷰 전환 ──────────────────────────────────────────────

    def show_view(self, name: str) -> None:
        """지정한 View를 표시하고 나머지를 숨깁니다.

        Args:
            name: 표시할 뷰 이름 (dashboard/inventory/recipe/analytics/shopping)
        """
        for view in self.views.values():
            view.grid_remove()

        self.views[name].grid()
        self.views[name].refresh()
        self.current_view = name

        # 활성 버튼 강조, 나머지는 투명
        for k, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=("gray75", "gray25") if k == name else "transparent"
            )
