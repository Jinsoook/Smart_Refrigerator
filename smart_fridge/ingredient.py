"""
스마트 냉장고 관리 시스템 - 식재료 클래스 모듈
"""

from __future__ import annotations

import datetime
from database import EXPIRY_DB, NUTRITION_DB

# 카테고리 → 이모지 매핑
CATEGORY_EMOJI: dict[str, str] = {
    "유제품":   "🥛",
    "육류":     "🥩",
    "채소":     "🥬",
    "곡물":     "🍚",
    "가공식품": "📦",
}


class Ingredient:
    """냉장고 내 단일 식재료를 나타내는 클래스.

    Attributes:
        name (str): 식재료 이름
        quantity (float): 보유 수량
        unit (str): 수량 단위 (g, 개, L 등)
        purchase_date (datetime.date): 구매 날짜
        category (str): 카테고리 (EXPIRY_DB에서 자동 설정)
    """

    def __init__(
        self,
        name: str,
        quantity: float,
        unit: str,
        purchase_date: datetime.date | None = None,
    ) -> None:
        """식재료 인스턴스를 초기화합니다.

        Args:
            name: 식재료 이름 (EXPIRY_DB에 등록된 이름 권장)
            quantity: 보유 수량 (양수여야 함)
            unit: 수량 단위
            purchase_date: 구매 날짜. None이면 오늘로 자동 설정

        Raises:
            ValueError: quantity가 0 이하인 경우
        """
        if quantity <= 0:
            raise ValueError(f"수량은 양수여야 합니다. 입력값: {quantity}")

        self.name: str = name
        self.quantity: float = quantity
        self.unit: str = unit
        self.purchase_date: datetime.date = purchase_date or datetime.date.today()

        # EXPIRY_DB에 없는 식재료는 카테고리를 '기타'로 지정
        db_entry = EXPIRY_DB.get(name, {})
        self.category: str = db_entry.get("category", "기타")

    def days_left(self) -> int:
        """구매일과 표준 유통기한을 기준으로 남은 유통기한 일수를 계산합니다.

        Returns:
            int: 남은 일수. 음수이면 이미 만료된 상태.
                 EXPIRY_DB에 없는 식재료는 999(사실상 무한)를 반환.
        """
        db_entry = EXPIRY_DB.get(self.name)
        if db_entry is None:
            return 999  # DB 미등록 재료 → 유통기한 미적용

        # 만료 예정일 = 구매일 + 표준 유통기한
        expiry_date = self.purchase_date + datetime.timedelta(days=db_entry["days"])
        remaining = (expiry_date - datetime.date.today()).days
        return remaining

    def is_expiring(self, threshold: int = 3) -> bool:
        """유통기한이 임박했는지 여부를 반환합니다.

        만료(음수)된 재료는 False를 반환합니다.
        만료 여부는 get_expired()에서 별도 처리합니다.

        Args:
            threshold: 임박 기준 일수 (기본값 3일)

        Returns:
            bool: 남은 일수가 0 이상 threshold 이하이면 True
        """
        left = self.days_left()
        return 0 <= left <= threshold

    def get_nutrition(self) -> dict:
        """100g 기준 영양 정보를 반환합니다.

        Returns:
            dict: {"kcal": ..., "protein": ..., "carb": ..., "fat": ...}.
                  NUTRITION_DB에 없으면 빈 dict 반환.
        """
        return NUTRITION_DB.get(self.name, {})

    def __str__(self) -> str:
        """카테고리 이모지, 이름, 수량, 남은 유통기한을 포함한 문자열을 반환합니다.

        Returns:
            str: 예) "🥛 우유 - 1 L (⚠️ 2일 남음 (임박))"
        """
        emoji = CATEGORY_EMOJI.get(self.category, "🍽️")
        left = self.days_left()

        if left == 999:
            expire_str = "✅ 유통기한 정보 없음"
        elif left < 0:
            expire_str = f"🚨 {abs(left)}일 초과 (만료)"
        elif left == 0:
            expire_str = "🚨 오늘 만료"
        elif left <= 3:
            expire_str = f"⚠️ {left}일 남음 (임박)"
        else:
            expire_str = f"✅ {left}일 남음"

        return f"{emoji} {self.name} - {self.quantity} {self.unit} ({expire_str})"
