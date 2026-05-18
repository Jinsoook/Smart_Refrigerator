"""
스마트 냉장고 관리 시스템 v2.0 — 요리 추천 뷰

RecipeRecommender.recommend(top_n=3) 결과를 카드 3개로 표시합니다.
각 카드: 점수·재료 진행 바·재료 목록(색상 구분)·영양 정보·레시피 보기 버튼.
"""

from __future__ import annotations
import customtkinter as ctk
from fridge import Fridge
from recommender import RecipeRecommender
from database import NUTRITION_DB


class RecipeView(ctk.CTkFrame):
    """요리 추천 뷰.

    Attributes:
        fridge (Fridge): 공유 냉장고 인스턴스
    """

    def __init__(self, parent: ctk.CTkFrame, fridge: Fridge) -> None:
        """요리 추천 뷰를 초기화합니다.

        Args:
            parent: 부모 위젯
            fridge: 공유 냉장고 인스턴스
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.fridge = fridge
        self._rec   = RecipeRecommender()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_cards_area()

    # ── UI 구성 ───────────────────────────────────────────────

    def _build_header(self) -> None:
        """상단 제목 + 새로고침 버튼을 구성합니다."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        ctk.CTkLabel(
            header, text="🍳 요리 추천",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            header,
            text="현재 보유 재료와 유통기한을 고려해 점수 순으로 추천합니다",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            header, text="🔄 새로고침", width=100, command=self.refresh,
        ).pack(side="right", padx=5)

    def _build_cards_area(self) -> None:
        """카드 3개를 배치할 스크롤 가능 영역을 생성합니다."""
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self._scroll.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="nswe")
        for i in range(3):
            self._scroll.grid_columnconfigure(i, weight=1)

    # ── 새로고침 ─────────────────────────────────────────────

    def refresh(self) -> None:
        """추천 레시피를 다시 계산하고 카드를 갱신합니다."""
        for w in self._scroll.winfo_children():
            w.destroy()

        results = self._rec.recommend(self.fridge, top_n=3)
        if not results:
            ctk.CTkLabel(
                self._scroll, text="추천할 레시피가 없습니다.",
                font=ctk.CTkFont(size=14), text_color="gray",
            ).grid(row=0, column=0, padx=20, pady=40)
            return

        for col, (recipe, score) in enumerate(results):
            self._make_card(col, recipe, score)

    # ── 카드 생성 ────────────────────────────────────────────

    def _make_card(self, col: int, recipe: dict, score: float) -> None:
        """단일 레시피 카드 위젯을 생성합니다.

        Args:
            col: 배치할 그리드 열
            recipe: RECIPE_DB 레시피 딕셔너리
            score: 추천 점수
        """
        card = ctk.CTkFrame(self._scroll, corner_radius=12)
        card.grid(row=0, column=col, padx=8, pady=5, sticky="nswe")

        ings    = recipe["ingredients"]
        have    = [i for i in ings if i["name"] in self.fridge.items]
        missing = [i for i in ings if i["name"] not in self.fridge.items]
        urgent  = [
            i for i in have
            if self.fridge.items[i["name"]].days_left() <= 3
        ]
        ratio   = len(have) / len(ings) if ings else 0

        # 요리 이름 + 순위 배지
        rank_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # 금·은·동
        rank = col + 1
        badge_color = rank_colors[col] if col < 3 else "#888888"

        top_bar = ctk.CTkFrame(card, fg_color=badge_color, corner_radius=0,
                                height=6)
        top_bar.pack(fill="x")

        ctk.CTkLabel(
            card,
            text=f"{'🥇' if rank==1 else '🥈' if rank==2 else '🥉'} {recipe['name']}",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(padx=15, pady=(12, 2))

        ctk.CTkLabel(
            card,
            text=f"추천 점수: {score:.2f}  |  {recipe['servings']}인분",
            text_color="#1F6AA5",
            font=ctk.CTkFont(size=12),
        ).pack(padx=15)

        # 보유율 진행 바
        ctk.CTkLabel(
            card,
            text=f"보유 재료  {len(have)} / {len(ings)}",
            font=ctk.CTkFont(size=12),
        ).pack(padx=15, pady=(10, 2))
        pb = ctk.CTkProgressBar(card, height=10)
        pb.pack(padx=18, pady=(0, 10), fill="x")
        pb.set(ratio)

        # 재료 목록 (보유=초록, 임박=주황, 부족=회색)
        ctk.CTkLabel(
            card, text="재료", font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        ).pack(padx=15, fill="x")

        ings_frame = ctk.CTkFrame(card, fg_color="transparent")
        ings_frame.pack(padx=15, pady=(2, 8), fill="x")

        for ing in ings:
            name = ing["name"]
            if name not in self.fridge.items:
                color, prefix = "#AAAAAA", "✗"
            elif name in [i["name"] for i in urgent]:
                color, prefix = "#FFA500", "⚠"
            else:
                color, prefix = "#4CAF50", "✓"

            ctk.CTkLabel(
                ings_frame,
                text=f"{prefix} {name}  {ing['amount']}{ing['unit']}",
                text_color=color,
                font=ctk.CTkFont(size=12),
                anchor="w",
            ).pack(fill="x")

        # 1인분 영양 정보
        nutrition_text = self._calc_nutrition(recipe)
        if nutrition_text:
            ctk.CTkFrame(card, height=1, fg_color=("gray80", "gray40")).pack(
                fill="x", padx=15, pady=5
            )
            ctk.CTkLabel(
                card,
                text=f"🥗 1인분  {nutrition_text}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                wraplength=200,
            ).pack(padx=15, pady=(0, 8))

        # 레시피 보기 버튼
        ctk.CTkButton(
            card,
            text="📖 레시피 보기",
            height=34,
            command=lambda r=recipe: self._open_detail(r),
        ).pack(padx=15, pady=(5, 15), fill="x")

    # ── 영양 계산 ────────────────────────────────────────────

    def _calc_nutrition(self, recipe: dict) -> str:
        """레시피 1인분 영양 정보 요약 문자열을 반환합니다.

        단위가 'g'인 재료만 계산합니다.

        Args:
            recipe: RECIPE_DB 레시피 딕셔너리

        Returns:
            str: "360kcal | 단백질 20.1g" 형태, 데이터 없으면 빈 문자열
        """
        kcal = protein = 0.0
        calculated = False
        for ing in recipe["ingredients"]:
            n = NUTRITION_DB.get(ing["name"])
            if n and ing["unit"] == "g":
                r = ing["amount"] / 100.0
                kcal    += n["kcal"]    * r
                protein += n["protein"] * r
                calculated = True
        if not calculated:
            return ""
        s = recipe["servings"]
        return f"{kcal/s:.0f} kcal | 단백질 {protein/s:.1f}g"

    # ── 상세 다이얼로그 ───────────────────────────────────────

    def _open_detail(self, recipe: dict) -> None:
        """레시피 상세 다이얼로그를 엽니다.

        Args:
            recipe: 표시할 레시피 딕셔너리
        """
        from gui.dialogs import RecipeDetailDialog
        RecipeDetailDialog(self, recipe)
