"""
스마트 냉장고 관리 시스템 v2.0 — 장보기 리스트 뷰

analytics.generate_shopping_list() 결과를 체크박스 리스트로 표시합니다.
항목별 쿠팡 검색 링크를 webbrowser.open()으로 엽니다.
"""

from __future__ import annotations
import webbrowser
import customtkinter as ctk
from fridge import Fridge
from analytics import generate_shopping_list


class ShoppingView(ctk.CTkFrame):
    """장보기 리스트 뷰.

    Attributes:
        fridge (Fridge): 공유 냉장고 인스턴스
    """

    def __init__(self, parent: ctk.CTkFrame, fridge: Fridge) -> None:
        """장보기 리스트 뷰를 초기화합니다.

        Args:
            parent: 부모 위젯
            fridge: 공유 냉장고 인스턴스
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.fridge = fridge
        self._check_vars: list[ctk.IntVar] = []  # GC 방지용 참조 보관

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_list_area()

    # ── UI 구성 ───────────────────────────────────────────────

    def _build_header(self) -> None:
        """상단 제목·안내 문구·자동 생성 버튼."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        ctk.CTkLabel(
            header, text="🛒 장보기 리스트",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            header,
            text="재고 부족 + 자주 쓰는 재료를 자동으로 분석합니다",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            header, text="🔄 자동 생성", width=110, command=self.refresh,
        ).pack(side="right", padx=5)

    def _build_list_area(self) -> None:
        """체크박스 리스트가 들어갈 스크롤 가능 영역."""
        self._scroll = ctk.CTkScrollableFrame(
            self, corner_radius=10, fg_color="transparent"
        )
        self._scroll.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="nswe")
        self._scroll.grid_columnconfigure(0, weight=1)

    # ── 새로고침 ─────────────────────────────────────────────

    def refresh(self) -> None:
        """장보기 리스트를 재생성합니다."""
        for w in self._scroll.winfo_children():
            w.destroy()
        self._check_vars.clear()

        items = generate_shopping_list(self.fridge, self.fridge.history)

        if not items:
            ctk.CTkLabel(
                self._scroll,
                text="✅ 구매가 필요한 재료가 없습니다",
                font=ctk.CTkFont(size=14),
                text_color="#4CAF50",
            ).grid(row=0, column=0, padx=20, pady=40)
            return

        # 헤더 행
        header_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))
        ctk.CTkLabel(
            header_frame,
            text=f"총 {len(items)}개 항목",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left")

        # 항목 행 생성
        for idx, entry in enumerate(items):
            self._make_item_row(idx + 1, entry)

    def _make_item_row(self, row_idx: int, entry: dict) -> None:
        """단일 장보기 항목 행을 생성합니다.

        Args:
            row_idx: 그리드 행 번호
            entry: {"name": ..., "reason": ..., "link": ...} 딕셔너리
        """
        # 체크박스 IntVar
        var = ctk.IntVar(value=0)
        self._check_vars.append(var)  # GC 방지

        # 행 카드 프레임
        row_card = ctk.CTkFrame(self._scroll, corner_radius=8)
        row_card.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=4)
        row_card.grid_columnconfigure(1, weight=1)

        # 체크박스
        cb = ctk.CTkCheckBox(
            row_card, text="", variable=var, width=30,
            command=lambda v=var, card=row_card: self._on_check(v, card),
        )
        cb.grid(row=0, column=0, padx=(12, 5), pady=12, rowspan=2)

        # 재료명
        name_lbl = ctk.CTkLabel(
            row_card,
            text=f"🛍️  {entry['name']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        name_lbl.grid(row=0, column=1, padx=5, pady=(12, 2), sticky="w")

        # 사유
        reason_lbl = ctk.CTkLabel(
            row_card,
            text=entry["reason"],
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        reason_lbl.grid(row=1, column=1, padx=5, pady=(0, 12), sticky="w")

        # 쿠팡 버튼
        link = entry["link"]
        ctk.CTkButton(
            row_card,
            text="🛒 쿠팡 검색",
            width=110,
            height=32,
            fg_color="#FF6000",
            hover_color="#CC4D00",
            command=lambda url=link: webbrowser.open(url),
        ).grid(row=0, column=2, rowspan=2, padx=12, pady=8)

        # 태그: 나중에 체크 상태에서 색을 변경할 위젯 참조
        row_card._name_lbl   = name_lbl    # type: ignore[attr-defined]
        row_card._reason_lbl = reason_lbl  # type: ignore[attr-defined]

    def _on_check(self, var: ctk.IntVar, card: ctk.CTkFrame) -> None:
        """체크박스 토글 시 항목 색상을 변경합니다.

        구매 완료 = 회색으로 표시.

        Args:
            var: 체크 상태 IntVar
            card: 해당 항목의 행 카드 프레임
        """
        done = bool(var.get())
        color = ("gray60", "gray50") if done else ("gray10", "gray90")
        card._name_lbl.configure(text_color=color)    # type: ignore[attr-defined]
        card._reason_lbl.configure(text_color=color)  # type: ignore[attr-defined]
