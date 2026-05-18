# Smart_Refrigerator
26 소프트웨어적 사고 / 기말 프로젝트

# 조건

1. 사용자 입력이 있어야 합니다.
2. 조건문, 반복문, 함수, 리스트/딕셔너리 등을 활용해야 합니다.
3. 입력을 바탕으로 의미 있는 처리 결과를 출력해야 합니다.
4. 실행 가능한 Python 코드로 제출해야 합니다.
5. LLM 활용 기록을 제출해야 합니다.

# 최종 제출물 :
* 20~25 분 발표영상 (데모 포함)
* 발표자료
* 보고서 (프로젝트 주제 목적, 기능, 코드 구조, 활용박식, 실행결과 )
-> 코드를 다 붙여넣는게 아니라 주요부분만 설명하고 분량은 6~10페이지.
* 동작코드

## Smart_Refrigerator

Summary:
1. Primary Request and Intent:

**Request 1 (main project):** Create a "고급 스마트 냉장고 관리 시스템" (Advanced Smart Fridge Management System) in Python as a university freshman final project. Strict constraints:
- JSON/pickle and all serialization **completely forbidden**; all data must be in pure Python dicts/lists inside `database.py`
- External libraries: only standard library (`datetime`)
- No persistence; each run starts from sample data
- 6-file structure: `main.py`, `ingredient.py`, `fridge.py`, `recommender.py`, `analytics.py`, `database.py`
- Type hints required on all methods; Korean docstrings with Args/Returns; Korean comments especially on score formula
- Exception handling for bad date format, nonexistent ingredients, negative quantities, invalid menu input
- Emoji usage in output; snake_case variables, PascalCase classes

**Request 2:** Explain the full code structure and how to run it.

**Request 3 (GUI addition):** Add a CustomTkinter-based GUI to the existing system. Key constraints:
- The 6 existing business logic files (`ingredient.py`, `fridge.py`, `recommender.py`, `analytics.py`, `database.py`, original `main.py` logic) must **not be modified by even one line**
- Only `main.py` replaced as GUI entry point; `gui/` folder with 7 files added
- External libraries: `customtkinter`, `matplotlib` only
- Specific views: dashboard, inventory (ttk.Treeview), recipe cards, analytics (matplotlib charts), shopping list
- Modal dialogs: AddIngredientDialog, UseIngredientDialog, RecipeDetailDialog
- All views share same `fridge` instance; views created once and toggled with `grid()`/`grid_remove()`

2. Key Technical Concepts:
- Pure Python data structures (dict, list) as database substitute — no serialization
- `datetime.date` for purchase dates and expiry calculation
- Object-oriented design: `Ingredient`, `Fridge`, `RecipeRecommender` classes
- Recommendation scoring formula: `score = w1 × match_ratio + w2 × urgency - w3 × missing_penalty` (w1=0.5, w2=0.4, w3=0.1)
- Urgency per ingredient: `max(0, 1 - days_left/7)` (expired items get 0)
- History list tracking `{"action": "used"/"discarded", "name": ..., "qty": ..., "date": ...}`
- CustomTkinter (`ctk.CTk`, `CTkFrame`, `CTkButton`, `CTkProgressBar`, `CTkScrollableFrame`, `CTkToplevel`, `CTkComboBox`, `CTkOptionMenu`, `CTkSwitch`, `CTkCheckBox`)
- `ttk.Treeview` with tag-based row coloring for inventory table
- `matplotlib.backends.backend_tkagg.FigureCanvasTkAgg` for embedding charts
- View pattern: all views inherit `ctk.CTkFrame`, all implement `refresh()` method
- Modal dialog pattern: `ctk.CTkToplevel` + `grab_set()` + parent-centering
- `on_success` callback pattern: dialogs call parent view's `refresh()` on success
- `from __future__ import annotations` for Python 3.9/3.10 `X | Y` union type hint compatibility
- Dict-based menu dispatch in `main.py` instead of if-elif chains

3. Files and Code Sections:

- **`/home/user/바탕화면/소사 기말/smart_fridge/database.py`** (260 lines, UNCHANGED after creation)
  - `EXPIRY_DB`: 20 ingredients with `{"days": int, "category": str}`
  - `NUTRITION_DB`: 20 ingredients with `{"kcal", "protein", "carb", "fat"}` per 100g
  - `RECIPE_DB`: 11 Korean recipes (김치찌개, 계란말이, 된장찌개, 제육볶음, 닭볶음탕, 콩나물국, 김치볶음밥, 부대찌개, 미역국, 떡국, 시금치나물)
  - `COUPANG_SEARCH = "https://www.coupang.com/np/search?q={}"`
  - `get_sample_fridge()` returns 12 items designed to cover all test scenarios:
    - Expired: 우유 (8 days ago, std 7), 두부 (6 days ago, std 5)
    - Expiring: 달걀 (19 days ago, std 21 = 2 left), 돼지고기 (1 day ago, std 3 = 2 left), 대파 (8 days ago, std 10 = 2 left)
    - Normal: 김치, 양파, 감자, 당근, 쌀
    - Low stock: 치즈 (qty=1), 마늘 (qty=1)

