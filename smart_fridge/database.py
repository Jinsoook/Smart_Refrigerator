"""
스마트 냉장고 관리 시스템 - 데이터베이스 모듈
모든 정적 데이터를 순수 Python 자료구조(딕셔너리·리스트)로 정의합니다.
JSON·pickle 등 직렬화 일체 사용 금지.
"""

# ───────────────────────────────────────────────
# 식재료별 표준 유통기한(일)과 카테고리 (20종)
# ───────────────────────────────────────────────
EXPIRY_DB: dict = {
    "우유":     {"days": 7,   "category": "유제품"},
    "달걀":     {"days": 21,  "category": "유제품"},
    "두부":     {"days": 5,   "category": "가공식품"},
    "돼지고기": {"days": 3,   "category": "육류"},
    "닭고기":   {"days": 3,   "category": "육류"},
    "소고기":   {"days": 3,   "category": "육류"},
    "양파":     {"days": 30,  "category": "채소"},
    "대파":     {"days": 10,  "category": "채소"},
    "감자":     {"days": 30,  "category": "채소"},
    "당근":     {"days": 21,  "category": "채소"},
    "시금치":   {"days": 5,   "category": "채소"},
    "고추":     {"days": 14,  "category": "채소"},
    "마늘":     {"days": 30,  "category": "채소"},
    "콩나물":   {"days": 4,   "category": "채소"},
    "김치":     {"days": 60,  "category": "가공식품"},
    "치즈":     {"days": 14,  "category": "유제품"},
    "버터":     {"days": 30,  "category": "유제품"},
    "쌀":       {"days": 365, "category": "곡물"},
    "미역":     {"days": 180, "category": "가공식품"},
    "떡":       {"days": 3,   "category": "가공식품"},
}

# ───────────────────────────────────────────────
# 100g 기준 영양 정보 (kcal, protein·g, carb·g, fat·g)
# ───────────────────────────────────────────────
NUTRITION_DB: dict = {
    "우유":     {"kcal": 61,  "protein": 3.2,  "carb": 4.8,  "fat": 3.3},
    "달걀":     {"kcal": 155, "protein": 13.0, "carb": 1.1,  "fat": 11.0},
    "두부":     {"kcal": 76,  "protein": 8.1,  "carb": 1.9,  "fat": 4.2},
    "돼지고기": {"kcal": 242, "protein": 17.1, "carb": 0.0,  "fat": 19.0},
    "닭고기":   {"kcal": 165, "protein": 31.0, "carb": 0.0,  "fat": 3.6},
    "소고기":   {"kcal": 250, "protein": 26.0, "carb": 0.0,  "fat": 15.0},
    "양파":     {"kcal": 40,  "protein": 1.1,  "carb": 9.3,  "fat": 0.1},
    "대파":     {"kcal": 32,  "protein": 1.9,  "carb": 6.5,  "fat": 0.3},
    "감자":     {"kcal": 77,  "protein": 2.0,  "carb": 17.0, "fat": 0.1},
    "당근":     {"kcal": 41,  "protein": 0.9,  "carb": 9.6,  "fat": 0.2},
    "시금치":   {"kcal": 23,  "protein": 2.9,  "carb": 3.6,  "fat": 0.4},
    "고추":     {"kcal": 40,  "protein": 2.0,  "carb": 8.8,  "fat": 0.4},
    "마늘":     {"kcal": 149, "protein": 6.4,  "carb": 33.0, "fat": 0.5},
    "콩나물":   {"kcal": 30,  "protein": 3.2,  "carb": 3.0,  "fat": 0.7},
    "김치":     {"kcal": 33,  "protein": 2.0,  "carb": 5.4,  "fat": 0.5},
    "치즈":     {"kcal": 403, "protein": 25.0, "carb": 1.3,  "fat": 33.0},
    "버터":     {"kcal": 717, "protein": 0.9,  "carb": 0.1,  "fat": 81.0},
    "쌀":       {"kcal": 360, "protein": 6.5,  "carb": 79.0, "fat": 0.9},
    "미역":     {"kcal": 45,  "protein": 1.8,  "carb": 9.1,  "fat": 0.6},
    "떡":       {"kcal": 230, "protein": 4.0,  "carb": 52.0, "fat": 0.5},
}

