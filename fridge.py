"""
스마트 냉장고 관리 시스템 - 냉장고 클래스 모듈
"""

from __future__ import annotations

import datetime
from ingredient import Ingredient, CATEGORY_EMOJI
from database import get_sample_fridge


class Fridge:
    """스마트 냉장고를 나타내는 클래스.

    Attributes:
        items (dict[str, Ingredient]): 식재료명 → Ingredient 인스턴스 매핑
        history (list[dict]): 사용·폐기 이력 (action, name, qty, date)
    """

    def __init__(self) -> None:
        """샘플 데이터로 냉장고를 초기화합니다.

        database.get_sample_fridge()의 튜플 리스트를 읽어
        Ingredient 인스턴스를 생성하고 items에 저장합니다.
        """
        self.items: dict[str, Ingredient] = {}
        self.history: list[dict] = []

        for name, qty, unit, days_ago in get_sample_fridge():
            purchase_date = datetime.date.today() - datetime.timedelta(days=days_ago)
            try:
                self.items[name] = Ingredient(name, qty, unit, purchase_date)
            except ValueError as e:
                print(f"  ⚠️  샘플 데이터 로드 오류 ({name}): {e}")

    def add_ingredient(
        self,
        name: str,
        qty: float,
        unit: str,
        date: datetime.date | None = None,
    ) -> None:
        """식재료를 냉장고에 추가합니다.

        같은 이름의 식재료가 이미 있으면 수량을 합산하고
        구매일을 새 날짜로 갱신합니다.

        Args:
            name: 식재료 이름
            qty: 추가할 수량 (양수여야 함)
            unit: 수량 단위
            date: 구매 날짜. None이면 오늘

        Raises:
            ValueError: qty가 0 이하인 경우
        """
        if qty <= 0:
            raise ValueError(f"수량은 양수여야 합니다. 입력값: {qty}")

        purchase_date = date or datetime.date.today()

        if name in self.items:
            # 동일 재료가 있으면 수량 합산, 구매일은 최신으로 갱신
            self.items[name].quantity += qty
            self.items[name].purchase_date = purchase_date
        else:
            self.items[name] = Ingredient(name, qty, unit, purchase_date)

    def use_ingredient(self, name: str, qty: float) -> None:
        """식재료를 사용(차감)합니다.

        수량이 0이 되면 items에서 자동으로 삭제하고 이력에 'used'를 기록합니다.

        Args:
            name: 사용할 식재료 이름
            qty: 사용량 (양수여야 함)

        Raises:
            KeyError: 해당 식재료가 냉장고에 없는 경우
            ValueError: qty가 0 이하이거나 보유량보다 많은 경우
        """
        if name not in self.items:
            raise KeyError(f"'{name}'은(는) 냉장고에 없습니다.")
        if qty <= 0:
            raise ValueError(f"사용량은 양수여야 합니다. 입력값: {qty}")
        if qty > self.items[name].quantity:
            raise ValueError(
                f"보유량({self.items[name].quantity} {self.items[name].unit})보다 "
                f"많은 양({qty})을 사용할 수 없습니다."
            )

        self.items[name].quantity -= qty

        # 이력 기록
        self.history.append({
            "action": "used",
            "name": name,
            "qty": qty,
            "date": datetime.date.today().isoformat(),
        })

        # 수량이 0이 되면 자동 삭제
        if self.items[name].quantity <= 0:
            del self.items[name]

    def discard_ingredient(self, name: str) -> None:
        """식재료를 폐기하고 이력에 'discarded'를 기록합니다.

        Args:
            name: 폐기할 식재료 이름

        Raises:
            KeyError: 해당 식재료가 냉장고에 없는 경우
        """
        if name not in self.items:
            raise KeyError(f"'{name}'은(는) 냉장고에 없습니다.")

        qty = self.items[name].quantity

        self.history.append({
            "action": "discarded",
            "name": name,
            "qty": qty,
            "date": datetime.date.today().isoformat(),
        })

        del self.items[name]

    def search(self, keyword: str) -> list[Ingredient]:
        """키워드로 식재료를 검색합니다 (부분 문자열 매칭).

        Args:
            keyword: 검색할 키워드

        Returns:
            list[Ingredient]: 키워드를 포함하는 식재료 목록
        """
        return [
            ingredient
            for name, ingredient in self.items.items()
            if keyword in name
        ]

    def get_expiring(self, threshold: int = 3) -> list[Ingredient]:
        """유통기한이 임박한 식재료를 반환합니다.

        Args:
            threshold: 임박 기준 일수 (기본값 3일)

        Returns:
            list[Ingredient]: 임박 식재료 목록 (남은 일수 오름차순 정렬)
        """
        expiring = [
            item for item in self.items.values()
            if item.is_expiring(threshold)
        ]
        return sorted(expiring, key=lambda x: x.days_left())

    def get_expired(self) -> list[Ingredient]:
        """이미 만료된 식재료(남은 일수 < 0)를 반환합니다.

        Returns:
            list[Ingredient]: 만료 식재료 목록
        """
        return [
            item for item in self.items.values()
            if item.days_left() < 0
        ]

    def get_low_stock(self, threshold: float = 1) -> list[Ingredient]:
        """재고가 부족한 식재료를 반환합니다.

        Args:
            threshold: 부족 기준 수량 (기본값 1, 이 값 이하이면 부족)

        Returns:
            list[Ingredient]: 재고 부족 식재료 목록
        """
        return [
            item for item in self.items.values()
            if item.quantity <= threshold
        ]

    def show_by_category(self) -> None:
        """카테고리별로 그룹화하여 식재료 목록을 출력합니다."""
        # 카테고리 → 식재료 리스트 딕셔너리 구성
        grouped: dict[str, list[Ingredient]] = {}
        for item in self.items.values():
            grouped.setdefault(item.category, []).append(item)

        if not grouped:
            print("  냉장고가 비어 있습니다.")
            return

        for category, items in sorted(grouped.items()):
            emoji = CATEGORY_EMOJI.get(category, "🍽️")
            print(f"\n  {emoji} [{category}]  ({len(items)}종)")
            for item in sorted(items, key=lambda x: x.name):
                print(f"    {item}")
