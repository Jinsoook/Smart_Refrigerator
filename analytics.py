"""
스마트 냉장고 관리 시스템 - 분석 모듈
소비 이력과 냉장고 현황을 분석해 통계·장보기 리스트를 제공합니다.
"""

from __future__ import annotations

from fridge import Fridge
from ingredient import CATEGORY_EMOJI
from database import COUPANG_SEARCH


def waste_rate(history: list) -> float:
    """소비 이력에서 폐기율을 계산합니다.

    폐기율 = 폐기 이벤트 수 / 전체 소비 이벤트 수

    Args:
        history: Fridge.history 리스트 (각 항목은 action, name, qty, date 포함)

    Returns:
        float: 0.0 ~ 1.0 사이의 폐기율.
               이벤트가 없으면 0.0 반환.
    """
    total = len(history)
    if total == 0:
        return 0.0

    discarded = sum(1 for event in history if event["action"] == "discarded")
    return discarded / total


def top_used(history: list, n: int = 5) -> list[tuple]:
    """사용 빈도 상위 N개 식재료를 반환합니다.

    collections.Counter 대신 순수 dict로 빈도를 집계합니다.

    Args:
        history: Fridge.history 리스트
        n: 반환할 상위 개수 (기본값 5)

    Returns:
        list[tuple]: (식재료명, 사용횟수) 튜플 리스트, 빈도 내림차순.
                     사용 이력이 없으면 빈 리스트 반환.
    """
    # dict로 각 재료의 사용 횟수 집계
    freq: dict[str, int] = {}
    for event in history:
        if event["action"] == "used":
            name = event["name"]
            freq[name] = freq.get(name, 0) + 1

    # 빈도 내림차순 정렬 후 상위 N개 반환
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_freq[:n]


def category_distribution(fridge: Fridge) -> dict[str, int]:
    """카테고리별 보유 식재료 수를 집계합니다.

    Args:
        fridge: Fridge 인스턴스

    Returns:
        dict[str, int]: {카테고리명: 보유 종 수} 딕셔너리
    """
    distribution: dict[str, int] = {}
    for item in fridge.items.values():
        distribution[item.category] = distribution.get(item.category, 0) + 1
    return distribution


def generate_shopping_list(fridge: Fridge, history: list) -> list[dict]:
    """구매가 필요한 식재료 목록을 생성합니다.

    선정 기준:
        1. 재고가 1 이하인 식재료 (재고 부족)
        2. 소비 이력 상위 5개 중 현재 재고가 없거나 부족한 식재료 (자주 쓰는 재료)

    쿠팡 검색 링크를 포함해 바로 구매할 수 있도록 합니다.

    Args:
        fridge: Fridge 인스턴스
        history: Fridge.history 리스트

    Returns:
        list[dict]: [{"name": ..., "reason": ..., "link": ...}, ...] 리스트
    """
    # 중복 방지를 위해 dict 사용 (key=재료명)
    shopping: dict[str, dict] = {}

    # 기준 1: 재고 임계값(1) 이하인 재료
    for item in fridge.items.values():
        if item.quantity <= 1:
            shopping[item.name] = {
                "name":   item.name,
                "reason": f"재고 부족 (현재 {item.quantity} {item.unit})",
                "link":   COUPANG_SEARCH.format(item.name),
            }

    # 기준 2: 소비 빈도 상위 5개 중 재고 없음 또는 부족
    for name, count in top_used(history, n=5):
        in_fridge = name in fridge.items
        low_stock = in_fridge and fridge.items[name].quantity <= 1

        if not in_fridge or low_stock:
            if name not in shopping:  # 기준 1과 중복이면 건너뜀
                shopping[name] = {
                    "name":   name,
                    "reason": f"자주 사용하는 재료 (사용 {count}회, 재고 부족)",
                    "link":   COUPANG_SEARCH.format(name),
                }

    return list(shopping.values())


def print_statistics(fridge: Fridge, history: list) -> None:
    """소비 통계를 종합적으로 출력합니다.

    폐기율·사용 빈도 TOP 5·카테고리 분포를 포함합니다.

    Args:
        fridge: Fridge 인스턴스
        history: Fridge.history 리스트
    """
    print("\n  📊 소비 통계 리포트")
    print("  " + "=" * 42)

    # 폐기율 및 전체 이벤트 수
    total_events = len(history)
    used_count   = sum(1 for e in history if e["action"] == "used")
    disc_count   = sum(1 for e in history if e["action"] == "discarded")
    rate         = waste_rate(history)

    print(f"  📋 전체 소비 이벤트: {total_events}건")
    print(f"     - 사용: {used_count}건  |  폐기: {disc_count}건")
    print(f"  🗑️  폐기율: {rate * 100:.1f}%", end="")
    if rate == 0.0:
        print("  (폐기 없음 ✅)")
    elif rate < 0.2:
        print("  (양호)")
    elif rate < 0.5:
        print("  (주의 ⚠️)")
    else:
        print("  (위험 🚨 — 유통기한 관리가 필요합니다)")

    # 사용 빈도 상위 5위
    print("\n  🔝 자주 사용한 재료 TOP 5")
    top = top_used(history, n=5)
    if top:
        for i, (name, count) in enumerate(top, start=1):
            bar = "█" * count + "░" * max(0, 5 - count)  # 간단한 막대 그래프
            print(f"    {i}. {name:6s}  {bar}  {count}회")
    else:
        print("    (사용 이력이 없습니다)")

    # 카테고리별 분포
    print("\n  📦 카테고리별 보유 현황")
    dist = category_distribution(fridge)
    if dist:
        total_items = sum(dist.values())
        for category, count in sorted(dist.items()):
            emoji   = CATEGORY_EMOJI.get(category, "🍽️")
            percent = count / total_items * 100
            print(f"    {emoji} {category:6s}: {count}종  ({percent:.0f}%)")
        print(f"    {'':8s}  합계: {total_items}종")
    else:
        print("    (냉장고가 비어 있습니다)")

    print()
