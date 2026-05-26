"""
스마트 냉장고 관리 시스템 v2.0 — 모달 다이얼로그

CTkToplevel 기반 다이얼로그 3종:
  - AddIngredientDialog  : 식재료 추가
  - UseIngredientDialog  : 식재료 사용
  - RecipeDetailDialog   : 레시피 상세 보기
"""

from __future__ import annotations
import datetime
from tkinter import messagebox
import customtkinter as ctk
from fridge import Fridge
from database import EXPIRY_DB


# 단위 선택 목록
_UNITS = ["g", "kg", "ml", "L", "개", "대", "모", "장", "통", "봉"]


class _BaseDialog(ctk.CTkToplevel):
    """모든 다이얼로그의 공통 기반 클래스.

    부모 창 중앙에 배치하고 grab_set()으로 포커스를 고정합니다.
    """

    def __init__(self, parent: ctk.CTkFrame, title: str, width: int, height: int) -> None:
        """다이얼로그를 초기화합니다.

        Args:
            parent: 부모 위젯
            title: 윈도우 제목
            width: 다이얼로그 폭(px)
            height: 다이얼로그 높이(px)
        """
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.geometry(f"{width}x{height}")
        self.after(50, self._center_and_grab)  # 렌더링 후 중앙 배치·포커스 고정

    def _center_and_grab(self) -> None:
        """부모 윈도우 중앙에 배치하고 모달 포커스를 설정합니다."""
        self.update_idletasks()
        parent = self.master
        # 최상위 창 기준으로 중앙 계산
        try:
            root = parent.winfo_toplevel()
            px = root.winfo_rootx()
            py = root.winfo_rooty()
            pw = root.winfo_width()
            ph = root.winfo_height()
        except Exception:
            px, py, pw, ph = 100, 100, 1100, 700

        dw = self.winfo_width()
        dh = self.winfo_height()
        x  = px + (pw - dw) // 2
        y  = py + (ph - dh) // 2
        self.geometry(f"+{x}+{y}")
        self.grab_set()
        self.focus_force()


# ── 식재료 추가 다이얼로그 ────────────────────────────────────

