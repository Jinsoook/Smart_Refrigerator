"""스마트 냉장고 관리 시스템 v2.0 - 요리 추천 뷰.

RecipeRecommender.recommend(top_n=3) 결과를 카드 3개로 표시합니다.
각 카드: 점수, 재료 진행 바, 재료 목록, 영양 정보, 레시피 보기,
요리 완료 버튼.
"""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from database import NUTRITION_DB
from fridge import Fridge
from recommender import RecipeRecommender


class RecipeView(ctk.CTkFrame):
    """요리 추천 뷰."""

    def __init__(self, parent: ctk.CTkFrame, fridge: Fridge) -> None:
        """요리 추천 뷰를 초기화합니다."""
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.fridge = fridge
        self._rec = RecipeRecommender()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_cards_area()

    def _build_header(self) -> None:
        """상단 제목 + 새로고침 버튼을 구성합니다."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        ctk.CTkLabel(
            header,
            text=" 요리 추천",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            header,
            text="현재 보유 재료와 유통기한을 고려해 점수 순으로 추천합니다",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            header,
            text=" 새로고침",
            width=100,
            command=self.refresh,
        ).pack(side="right", padx=5)

    def _build_cards_area(self) -> None:
        """카드 3개를 배치할 스크롤 가능 영역을 생성합니다."""
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self._scroll.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="nswe")

        for i in range(3):
            self._scroll.grid_columnconfigure(i, weight=1)

    def refresh(self) -> None:
        """추천 레시피를 다시 계산하고 카드를 갱신합니다."""
        for widget in self._scroll.winfo_children():
            widget.destroy()

        results = self._rec.recommend(self.fridge, top_n=3)
        if not results:
            ctk.CTkLabel(
                self._scroll,
                text="추천할 레시피가 없습니다.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            ).grid(row=0, column=0, padx=20, pady=40)
            return

        for col, (recipe, score) in enumerate(results):
            self._make_card(col, recipe, score)

    def _make_card(self, col: int, recipe: dict, score: float) -> None:
        """단일 레시피 카드 위젯을 생성합니다."""
        card = ctk.CTkFrame(self._scroll, corner_radius=12)
        card.grid(row=0, column=col, padx=8, pady=5, sticky="nswe")

        ingredients = recipe["ingredients"]
        have = [i for i in ingredients if i["name"] in self.fridge.items]
        missing = [i for i in ingredients if i["name"] not in self.fridge.items]
        urgent = [
            i
            for i in have
            if self.fridge.items[i["name"]].days_left() <= 3
        ]
        ratio = len(have) / len(ingredients) if ingredients else 0

        rank_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
        badge_color = rank_colors[col] if col < 3 else "#888888"

        ctk.CTkFrame(card, fg_color=badge_color, corner_radius=0, height=6).pack(
            fill="x"
        )

        ctk.CTkLabel(
            card,
            text=recipe["name"],
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(padx=15, pady=(12, 2))

        ctk.CTkLabel(
            card,
            text=f"추천 점수: {score:.2f} | {recipe['servings']}인분",
            text_color="#1F6AA5",
            font=ctk.CTkFont(size=12),
        ).pack(padx=15)

        ctk.CTkLabel(
            card,
            text=f"보유 재료 {len(have)} / {len(ingredients)}",
            font=ctk.CTkFont(size=12),
        ).pack(padx=15, pady=(10, 2))

        progress = ctk.CTkProgressBar(card, height=10)
        progress.pack(padx=18, pady=(0, 10), fill="x")
        progress.set(ratio)

        ctk.CTkLabel(
            card,
            text="재료",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(padx=15, fill="x")

        ingredients_frame = ctk.CTkFrame(card, fg_color="transparent")
        ingredients_frame.pack(padx=15, pady=(2, 8), fill="x")

        urgent_names = [i["name"] for i in urgent]
        missing_names = [i["name"] for i in missing]
        for ingredient in ingredients:
            name = ingredient["name"]
            if name in missing_names:
                color, prefix = "#AAAAAA", "x"
            elif name in urgent_names:
                color, prefix = "#FFA500", "!"
            else:
                color, prefix = "#4CAF50", "o"

            ctk.CTkLabel(
                ingredients_frame,
                text=f"{prefix} {name} {ingredient['amount']}{ingredient['unit']}",
                text_color=color,
                font=ctk.CTkFont(size=12),
                anchor="w",
            ).pack(fill="x")

        nutrition_text = self._calc_nutrition(recipe)
        if nutrition_text:
            ctk.CTkFrame(card, height=1, fg_color=("gray80", "gray40")).pack(
                fill="x",
                padx=15,
                pady=5,
            )
            ctk.CTkLabel(
                card,
                text=f"1인분 {nutrition_text}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                wraplength=200,
            ).pack(padx=15, pady=(0, 8))

        ctk.CTkButton(
            card,
            text="레시피 보기",
            height=34,
            command=lambda r=recipe: self._open_detail(r),
        ).pack(padx=15, pady=(5, 6), fill="x")

        ctk.CTkButton(
            card,
            text="요리 완료",
            height=34,
            fg_color="#4CAF50",
            hover_color="#3D8B40",
            command=lambda r=recipe: self._complete_recipe(r),
        ).pack(padx=15, pady=(0, 15), fill="x")

    def _calc_nutrition(self, recipe: dict) -> str:
        """레시피 1인분 영양 정보 요약 문자열을 반환합니다."""
        kcal = protein = 0.0
        calculated = False

        for ingredient in recipe["ingredients"]:
            nutrition = NUTRITION_DB.get(ingredient["name"])
            if nutrition and ingredient["unit"] == "g":
                ratio = ingredient["amount"] / 100.0
                kcal += nutrition["kcal"] * ratio
                protein += nutrition["protein"] * ratio
                calculated = True

        if not calculated:
            return ""

        servings = recipe["servings"]
        return f"{kcal / servings:.0f} kcal | 단백질 {protein / servings:.1f}g"

    def _open_detail(self, recipe: dict) -> None:
        """레시피 상세 다이얼로그를 엽니다."""
        from gui.dialogs import RecipeDetailDialog

        RecipeDetailDialog(self, recipe)

    def _complete_recipe(self, recipe: dict) -> None:
        """요리 완료 처리 후 레시피에 필요한 재료를 냉장고에서 차감합니다."""
        shortage_messages = self._get_shortage_messages(recipe)
        if shortage_messages:
            messagebox.showwarning(
                "재료 부족",
                "다음 재료가 부족해서 요리를 완료할 수 없습니다.\n\n"
                + "\n".join(shortage_messages),
            )
            return

        confirmed = messagebox.askyesno(
            "요리 완료 확인",
            "정말 이 요리를 완료하고 재료를 차감할까요?",
        )
        if not confirmed:
            return

        try:
            for ingredient in recipe["ingredients"]:
                self.fridge.use_ingredient(ingredient["name"], ingredient["amount"])
        except (KeyError, ValueError) as error:
            messagebox.showerror("재료 차감 실패", str(error))
            return

        messagebox.showinfo(
            "요리 완료",
            "요리 완료! 사용한 재료가 냉장고에서 차감되었습니다.",
        )
        self._refresh_after_complete()

    def _get_shortage_messages(self, recipe: dict) -> list[str]:
        """레시피에 필요한 재료의 보유 여부와 수량 부족 여부를 검사합니다."""
        shortage_messages = []

        for ingredient in recipe["ingredients"]:
            name = ingredient["name"]
            required_amount = ingredient["amount"]
            required_unit = ingredient["unit"]
            fridge_item = self.fridge.items.get(name)

            if fridge_item is None:
                shortage_messages.append(
                    f"- {name}: 필요 {required_amount}{required_unit}, 보유 없음"
                )
                continue

            if fridge_item.quantity < required_amount:
                shortage_messages.append(
                    f"- {name}: 필요 {required_amount}{required_unit}, "
                    f"보유 {fridge_item.quantity}{fridge_item.unit}"
                )

        return shortage_messages

    def _refresh_after_complete(self) -> None:
        """요리 완료 후 추천 화면과 다른 주요 화면을 새로고침합니다."""
        self.refresh()

        app = self.winfo_toplevel()
        views = getattr(app, "views", None) or getattr(app, "_views", None)
        if not isinstance(views, dict):
            return

        for view_name in ("dashboard", "inventory", "shopping"):
            view = views.get(view_name)
            if view is not None and hasattr(view, "refresh"):
                view.refresh()