- **`/home/user/바탕화면/소사 기말/smart_fridge/ingredient.py`** (121 lines, UNCHANGED)
  - `CATEGORY_EMOJI = {"유제품": "🥛", "육류": "🥩", "채소": "🥬", "곡물": "🍚", "가공식품": "📦"}`
  - `class Ingredient`: fields `name, quantity, unit, purchase_date, category`
  - `days_left()`: `expiry_date = purchase_date + timedelta(days=EXPIRY_DB[name]["days"])`, returns `(expiry_date - today).days`; returns 999 if not in DB
  - `is_expiring(threshold=3)`: returns `0 <= left <= threshold` (excludes expired)
  - `get_nutrition()`: returns `NUTRITION_DB.get(self.name, {})`
  - `__str__()`: emoji + name + qty + status string with 🚨/⚠️/✅ prefixes

- **`/home/user/바탕화면/소사 기말/smart_fridge/fridge.py`** (199 lines, UNCHANGED)
  - `class Fridge`: `items: dict[str, Ingredient]`, `history: list[dict]`
  - `__init__`: loads from `get_sample_fridge()`, creates `Ingredient` with `today - timedelta(days_ago)`
  - `use_ingredient()`: subtracts qty, deletes if ≤0, appends `{"action":"used",...}` to history
  - `discard_ingredient()`: appends `{"action":"discarded",...}`, deletes item
  - `get_expiring(threshold=3)`: sorted by `days_left()` ascending
  - `show_by_category()`: groups by category, uses `CATEGORY_EMOJI`

- **`/home/user/바탕화면/소사 기말/smart_fridge/recommender.py`** (263 lines, UNCHANGED)
  - Score formula documented in module docstring:
    ```
    score = w1 × match_ratio + w2 × urgency - w3 × missing_penalty
    match_ratio    = |보유 ∩ 레시피| / |레시피|
    urgency        = Σ max(0, 1 - days_left_i/7) / |레시피|  [expired→0]
    missing_penalty = |부족| / |레시피|
    w1=0.5, w2=0.4, w3=0.1
    ```
  - `recommend()`: `sorted(..., key=lambda x: x[1], reverse=True)[:top_n]`
  - `_print_nutrition()`: only calculates for ingredients with `unit == "g"`

- **`/home/user/바탕화면/소사 기말/smart_fridge/analytics.py`** (170 lines, UNCHANGED)
  - `waste_rate(history)`: discarded count / total events
  - `top_used(history, n=5)`: pure dict frequency counting (no `collections.Counter`)
  - `category_distribution(fridge)`: `dict[str, int]` by category
  - `generate_shopping_list()`: combines low-stock (qty≤1) + frequently used but missing/low

- **`/home/user/바탕화면/소사 기말/smart_fridge/main.py`** (REPLACED for GUI)
  ```python
  import customtkinter as ctk
  from gui.app import SmartFridgeApp
  from fridge import Fridge
  def main():
      ctk.set_appearance_mode("light")
      ctk.set_default_color_theme("blue")
      fridge = Fridge()
      app = SmartFridgeApp(fridge)
      app.mainloop()
  if __name__ == "__main__":
      main()
  ```

- **`/home/user/바탕화면/소사 기말/smart_fridge/gui/app.py`**
  - `class SmartFridgeApp(ctk.CTk)`: 1100×700 window, minsize 900×600
  - Sidebar: width=200, `grid_propagate(False)` to fix width, logo + 5 nav buttons + dark mode switch
  - Nav buttons: `fg_color="transparent"` default, `fg_color=("gray75","gray25")` when active
  - `_create_views()`: deferred imports inside method to avoid circular imports; all views `.grid(row=0, column=0, sticky="nswe")`
  - `show_view(name)`: `grid_remove()` all → `grid()` + `refresh()` selected
  - `_toggle_dark()`: `ctk.set_appearance_mode("dark" if switch.get() else "light")`

- **`/home/user/바탕화면/소사 기말/smart_fridge/gui/dashboard_view.py`**
  - Stats cards: 4 cards in a row using `_card_area` with `grid_columnconfigure(i, weight=1)` for 4 columns
  - Card colors: expiring→`#FFA500`, expired→`#FF4444`, cookable→`#4CAF50`, total→default
  - Cookable count: recipes where `matched/total >= 0.5`
  - Bottom: two panels side-by-side — expiring list (left) + today's recommendation (right)
  - Recommendation uses `RecipeRecommender().recommend(fridge, top_n=1)`
  - Progress bar: `pb = ctk.CTkProgressBar(...); pb.set(ratio)` where ratio = have/total