class AddIngredientDialog(_BaseDialog):
    """식재료 추가 다이얼로그.

    이름(ComboBox), 수량, 단위, 구입일을 입력받아
    fridge.add_ingredient()를 호출합니다.

    Attributes:
        fridge (Fridge): 냉장고 인스턴스
        on_success (callable): 추가 성공 후 호출할 콜백
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        fridge: Fridge,
        on_success: object = None,
    ) -> None:
        """식재료 추가 다이얼로그를 초기화합니다.

        Args:
            parent: 부모 위젯
            fridge: 공유 냉장고 인스턴스
            on_success: 추가 성공 후 실행할 콜백 (예: view.refresh)
        """
        super().__init__(parent, "➕ 식재료 추가", 400, 360)
        self.fridge     = fridge
        self.on_success = on_success
        self._build()

    def _build(self) -> None:
        """입력 폼 UI를 구성합니다."""
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="➕ 식재료 추가",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=25, pady=(20, 15))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, padx=25, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        # 식재료 이름 (EXPIRY_DB 목록 + 직접 입력)
        ctk.CTkLabel(form, text="이름", anchor="w").grid(
            row=0, column=0, padx=(0, 10), pady=6, sticky="w"
        )
        self._name_cb = ctk.CTkComboBox(
            form, values=sorted(EXPIRY_DB.keys()), width=220
        )
        self._name_cb.set("")
        self._name_cb.grid(row=0, column=1, pady=6, sticky="ew")

        # 수량
        ctk.CTkLabel(form, text="수량", anchor="w").grid(
            row=1, column=0, padx=(0, 10), pady=6, sticky="w"
        )
        self._qty_entry = ctk.CTkEntry(form, placeholder_text="예) 200")
        self._qty_entry.grid(row=1, column=1, pady=6, sticky="ew")

        # 단위
        ctk.CTkLabel(form, text="단위", anchor="w").grid(
            row=2, column=0, padx=(0, 10), pady=6, sticky="w"
        )
        self._unit_menu = ctk.CTkOptionMenu(form, values=_UNITS, width=100)
        self._unit_menu.set("g")
        self._unit_menu.grid(row=2, column=1, pady=6, sticky="w")

        # 구입일
        today_str = datetime.date.today().isoformat()
        ctk.CTkLabel(form, text="구입일", anchor="w").grid(
            row=3, column=0, padx=(0, 10), pady=6, sticky="w"
        )
        self._date_entry = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD")
        self._date_entry.insert(0, today_str)
        self._date_entry.grid(row=3, column=1, pady=6, sticky="ew")

        # 버튼 행
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, padx=25, pady=(20, 20), sticky="ew")
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_row, text="추가", fg_color="#4CAF50", hover_color="#388E3C",
            command=self._on_add,
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(
            btn_row, text="취소", fg_color="gray",
            command=self.destroy,
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def _on_add(self) -> None:
        """[추가] 버튼 핸들러: 입력 검증 후 fridge.add_ingredient() 호출."""
        name = self._name_cb.get().strip()
        if not name:
            messagebox.showwarning("입력 오류", "식재료 이름을 입력하세요.", parent=self)
            return

        # 수량 검증
        try:
            qty = float(self._qty_entry.get().strip())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("입력 오류", "수량은 양수 숫자여야 합니다.", parent=self)
            return

        unit = self._unit_menu.get()

        # 날짜 검증
        try:
            purchase_date = datetime.date.fromisoformat(self._date_entry.get().strip())
        except ValueError:
            messagebox.showwarning(
                "입력 오류", "날짜 형식이 올바르지 않습니다.\nYYYY-MM-DD 형식으로 입력하세요.",
                parent=self,
            )
            return

        try:
            self.fridge.add_ingredient(name, qty, unit, purchase_date)
            if callable(self.on_success):
                self.on_success()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("오류", str(e), parent=self)


# ── 식재료 사용 다이얼로그 ────────────────────────────────────

class UseIngredientDialog(_BaseDialog):
    """식재료 사용(차감) 다이얼로그.

    선택된 식재료의 사용량을 입력받아
    fridge.use_ingredient()를 호출합니다.

    Attributes:
        fridge (Fridge): 냉장고 인스턴스
        name (str): 사용할 식재료 이름
        on_success (callable): 성공 후 호출할 콜백
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        fridge: Fridge,
        name: str,
        on_success: object = None,
    ) -> None:
        """식재료 사용 다이얼로그를 초기화합니다.

        Args:
            parent: 부모 위젯
            fridge: 공유 냉장고 인스턴스
            name: 사용할 식재료 이름
            on_success: 성공 후 실행할 콜백
        """
        super().__init__(parent, "🍴 식재료 사용", 360, 280)
        self.fridge     = fridge
        self.name       = name
        self.on_success = on_success
        self._build()

    def _build(self) -> None:
        """사용량 입력 폼 UI를 구성합니다."""
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="🍴 식재료 사용",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=25, pady=(20, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, padx=25, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        # 재료명 (읽기 전용)
        ctk.CTkLabel(form, text="재료명", anchor="w").grid(
            row=0, column=0, padx=(0, 10), pady=8, sticky="w"
        )
        ctk.CTkLabel(
            form,
            text=self.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).grid(row=0, column=1, pady=8, sticky="w")

        # 현재 보유량 표시
        item = self.fridge.items.get(self.name)
        current = f"{item.quantity} {item.unit}" if item else "—"
        ctk.CTkLabel(form, text="현재 보유", anchor="w").grid(
            row=1, column=0, padx=(0, 10), pady=8, sticky="w"
        )
        ctk.CTkLabel(
            form, text=current, text_color="#4CAF50",
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=1, pady=8, sticky="w")

        # 사용량 입력
        ctk.CTkLabel(form, text="사용량", anchor="w").grid(
            row=2, column=0, padx=(0, 10), pady=8, sticky="w"
        )
        self._qty_entry = ctk.CTkEntry(form, placeholder_text="사용할 양")
        self._qty_entry.grid(row=2, column=1, pady=8, sticky="ew")
        self._qty_entry.focus()

        # 버튼 행
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, padx=25, pady=(15, 20), sticky="ew")
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_row, text="사용", command=self._on_use,
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(
            btn_row, text="취소", fg_color="gray",
            command=self.destroy,
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def _on_use(self) -> None:
        """[사용] 버튼 핸들러: 검증 후 fridge.use_ingredient() 호출."""
        try:
            qty = float(self._qty_entry.get().strip())
            if qty <= 0:
                raise ValueError("사용량은 양수여야 합니다.")
        except ValueError:
            messagebox.showwarning("입력 오류", "올바른 양수 숫자를 입력하세요.", parent=self)
            return

        try:
            self.fridge.use_ingredient(self.name, qty)
            if callable(self.on_success):
                self.on_success()
            self.destroy()
        except (KeyError, ValueError) as e:
            messagebox.showerror("오류", str(e), parent=self)


# ── 레시피 상세 다이얼로그 ────────────────────────────────────

class RecipeDetailDialog(_BaseDialog):
    """레시피 상세 다이얼로그.

    요리 이름·재료 전체·조리법을 스크롤 가능한 형태로 표시합니다.

    Attributes:
        recipe (dict): RECIPE_DB 레시피 딕셔너리
    """

    def __init__(self, parent: ctk.CTkFrame, recipe: dict) -> None:
        """레시피 상세 다이얼로그를 초기화합니다.

        Args:
            parent: 부모 위젯
            recipe: 표시할 레시피 딕셔너리
        """
        super().__init__(parent, f"📖 {recipe['name']} 레시피", 460, 500)
        self.recipe = recipe
        self._build()

    def _build(self) -> None:
        """레시피 정보 UI를 구성합니다."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 요리 이름 헤더
        ctk.CTkLabel(
            self,
            text=f"🍽️  {self.recipe['name']}",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=25, pady=(20, 5))

        ctk.CTkLabel(
            self,
            text=f"{self.recipe['servings']}인분 기준",
            text_color="gray",
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, padx=25)

        # 스크롤 가능 본문
        scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        scroll.grid(row=2, column=0, padx=20, pady=15, sticky="nswe")
        scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 재료 목록
        ctk.CTkLabel(
            scroll, text="📋 재료",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", padx=5, pady=(10, 5))

        for ing in self.recipe["ingredients"]:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(
                row, text=f"• {ing['name']}",
                font=ctk.CTkFont(size=13), anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=f"{ing['amount']} {ing['unit']}",
                font=ctk.CTkFont(size=13),
                text_color="#1F6AA5",
                anchor="e",
            ).pack(side="right")

        # 구분선
        ctk.CTkFrame(scroll, height=1, fg_color=("gray80", "gray40")).pack(
            fill="x", padx=5, pady=12
        )

        # 조리법
        ctk.CTkLabel(
            scroll, text="👨‍🍳 조리법",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(fill="x", padx=5, pady=(0, 8))

        # 조리법을 단계별로 분리해 표시
        steps = self.recipe["instructions"].split(". ")
        for step in steps:
            step = step.strip()
            if step:
                ctk.CTkLabel(
                    scroll,
                    text=step + ("." if not step.endswith(".") else ""),
                    font=ctk.CTkFont(size=13),
                    wraplength=380,
                    justify="left",
                    anchor="w",
                ).pack(fill="x", padx=5, pady=3)

        # 닫기 버튼
        ctk.CTkButton(
            self, text="닫기", command=self.destroy,
        ).grid(row=3, column=0, padx=25, pady=(0, 20), sticky="ew")