# ───────────────────────────────────────────────
# 한국 가정식 레시피 (11개)
# ───────────────────────────────────────────────
RECIPE_DB: list = [
    {
        "name": "김치찌개",
        "ingredients": [
            {"name": "김치",     "amount": 200, "unit": "g"},
            {"name": "돼지고기", "amount": 150, "unit": "g"},
            {"name": "두부",     "amount": 100, "unit": "g"},
            {"name": "대파",     "amount": 50,  "unit": "g"},
        ],
        "servings": 2,
        "instructions": (
            "1) 돼지고기와 김치를 팬에 볶아 풍미를 낸다. "
            "2) 물 500ml를 붓고 센 불로 끓인다. "
            "3) 두부와 대파를 넣고 5분 더 끓인 뒤 간을 맞춘다."
        ),
    },
    {
        "name": "계란말이",
        "ingredients": [
            {"name": "달걀", "amount": 150, "unit": "g"},
            {"name": "대파", "amount": 30,  "unit": "g"},
            {"name": "당근", "amount": 30,  "unit": "g"},
        ],
        "servings": 1,
        "instructions": (
            "1) 달걀을 풀고 잘게 썬 대파·당근을 넣어 섞는다. "
            "2) 팬에 기름을 두르고 약불에서 천천히 말아 가며 익힌다. "
            "3) 먹기 좋은 크기로 썬다."
        ),
    },
    {
        "name": "된장찌개",
        "ingredients": [
            {"name": "두부",   "amount": 150, "unit": "g"},
            {"name": "감자",   "amount": 100, "unit": "g"},
            {"name": "양파",   "amount": 80,  "unit": "g"},
            {"name": "대파",   "amount": 40,  "unit": "g"},
            {"name": "마늘",   "amount": 10,  "unit": "g"},
        ],
        "servings": 2,
        "instructions": (
            "1) 된장 2큰술을 물 500ml에 풀어 끓인다. "
            "2) 감자, 두부, 양파를 넣고 10분 끓인다. "
            "3) 대파와 마늘을 넣고 한 번 더 끓여 마무리한다."
        ),
    },
    {
        "name": "제육볶음",
        "ingredients": [
            {"name": "돼지고기", "amount": 300, "unit": "g"},
            {"name": "양파",     "amount": 100, "unit": "g"},
            {"name": "대파",     "amount": 50,  "unit": "g"},
            {"name": "고추",     "amount": 30,  "unit": "g"},
            {"name": "마늘",     "amount": 15,  "unit": "g"},
        ],
        "servings": 2,
        "instructions": (
            "1) 고추장·간장·설탕으로 양념을 만든다. "
            "2) 돼지고기를 양념에 30분 재운다. "
            "3) 팬에 양파·고추를 먼저 볶다가 고기를 넣고 강불에 볶는다."
        ),
    },
    {
        "name": "닭볶음탕",
        "ingredients": [
            {"name": "닭고기", "amount": 500, "unit": "g"},
            {"name": "감자",   "amount": 200, "unit": "g"},
            {"name": "당근",   "amount": 100, "unit": "g"},
            {"name": "양파",   "amount": 100, "unit": "g"},
            {"name": "대파",   "amount": 50,  "unit": "g"},
            {"name": "마늘",   "amount": 15,  "unit": "g"},
        ],
        "servings": 3,
        "instructions": (
            "1) 닭을 끓는 물에 한 번 데쳐 잡냄새를 제거한다. "
            "2) 고추장·고춧가루·간장 양념을 만든다. "
            "3) 닭과 채소를 양념과 함께 넣고 물 300ml를 부어 30분 조린다."
        ),
    },
    {
        "name": "콩나물국",
        "ingredients": [
            {"name": "콩나물", "amount": 200, "unit": "g"},
            {"name": "대파",   "amount": 40,  "unit": "g"},
            {"name": "마늘",   "amount": 5,   "unit": "g"},
        ],
        "servings": 2,
        "instructions": (
            "1) 물 600ml를 센 불로 끓인다. "
            "2) 콩나물을 넣고 뚜껑을 닫아 5분 끓인다 (비린내 방지). "
            "3) 마늘·대파를 넣고 국간장으로 간을 맞춘다."
        ),
    },
    {
        "name": "김치볶음밥",
        "ingredients": [
            {"name": "김치", "amount": 150, "unit": "g"},
            {"name": "쌀",   "amount": 200, "unit": "g"},
            {"name": "달걀", "amount": 60,  "unit": "g"},
            {"name": "대파", "amount": 30,  "unit": "g"},
        ],
        "servings": 1,
        "instructions": (
            "1) 쌀로 밥을 미리 짓는다. "
            "2) 팬에 김치를 볶다가 밥을 넣고 강불에 함께 볶는다. "
            "3) 계란 프라이를 만들어 위에 올린다."
        ),
    },
    {
        "name": "부대찌개",
        "ingredients": [
            {"name": "김치",   "amount": 150, "unit": "g"},
            {"name": "두부",   "amount": 100, "unit": "g"},
            {"name": "대파",   "amount": 40,  "unit": "g"},
            {"name": "양파",   "amount": 80,  "unit": "g"},
            {"name": "마늘",   "amount": 10,  "unit": "g"},
        ],
        "servings": 2,
        "instructions": (
            "1) 멸치 육수 600ml를 준비한다. "
            "2) 김치, 두부, 양파를 냄비에 담고 육수를 붓는다. "
            "3) 끓으면 대파·마늘을 넣고 고추장으로 간을 맞춘다."
        ),
    },
    {
        "name": "미역국",
        "ingredients": [
            {"name": "미역",   "amount": 30,  "unit": "g"},
            {"name": "소고기", "amount": 100, "unit": "g"},
            {"name": "마늘",   "amount": 5,   "unit": "g"},
        ],
        "servings": 2,
        "instructions": (
            "1) 미역을 찬물에 20분 불린 뒤 먹기 좋게 썬다. "
            "2) 소고기와 마늘을 참기름에 볶는다. "
            "3) 물 700ml를 붓고 미역을 넣어 20분 끓인 뒤 국간장으로 간한다."
        ),
    },
    {
        "name": "떡국",
        "ingredients": [
            {"name": "떡",   "amount": 300, "unit": "g"},
            {"name": "달걀", "amount": 60,  "unit": "g"},
            {"name": "대파", "amount": 30,  "unit": "g"},
            {"name": "마늘", "amount": 5,   "unit": "g"},
        ],
        "servings": 2,
        "instructions": (
            "1) 사골 육수 800ml를 준비해 끓인다. "
            "2) 떡을 넣고 떠오를 때까지 익힌다. "
            "3) 달걀 지단과 대파를 고명으로 올려 완성한다."
        ),
    },
    {
        "name": "시금치나물",
        "ingredients": [
            {"name": "시금치", "amount": 200, "unit": "g"},
            {"name": "마늘",   "amount": 5,   "unit": "g"},
        ],
        "servings": 2,
        "instructions": (
            "1) 시금치를 끓는 물에 30초 데쳐 찬물에 헹군다. "
            "2) 물기를 꼭 짜고 간장·마늘·참기름으로 무친다."
        ),
    },
]

