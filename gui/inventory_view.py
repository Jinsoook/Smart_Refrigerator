"""
스마트 냉장고 관리 시스템 v2.0 — 재고 관리 뷰

카테고리 필터·검색·추가/사용/폐기 버튼 툴바와
ttk.Treeview 기반 테이블을 제공합니다.
행 색상: 만료=빨강, 임박=노랑, 정상=기본.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from fridge import Fridge


# 카테고리 목록 (필터 드롭다운용)
_CATEGORIES = ["전체", "유제품", "육류", "채소", "곡물", "가공식품"]


class InventoryView(ctk.CTkFrame):
    """재고 관리 뷰.

    Attributes:
        fridge (Fridge): 공유 냉장고 인스턴스
    """

    def __init__(self, parent: ctk.CTkFrame, fridge: Fridge) -> None:
        """재고 관리 뷰를 초기화합니다.

        Args:
            parent: 부모 위젯
            fridge: 공유 냉장고 인스턴스
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.fridge = fridge

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_table()

    # ── UI 구성 ───────────────────────────────────────────────

    def _build_toolbar(self) -> None:
        """상단 툴바(필터·검색·버튼)를 구성합니다."""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        # 페이지 제목
        ctk.CTkLabel(
            toolbar, text="📦 재고 관리",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left", padx=(5, 20))

        # 카테고리 필터
        ctk.CTkLabel(toolbar, text="카테고리:").pack(side="left")
        self._cat_var = ctk.StringVar(value="전체")
        cat_menu = ctk.CTkOptionMenu(
            toolbar,
            values=_CATEGORIES,
            variable=self._cat_var,
            width=100,
            command=lambda _: self.refresh(),
        )
        cat_menu.pack(side="left", padx=(4, 15))

        # 검색창
        self._search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            toolbar, textvariable=self._search_var, placeholder_text="🔍 검색...", width=160
        )
        search_entry.pack(side="left", padx=(0, 4))
        search_entry.bind("<Return>", lambda _: self.refresh())
        ctk.CTkButton(
            toolbar, text="검색", width=60, command=self.refresh
        ).pack(side="left", padx=(0, 20))

        # 동작 버튼
        ctk.CTkButton(
            toolbar, text="➕ 추가", width=80, fg_color="#4CAF50",
            hover_color="#388E3C", command=self._open_add,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            toolbar, text="🍴 사용", width=80, command=self._open_use,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            toolbar, text="🗑️ 폐기", width=80, fg_color="#FF4444",
            hover_color="#C62828", command=self._discard_selected,
        ).pack(side="left", padx=4)

    def _build_table(self) -> None:
        """중앙 ttk.Treeview 테이블을 구성합니다."""
        table_frame = tk.Frame(self, bg="#F0F0F0")
        table_frame.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="nswe")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # ttk 스타일 설정
        style = ttk.Style()
        style.configure("Inv.Treeview",
            background="#FAFAFA",
            fieldbackground="#FAFAFA",
            foreground="#111111",
            rowheight=30,
            font=("", 12),
        )
        style.configure("Inv.Treeview.Heading",
            font=("", 12, "bold"),
            background="#E0E0E0",
            foreground="#111111",
        )
        style.map("Inv.Treeview", background=[("selected", "#1F6AA5")])

        cols = ("name", "qty", "unit", "category", "bought", "days_left", "status")
        self._tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            style="Inv.Treeview",
            selectmode="browse",
        )

        headers = {
            "name":      ("식재료명",    160),
            "qty":       ("수량",         80),
            "unit":      ("단위",         70),
            "category":  ("카테고리",    100),
            "bought":    ("구입일",      120),
            "days_left": ("남은 기한",   100),
            "status":    ("상태",         90),
        }
        for col, (text, width) in headers.items():
            self._tree.heading(col, text=text)
            self._tree.column(col, width=width, anchor="center", minwidth=60)
        self._tree.column("name", anchor="w")

        # 행 색상 태그 정의
        self._tree.tag_configure("expired",  background="#FFCCCC", foreground="#880000")
        self._tree.tag_configure("expiring", background="#FFF3CD", foreground="#664D03")
        self._tree.tag_configure("normal",   background="#FAFAFA", foreground="#111111")

        # 스크롤바
        sb_y = ttk.Scrollbar(table_frame, orient="vertical",   command=self._tree.yview)
        sb_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        self._tree.grid(row=0, column=0, sticky="nswe")
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")

        # 더블클릭 → 사용 다이얼로그
        self._tree.bind("<Double-1>", lambda _: self._open_use())

    # ── 새로고침 ─────────────────────────────────────────────

    def refresh(self) -> None:
        """현재 필터·검색 조건에 맞게 테이블을 갱신합니다."""
        self._tree.delete(*self._tree.get_children())

        keyword  = self._search_var.get().strip()
        category = self._cat_var.get()

        for item in sorted(self.fridge.items.values(), key=lambda x: x.name):
            # 카테고리 필터
            if category != "전체" and item.category != category:
                continue
            # 키워드 검색
            if keyword and keyword not in item.name:
                continue

            left = item.days_left()
            if left < 0:
                tag    = "expired"
                status = "🚨 만료"
                left_str = f"-{abs(left)}일"
            elif left <= 3:
                tag    = "expiring"
                status = "⚠️ 임박"
                left_str = f"{left}일"
            else:
                tag    = "normal"
                status = "✅ 정상"
                left_str = f"{left}일" if left < 999 else "—"

            self._tree.insert("", "end", values=(
                item.name,
                item.quantity,
                item.unit,
                item.category,
                item.purchase_date.strftime("%Y-%m-%d"),
                left_str,
                status,
            ), tags=(tag,))

    # ── 버튼 핸들러 ──────────────────────────────────────────

    def _selected_name(self) -> str | None:
        """Treeview에서 선택된 행의 식재료명을 반환합니다.

        Returns:
            str | None: 선택된 식재료명. 없으면 None.
        """
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.item(sel[0])["values"][0]

    def _open_add(self) -> None:
        """식재료 추가 다이얼로그를 엽니다."""
        from gui.dialogs import AddIngredientDialog
        AddIngredientDialog(self, self.fridge, on_success=self.refresh)

    def _open_use(self) -> None:
        """식재료 사용 다이얼로그를 엽니다."""
        name = self._selected_name()
        if not name:
            messagebox.showinfo("안내", "사용할 식재료를 먼저 선택하세요.")
            return
        from gui.dialogs import UseIngredientDialog
        UseIngredientDialog(self, self.fridge, name, on_success=self.refresh)

    def _discard_selected(self) -> None:
        """선택된 식재료를 폐기합니다 (확인 후)."""
        name = self._selected_name()
        if not name:
            messagebox.showinfo("안내", "폐기할 식재료를 먼저 선택하세요.")
            return
        if messagebox.askyesno("폐기 확인", f"'{name}'을(를) 폐기하시겠습니까?"):
            try:
                self.fridge.discard_ingredient(name)
                self.refresh()
            except KeyError as e:
                messagebox.showerror("오류", str(e))
