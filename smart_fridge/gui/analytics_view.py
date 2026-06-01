"""
스마트 냉장고 관리 시스템 v2.0 — 통계 뷰

폐기율 카드, 사용 빈도 막대 그래프, 카테고리 파이 차트를 표시합니다.
matplotlib.backends.backend_tkagg.FigureCanvasTkAgg로 차트를 임베드합니다.
"""

from __future__ import annotations
import matplotlib
import matplotlib.font_manager as fm
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fridge import Fridge
from analytics import waste_rate, top_used, category_distribution


# 한글 폰트 설정
_KO_FONTS = [
    "Noto Sans CJK KR", "Noto Sans CJK JP", "NanumGothic", "NanumBarunGothic",
    "AppleGothic", "Malgun Gothic", "DejaVu Sans",
]
for _f in _KO_FONTS:
    if any(fe.name == _f for fe in fm.fontManager.ttflist):
        matplotlib.rc("font", family=_f)
        break
matplotlib.rc("axes", unicode_minus=False)


class AnalyticsView(ctk.CTkFrame):
    """통계 뷰.

    Attributes:
        fridge (Fridge): 공유 냉장고 인스턴스
    """

    def __init__(self, parent: ctk.CTkFrame, fridge: Fridge) -> None:
        """통계 뷰를 초기화합니다.

        Args:
            parent: 부모 위젯
            fridge: 공유 냉장고 인스턴스
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.fridge = fridge
        self._canvas: FigureCanvasTkAgg | None = None
        self._fig:    Figure | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_summary_row()
        self._build_chart_frame()

    # ── UI 뼈대 ──────────────────────────────────────────────

    def _build_header(self) -> None:
        """상단 제목 + 새로고침 버튼."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        ctk.CTkLabel(
            header, text="📊 통계",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            header, text="🔄 새로고침", width=100, command=self.refresh
        ).pack(side="right", padx=5)

    def _build_summary_row(self) -> None:
        """폐기율·이벤트 수 등 요약 카드 행을 배치합니다."""
        self._summary_row = ctk.CTkFrame(self, fg_color="transparent")
        self._summary_row.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        for i in range(3):
            self._summary_row.grid_columnconfigure(i, weight=1)

    def _build_chart_frame(self) -> None:
        """matplotlib 차트가 들어갈 컨테이너 프레임."""
        self._chart_frame = ctk.CTkFrame(self, corner_radius=10)
        self._chart_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nswe")
        self._chart_frame.grid_columnconfigure(0, weight=1)
        self._chart_frame.grid_rowconfigure(0, weight=1)

    # ── 새로고침 ─────────────────────────────────────────────

    def refresh(self) -> None:
        """통계를 다시 계산하고 차트를 갱신합니다."""
        self._refresh_summary()
        self._refresh_charts()

    # ── 요약 카드 ────────────────────────────────────────────

    def _refresh_summary(self) -> None:
        """폐기율·사용 횟수·보유 종 수 요약 카드를 갱신합니다."""
        for w in self._summary_row.winfo_children():
            w.destroy()

        history = self.fridge.history
        rate      = waste_rate(history)
        used_cnt  = sum(1 for e in history if e["action"] == "used")
        disc_cnt  = sum(1 for e in history if e["action"] == "discarded")
        total_cnt = len(self.fridge.items)

        # 폐기율 색상
        if rate == 0:
            rate_color = "#4CAF50"
        elif rate < 0.3:
            rate_color = "#FFA500"
        else:
            rate_color = "#FF4444"

        cards = [
            ("🗑️", "폐기율",      f"{rate*100:.1f}%", rate_color),
            ("📋", "사용 / 폐기",  f"{used_cnt} / {disc_cnt}회", None),
            ("📦", "현재 보유",    f"{total_cnt}종",  "#4CAF50"),
        ]
        for col, (emoji, title, val, color) in enumerate(cards):
            self._make_summary_card(col, emoji, title, val, color)

    def _make_summary_card(
        self, col: int, emoji: str, title: str, val: str, color: str | None
    ) -> None:
        """단일 요약 카드를 생성합니다.

        Args:
            col: 그리드 열 번호
            emoji: 카드 이모지
            title: 제목
            val: 표시 수치
            color: 강조 색 (None이면 기본)
        """
        fg = color if color else ("gray90", "gray20")
        card = ctk.CTkFrame(self._summary_row, corner_radius=12, fg_color=fg)
        card.grid(row=0, column=col, padx=6, pady=5, sticky="ew", ipady=8)

        tc  = "white" if color else ("gray10", "gray90")
        sub = "white" if color else ("gray50", "gray60")
        ctk.CTkLabel(card, text=emoji, font=ctk.CTkFont(size=24)).pack(pady=(15, 2))
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color=sub).pack()
        ctk.CTkLabel(
            card, text=val, font=ctk.CTkFont(size=22, weight="bold"), text_color=tc
        ).pack(pady=(2, 15))

    # ── matplotlib 차트 ──────────────────────────────────────

    def _refresh_charts(self) -> None:
        """사용 빈도 막대 + 카테고리 파이 차트를 갱신합니다."""
        # 기존 캔버스 제거 및 figure 닫기
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        if self._fig is not None:
            import matplotlib.pyplot as plt
            plt.close(self._fig)
            self._fig = None

        history = self.fridge.history
        top     = top_used(history, n=5)
        dist    = category_distribution(self.fridge)

        # 차트 색상 (라이트 모드 기준)
        bg      = "#FFFFFF"
        fg_text = "#111111"

        self._fig = Figure(figsize=(10, 3.8), dpi=90, facecolor=bg)
        self._fig.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.18,
                                  wspace=0.35)

        # ── 막대 그래프: 사용 빈도 Top 5 ──────────────────
        ax1 = self._fig.add_subplot(1, 2, 1)
        ax1.set_facecolor(bg)
        ax1.set_title("사용 빈도 Top 5", color=fg_text, fontsize=12, pad=8)

        if top:
            names   = [n for n, _ in top]
            counts  = [c for _, c in top]
            bars    = ax1.bar(names, counts,
                              color=["#1F6AA5", "#3A8FD4", "#5AB4F5",
                                     "#7CC8FF", "#9FDAFF"][:len(names)])
            ax1.set_ylabel("사용 횟수", color=fg_text, fontsize=10)
            for bar, cnt in zip(bars, counts):
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    str(cnt), ha="center", va="bottom",
                    color=fg_text, fontsize=10,
                )
        else:
            ax1.text(0.5, 0.5, "사용 이력 없음",
                     ha="center", va="center", transform=ax1.transAxes,
                     color=fg_text, fontsize=12)

        ax1.tick_params(colors=fg_text)
        for spine in ax1.spines.values():
            spine.set_edgecolor(fg_text)
        ax1.yaxis.label.set_color(fg_text)
        ax1.xaxis.label.set_color(fg_text)

        # ── 파이 차트: 카테고리별 비중 ──────────────────────
        ax2 = self._fig.add_subplot(1, 2, 2)
        ax2.set_facecolor(bg)
        ax2.set_title("카테고리별 비중", color=fg_text, fontsize=12, pad=8)

        if dist:
            labels = list(dist.keys())
            sizes  = list(dist.values())
            palette = ["#1F6AA5", "#4CAF50", "#FFA500", "#FF4444",
                       "#9C27B0", "#00BCD4", "#FF9800"][:len(sizes)]
            wedges, texts, autotexts = ax2.pie(
                sizes, labels=labels, autopct="%1.0f%%",
                colors=palette, startangle=90,
                textprops={"color": fg_text, "fontsize": 9},
            )
            for at in autotexts:
                at.set_fontsize(9)
        else:
            ax2.text(0.5, 0.5, "재료 없음",
                     ha="center", va="center", transform=ax2.transAxes,
                     color=fg_text, fontsize=12)

        # 캔버스 임베드
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._chart_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(
            row=0, column=0, sticky="nswe", padx=5, pady=5
        )