# 쿠팡 검색 URL 템플릿 (식재료명을 {}에 삽입)
COUPANG_SEARCH: str = "https://www.coupang.com/np/search?q={}"


def get_sample_fridge() -> list:
    """초기 샘플 냉장고 상태를 반환합니다.

    모든 기능을 즉시 테스트할 수 있도록
    만료 재료·임박 재료·정상 재료·재고 부족 재료가 고루 섞여 있습니다.

    Returns:
        list: (name, qty, unit, days_ago) 튜플 리스트.
              days_ago = 오늘 기준 며칠 전에 구매했는지.
    """
    return [
        # 이미 만료된 재료 (days_ago > 표준 유통기한)
        ("우유",     1,   "L",  8),    # 표준 7일  → -1일 (만료)
        ("두부",     1,   "모", 6),    # 표준 5일  → -1일 (만료)
        # 유통기한 임박 재료 (남은 일수 0~3일)
        ("달걀",     6,   "개", 19),   # 표준 21일 → 2일 남음 (임박)
        ("돼지고기", 200, "g",  1),    # 표준 3일  → 2일 남음 (임박)
        ("대파",     2,   "대", 8),    # 표준 10일 → 2일 남음 (임박)
        # 정상 재료
        ("김치",     500, "g",  30),   # 표준 60일 → 30일 남음
        ("양파",     3,   "개", 15),   # 표준 30일 → 15일 남음
        ("감자",     4,   "개", 5),    # 표준 30일 → 25일 남음
        ("당근",     2,   "개", 3),    # 표준 21일 → 18일 남음
        ("쌀",       1,   "kg", 10),   # 표준 365일→ 355일 남음
        # 재고 부족 재료 (수량 1 이하)
        ("치즈",     1,   "장", 2),    # 표준 14일 → 12일 남음, 수량=1 (부족)
        ("마늘",     1,   "통", 5),    # 표준 30일 → 25일 남음, 수량=1 (부족)
    ]