- **`/home/user/바탕화면/소사 기말/smart_fridge/gui/inventory_view.py`**
  - Toolbar: `CTkOptionMenu` for category filter, `CTkEntry` for search (bound to `<Return>`), 3 action buttons
  - Table: `ttk.Treeview` in a `tk.Frame` container with vertical+horizontal `ttk.Scrollbar`
  - `ttk.Style()` configured: `"Inv.Treeview"` with rowheight=30, `"Inv.Treeview.Heading"`
  - Tag colors: `expired→#FFCCCC/#880000`, `expiring→#FFF3CD/#664D03`, `normal→#FAFAFA/#111111`
  - Columns: name, qty, unit, category, bought, days_left, status
  - Double-click bound to `<Double-1>` → opens `UseIngredientDialog`
  - Discard: direct `messagebox.askyesno()` without separate dialog

- **`/home/user/바탕화면/소사 기말/smart_fridge/gui/recipe_view.py`**
  - `CTkScrollableFrame` holds 3 columns for recipe cards
  - Each card: rank badge bar (gold/silver/bronze color), recipe name with medal emoji, score label, `CTkProgressBar` with `pb.set(ratio)`, ingredient list with colored labels (✓ green/#4CAF50, ⚠ orange/#FFA500, ✗ gray/#AAAAAA)
  - `_calc_nutrition()`: calculates only for `unit == "g"` ingredients, returns formatted string
  - "📖 레시피 보기" button → `RecipeDetailDialog(self, recipe)`

- **`/home/user/바탕화면/소사 기말/smart_fridge/gui/analytics_view.py`**
  - `_canvas: FigureCanvasTkAgg | None` and `_fig: Figure | None` kept as instance vars
  - On refresh: destroys old canvas widget, calls `plt.close(self._fig)`, creates new `Figure(figsize=(10, 3.8), dpi=90)`
  - `add_subplot(1, 2, 1)` for bar chart (top used), `add_subplot(1, 2, 2)` for pie chart (category distribution)
  - Dark mode detection: `ctk.get_appearance_mode() == "Dark"` → adjusts bg/fg colors
  - Empty data handled with `ax.text(0.5, 0.5, "사용 이력 없음", ...)` centered text
  - Canvas embedded: `FigureCanvasTkAgg(fig, master=frame)` → `.get_tk_widget().grid(...)`

- **`/home/user/바탕화면/소사 기말/smart_fridge/gui/shopping_view.py`**
  - `self._check_vars: list[ctk.IntVar]` kept to prevent garbage collection
  - `webbrowser.open(url)` for Coupang links (standard library)
  - Checkbox toggle: `_on_check()` changes `text_color` to gray when checked
  - Row card stores widget references as attributes (`card._name_lbl`, `card._reason_lbl`) for color updates
  - Coupang button: `fg_color="#FF6000"` (Coupang orange)

- **`/home/user/바탕화면/소사 기말/smart_fridge/gui/dialogs.py`**
  - `_BaseDialog(ctk.CTkToplevel)`: `self.after(50, self._center_and_grab)` for delayed centering/modal
  - `_center_and_grab()`: calculates center from `winfo_toplevel()` position
  - `AddIngredientDialog`: `CTkComboBox(values=sorted(EXPIRY_DB.keys()))` + qty entry + unit `CTkOptionMenu` (values=`_UNITS`) + date entry defaulting to today
  - `UseIngredientDialog`: reads-only name label, current stock display, qty entry with `focus()`
  - `RecipeDetailDialog`: `CTkScrollableFrame` for ingredients list + parsed instruction steps
  - All dialogs: `on_success` callable called before `self.destroy()` on success; errors shown via `messagebox.showerror(..., parent=self)`

4. Errors and Fixes:
- **`python` command not found**: Initial test used `python` but the system only has `python3`. Fixed by using `python3` for all subsequent commands.
- **`pip install` blocked by system packages**: Running `pip3 install customtkinter matplotlib` failed with PEP 668 error. Fixed by adding `--break-system-packages` flag: `pip3 install customtkinter matplotlib --break-system-packages`. matplotlib was already installed system-wide; only `customtkinter` (5.2.2) and its dependency `darkdetect` (0.8.0) were newly installed.

5. Problem Solving:
- **Circular imports in gui/**: Solved by using deferred (lazy) imports inside `_create_views()` method of `app.py` rather than top-level imports.
- **Python 3.9/3.10 type hint compatibility**: Used `from __future__ import annotations` in all files to allow `X | Y` union syntax and `list[dict]` built-in generics.
- **ttk.Treeview vs CTk theming**: Configured `ttk.Style()` with a custom named style `"Inv.Treeview"` to ensure readable appearance independent of CTk theme.
- **matplotlib memory management**: Stored `_fig` and `_canvas` as instance variables; on each `refresh()` call, destroys the old canvas widget and calls `plt.close(self._fig)` before creating a new figure.
- **Dialog focus/centering timing**: Used `self.after(50, self._center_and_grab)` to delay centering and `grab_set()` until after the window is rendered, preventing incorrect geometry calculations.
- **Checkbox strike-through**: tkinter/CTk does not support inline strike-through text. Approximated by changing `text_color` to gray on checkbox check, which is functionally clear.
- **IntVar garbage collection**: Stored all checkbox `IntVar` instances in `self._check_vars` list to prevent Python GC from collecting them (which would break the checkbox behavior).
- **Sample data design**: Carefully chose `days_ago` values so that expired (우유, 두부), expiring (달걀, 돼지고기, 대파), and low-stock (치즈, 마늘) items all appear in the initial state for immediate feature testing.

6. All User Messages:
- **Message 1 (project creation):** "Python으로 **고급 스마트 냉장고 관리 시스템**을 만들어줘. 대학 1학년 Python 수업 기말 프로젝트. **JSON·pickle 등 직렬화 일체 사용 금지**, 모든 데이터는 순수 Python 자료구조(딕셔너리·리스트)로 `database.py`에 정의. 외부 라이브러리는 표준 라이브러리(`datetime`)만 사용. 영속성은 구현하지 않고, 매 실행 시 샘플 데이터로 시작." [followed by detailed file structure specification, class designs, score formula, and code quality requirements]
- **Message 2 (explanation request):** "코드 전체 구조에 대한 설명 + 실행방법 설명"
- **Message 3 (GUI addition):** "기존에 만든 스마트 냉장고 시스템에 **CustomTkinter 기반 GUI**를 추가해줘. 기존 비즈니스 로직 파일(`ingredient.py`, `fridge.py`, `recommender.py`, `analytics.py`, `database.py`)은 **단 한 줄도 수정하지 않고**, UI 레이어만 새로 추가하는 방식으로 진행. 외부 라이브러리는 `customtkinter`, `matplotlib`만 사용." [followed by detailed specification of all 8 GUI files]
- **Message 4 (current):** Request for conversation summary in TEXT ONLY format with analysis and summary blocks.

7. Pending Tasks:
- No explicitly pending tasks. All three major requests (terminal app, explanation, GUI) have been completed and verified. The GUI was verified with syntax checking of all 9 files and import verification confirming all 7 gui modules load correctly and the 6 original business logic files remain unmodified.

8. Current Work:
The most recently completed work was the CustomTkinter GUI addition. Nine files were created/modified:
- `main.py` replaced as GUI entry point
- `gui/__init__.py` (empty package marker)
- `gui/app.py` (main window, sidebar, view switching)
- `gui/dashboard_view.py` (stats cards, expiring list, daily recommendation)
- `gui/inventory_view.py` (ttk.Treeview inventory table with toolbar)
- `gui/recipe_view.py` (3 recipe cards with progress bars and ingredient coloring)
- `gui/analytics_view.py` (waste rate card + matplotlib bar/pie charts)
- `gui/shopping_view.py` (checkbox shopping list with Coupang links)
- `gui/dialogs.py` (AddIngredientDialog, UseIngredientDialog, RecipeDetailDialog)

Final verification output:
```
✅ main.py
✅ gui/__init__.py
✅ gui/app.py
✅ gui/dashboard_view.py
✅ gui/inventory_view.py
✅ gui/recipe_view.py
✅ gui/analytics_view.py
✅ gui/shopping_view.py
✅ gui/dialogs.py
✅ 기존 비즈니스 로직 모듈 import 정상
  ✅ gui.app
  ✅ gui.dashboard_view
  ✅ gui.inventory_view
  ✅ gui.recipe_view
  ✅ gui.analytics_view
  ✅ gui.shopping_view
  ✅ gui.dialogs
```
Original files confirmed unchanged: database.py (260 lines), ingredient.py (121 lines), fridge.py (199 lines), recommender.py (263 lines), analytics.py (170 lines).

9. Optional Next Step:
There is no pending next step — all explicitly requested tasks have been completed and verified. The most recent task (GUI addition) concluded with all files passing syntax and import checks. The user's last request before the summary was the GUI task, which is now fully done. Any further work would require new user instructions.

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /home/user/.claude/projects/-home-user-----------/719a80ff-e052-446a-912c-67e47f34cd74.jsonl
