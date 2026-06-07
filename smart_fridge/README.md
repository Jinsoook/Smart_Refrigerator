# 🧊 스마트 냉장고 관리 시스템 v2.0

냉장고 식재료 관리, 유통기한 알림, 레시피 추천, 소비 통계, 장보기 목록 자동 생성을 통합한 데스크톱 GUI 애플리케이션입니다.

---

## 화면 구성

| 화면 | 설명 |
|------|------|
| 🏠 대시보드 | 전체 통계 카드, 임박 재료 목록, 오늘의 추천 요리 |
| 📦 재고관리 | 식재료 추가·사용·폐기, 카테고리·검색 필터, 표 정렬 |
| 🍳 요리추천 | 보유 재료 기반 상위 3개 레시피 카드 + 상세 조리법 |
| 📊 통계 | 폐기율, 자주 쓴 재료 막대 차트, 카테고리 파이 차트 |
| 🛒 장보기 | 재고 부족·자주 쓰는 재료 목록, 쿠팡 바로구매 링크 |

---

## 실행 방법

### 1. 의존성 설치

```bash
pip install customtkinter matplotlib
```

> 시스템 패키지 충돌 시 `--break-system-packages` 플래그 추가

### 2. 앱 실행

```bash
cd smart_fridge
python3 main.py
```

---

## 프로젝트 구조

```
smart_fridge/
├── main.py              # GUI 진입점 (CTk 테마 설정 후 앱 실행)
├── database.py          # 모든 정적 데이터 (유통기한 DB, 영양 DB, 레시피 DB)
├── ingredient.py        # Ingredient 클래스 (유통기한 계산, 영양 정보)
├── fridge.py            # Fridge 클래스 (재료 추가·사용·폐기·검색)
├── recommender.py       # RecipeRecommender (점수 기반 레시피 추천)
├── analytics.py         # 통계 함수 (폐기율, 빈도, 장보기 목록)
└── gui/
    ├── app.py           # 메인 윈도우 + 사이드바 네비게이션
    ├── dashboard_view.py
    ├── inventory_view.py
    ├── recipe_view.py
    ├── analytics_view.py
    ├── shopping_view.py
    └── dialogs.py       # 재료 추가·사용·레시피 상세 다이얼로그
```

### 레이어 분리 원칙

비즈니스 로직 파일(`database.py`, `ingredient.py`, `fridge.py`, `recommender.py`, `analytics.py`)은 GUI에 의존하지 않습니다. `gui/` 폴더의 뷰 파일들이 이 모듈을 단방향으로 참조하는 구조입니다.

---

## 데이터 구조

모든 데이터는 JSON/pickle 없이 순수 Python 자료구조로 관리됩니다. 앱을 재실행하면 샘플 데이터로 초기화됩니다.

**EXPIRY_DB** — 식재료별 표준 유통기한(일)과 카테고리 (20종)

```python
"우유": {"days": 7, "category": "유제품"}
```

**NUTRITION_DB** — 100g 기준 영양 정보 (kcal, 단백질, 탄수화물, 지방)

**RECIPE_DB** — 한국 가정식 레시피 11종

> 김치찌개, 계란말이, 된장찌개, 제육볶음, 닭볶음탕, 콩나물국, 김치볶음밥, 부대찌개, 미역국, 떡국, 시금치나물

---

## 핵심 로직

### 유통기한 계산

```
남은 일수 = (구매일 + 표준 유통기한) - 오늘
```

- 음수: 만료 🚨
- 0~3일: 임박 ⚠️
- 4일 이상: 양호 ✅
- DB 미등록 재료: 999일 (무한)

### 레시피 추천 점수 공식

```
score = 0.5 × match_ratio + 0.4 × urgency - 0.1 × missing_penalty

match_ratio     = 보유 재료 수 / 레시피 재료 총 수
urgency         = Σ max(0, 1 - days_left_i / 7) / 레시피 재료 총 수
missing_penalty = 부족 재료 수 / 레시피 재료 총 수
```

유통기한이 임박한 재료를 먼저 사용하도록 urgency 가중치(0.4)가 높게 설정되어 있습니다.

### 장보기 목록 선정 기준

1. 재고가 1 이하인 재료 (재고 부족)
2. 소비 빈도 상위 5개 중 현재 재고가 없거나 부족한 재료

---

## 초기 샘플 데이터

앱 실행 시 아래 12개 재료로 시작되어 모든 기능을 즉시 확인할 수 있습니다.

| 재료 | 상태 |
|------|------|
| 우유, 두부 | 만료 🚨 |
| 달걀, 돼지고기, 대파 | 임박 ⚠️ |
| 김치, 양파, 감자, 당근, 쌀 | 정상 ✅ |
| 치즈, 마늘 | 재고 부족 (수량 1) |

---

## 기술 스택

| 구분 | 내용 |
|------|------|
| 언어 | Python 3.10+ |
| GUI 프레임워크 | CustomTkinter 5.x |
| 차트 | Matplotlib (FigureCanvasTkAgg 임베딩) |
| 테이블 | tkinter ttk.Treeview |
| 데이터 저장 | 런타임 메모리 (순수 Python dict/list) |
| 영속성 | 없음 (매 실행 시 샘플 데이터로 초기화) |
