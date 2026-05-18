"""
스마트 냉장고 관리 시스템 v2.0 — 대시보드 뷰

상단 통계 카드 4개, 임박 재료 리스트, 오늘의 추천 요리를 표시합니다.
"""

from __future__ import annotations
import customtkinter as ctk
from fridge import Fridge
from recommender import RecipeRecommender
from database import RECIPE_DB


class DashboardView(ctk.CTkFrame):
    """대시보드 뷰.

    Attributes:
        fridge (Fridge): 공유 냉장고 인스턴스
    """

    def __init__(self, parent: ctk.CTkFrame, fridge: Fridge) -> None:
        """대시보드 뷰를 초기화합니다.

        Args:
            parent: 부모 위젯
            fridge: 공유 냉장고 인스턴스
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.fridge = fridge
        self._recommender = RecipeRecommender()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_static_layout()

    # ── UI 뼈대 생성 ─────────────────────────────────────────

    def _build_static_layout(self) -> None:
        """변경되지 않는 뼈대 프레임을 생성합니다."""
        # 페이지 제목
        ctk.CTkLabel(
            self,
            text="🏠 대시보드",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=25, pady=(20, 10), sticky="w")

        # 통계 카드 영역 (동적으로 채워짐)
        self._card_area = ctk.CTkFrame(self, fg_color="transparent")
        self._card_area.grid(row=1, column=0, padx=25, pady=(0, 10), sticky="ew")
        for i in range(4):
            self._card_area.grid_columnconfigure(i, weight=1)

        # 하단 두 패널 (임박 리스트 | 오늘의 추천)
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, padx=25, pady=(0, 20), sticky="nswe")
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=1)

        self._expiring_panel = ctk.CTkFrame(bottom, corner_radius=10)
        self._expiring_panel.grid(row=0, column=0, padx=(0, 8), sticky="nswe")

        self._recipe_panel = ctk.CTkFrame(bottom, corner_radius=10)
        self._recipe_panel.grid(row=0, column=1, padx=(8, 0), sticky="nswe")

    # ── 새로고침 (공개 API) ────────────────────────────────

    def refresh(self) -> None:
        """냉장고 데이터를 다시 읽어 화면 전체를 갱신합니다."""
        self._refresh_cards()
        self._refresh_expiring()
        self._refresh_recommendation()

    # ── 통계 카드 ────────────────────────────────────────────

    def _refresh_cards(self) -> None:
        """상단 통계 카드 4개를 갱신합니다."""
        for w in self._card_area.winfo_children():
            w.destroy()

        total     = len(self.fridge.items)
        expiring  = len(self.fridge.get_expiring(threshold=3))
        expired   = len(self.fridge.get_expired())
        cookable  = sum(
            1 for r in RECIPE_DB
            if sum(1 for i in r["ingredients"] if i["name"] in self.fridge.items)
               / max(len(r["ingredients"]), 1) >= 0.5
        )

        cards = [
            ("📦", "전체 재료",  str(total),    "종",  None),
            ("⚠️", "임박 재료",  str(expiring), "종",  "#FFA500" if expiring else None),
            ("🚨", "만료 재료",  str(expired),  "종",  "#FF4444" if expired  else None),
            ("🍳", "가능 레시피", str(cookable), "개",  "#4CAF50"),
        ]
        for col, (emoji, title, val, unit, color) in enumerate(cards):
            self._make_card(col, emoji, title, val, unit, color)

    def _make_card(
        self,
        col: int,
        emoji: str,
        title: str,
        value: str,
        unit: str,
        bg: str | None,
    ) -> None:
        """단일 통계 카드 위젯을 생성합니다.

        Args:
            col: 그리드 열 번호
            emoji: 카드 상단 이모지
            title: 카드 제목
            value: 표시할 수치
            unit: 단위 문자열
            bg: 강조 배경색 (None이면 기본 프레임 색)
        """
        fg = bg if bg else ("gray90", "gray20")
        card = ctk.CTkFrame(self._card_area, corner_radius=12, fg_color=fg)
        card.grid(row=0, column=col, padx=6, pady=5, sticky="ew", ipady=8)

        text_color = "white" if bg else ("gray10", "gray90")
        sub_color  = "white" if bg else ("gray50", "gray60")

        ctk.CTkLabel(card, text=emoji,  font=ctk.CTkFont(size=26)).pack(pady=(18, 2))
        ctk.CTkLabel(card, text=title,  font=ctk.CTkFont(size=11), text_color=sub_color).pack()
        ctk.CTkLabel(
            card,
            text=f"{value} {unit}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=text_color,
        ).pack(pady=(2, 18))

    # ── 임박 재료 리스트 ─────────────────────────────────────

    def _refresh_expiring(self) -> None:
        """임박·만료 재료 리스트(상위 5개)를 갱신합니다."""
        for w in self._expiring_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self._expiring_panel,
            text="⚠️ 주의 재료 (상위 5개)",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(padx=15, pady=(15, 8), fill="x")

        # 만료 + 임박 재료를 합산, 중복 제거, 상위 5개
        seen: set[str] = set()
        items = []
        for item in self.fridge.get_expired() + self.fridge.get_expiring(threshold=5):
            if item.name not in seen:
                seen.add(item.name)
                items.append(item)
        items = items[:5]

        if not items:
            ctk.CTkLabel(
                self._expiring_panel,
                text="✅ 모든 재료가 양호합니다",
                text_color="#4CAF50",
                font=ctk.CTkFont(size=13),
            ).pack(padx=15, pady=20)
        else:
            for item in items:
                left = item.days_left()
                color  = "#FF4444" if left < 0 else ("#FFA500" if left <= 3 else "#888888")
                status = (f"만료 ({abs(left)}일 초과)" if left < 0
                          else f"{left}일 남음")

                row = ctk.CTkFrame(self._expiring_panel, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=4)
                ctk.CTkLabel(
                    row, text=item.name,
                    font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
                ).pack(side="left")
                ctk.CTkLabel(
                    row, text=status, text_color=color,
                    font=ctk.CTkFont(size=12), anchor="e",
                ).pack(side="right")

    # ── 오늘의 추천 ──────────────────────────────────────────

    def _refresh_recommendation(self) -> None:
        """오늘의 추천 요리 1개를 갱신합니다."""
        for w in self._recipe_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self._recipe_panel,
            text="🍳 오늘의 추천 요리",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(padx=15, pady=(15, 8), fill="x")

        results = self._recommender.recommend(self.fridge, top_n=1)
        if not results:
            ctk.CTkLabel(
                self._recipe_panel, text="추천 레시피가 없습니다",
                text_color="gray",
            ).pack(padx=15, pady=20)
            return

        recipe, score = results[0]
        ings  = recipe["ingredients"]
        have  = [i for i in ings if i["name"] in self.fridge.items]
        ratio = len(have) / len(ings) if ings else 0

        ctk.CTkLabel(
            self._recipe_panel,
            text=recipe["name"],
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(padx=15, pady=(0, 4))

        ctk.CTkLabel(
            self._recipe_panel,
            text=f"추천 점수: {score:.2f}  |  {recipe['servings']}인분",
            text_color="#1F6AA5",
            font=ctk.CTkFont(size=12),
        ).pack(padx=15)

        # 재료 매칭 진행 바
        ctk.CTkLabel(
            self._recipe_panel,
            text=f"보유 재료  {len(have)} / {len(ings)}",
            font=ctk.CTkFont(size=12),
        ).pack(padx=15, pady=(12, 2))
        pb = ctk.CTkProgressBar(self._recipe_panel, height=12)
        pb.pack(padx=20, pady=(0, 10), fill="x")
        pb.set(ratio)

        # 임박 재료 강조
        urgent = [i for i in have if self.fridge.items[i["name"]].days_left() <= 3]
        if urgent:
            ctk.CTkLabel(
                self._recipe_panel,
                text="🔥 " + ", ".join(i["name"] for i in urgent) + " 먼저 쓰세요!",
                text_color="#FFA500",
                font=ctk.CTkFont(size=12),
            ).pack(padx=15, pady=(0, 15))
        else:
            ctk.CTkLabel(
                self._recipe_panel,
                text=f"🍽️  {recipe['servings']}인분 기준",
                text_color="gray",
                font=ctk.CTkFont(size=12),
            ).pack(padx=15, pady=(0, 15))
