"""
스마트 냉장고 관리 시스템 - 레시피 추천 모듈

추천 점수 공식 (score formula):
─────────────────────────────────────────────────────────────────
  score(recipe) = w1 × match_ratio + w2 × urgency - w3 × missing_penalty

  match_ratio    = |보유 재료 ∩ 레시피 재료| / |레시피 재료|
                   → 레시피 재료 중 냉장고에 있는 재료의 비율

  urgency        = Σ urgency_i / |레시피 재료|
                   urgency_i = max(0, 1 - days_left_i / 7)   [단일 임박도]
                   → 7일 이내 임박 재료일수록 urgency_i → 1.0
                   → 만료된 재료(days_left < 0)는 urgency_i = 0

  missing_penalty = |레시피 재료 - 보유 재료| / |레시피 재료|
                   → 없는 재료가 많을수록 페널티 증가

  기본 가중치: w1=0.5, w2=0.4, w3=0.1
─────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from fridge import Fridge
from database import RECIPE_DB, NUTRITION_DB


class RecipeRecommender:
    """냉장고 보유 재료와 유통기한을 고려해 레시피를 추천하는 클래스."""

    # ── 내부 계산 메서드 ──────────────────────────────────────────

    def _match_ratio(self, recipe: dict, fridge: Fridge) -> float:
        """레시피 재료 중 냉장고에 보유 중인 재료의 비율을 계산합니다.

        Args:
            recipe: RECIPE_DB의 단일 레시피 딕셔너리
            fridge: Fridge 인스턴스

        Returns:
            float: 0.0 ~ 1.0 (보유 재료 수 / 전체 재료 수)
        """
        total = len(recipe["ingredients"])
        if total == 0:
            return 0.0

        # 냉장고에 있는 재료만 카운트
        matched = sum(
            1 for ing in recipe["ingredients"]
            if ing["name"] in fridge.items
        )
        return matched / total

    def _urgency(self, recipe: dict, fridge: Fridge) -> float:
        """레시피 재료의 평균 임박도를 계산합니다.

        단일 재료 임박도: urgency_i = max(0, 1 - days_left_i / 7)
        전체 urgency   : Σ urgency_i / 레시피 재료 총 수

        만료된 재료(days_left < 0)는 urgency_i = 0으로 처리합니다.
        (만료 재료를 요리에 쓰는 상황을 방지)

        Args:
            recipe: RECIPE_DB의 단일 레시피 딕셔너리
            fridge: Fridge 인스턴스

        Returns:
            float: 0.0 ~ 1.0 (임박도 평균)
        """
        total = len(recipe["ingredients"])
        if total == 0:
            return 0.0

        urgency_sum = 0.0
        for ing in recipe["ingredients"]:
            if ing["name"] in fridge.items:
                days = fridge.items[ing["name"]].days_left()
                if days >= 0:
                    # 7일 이내일수록 임박도가 1에 가까워짐
                    # days_left=0 → urgency_i=1.0, days_left=7 → urgency_i=0.0
                    urgency_i = max(0.0, 1.0 - days / 7.0)
                    urgency_sum += urgency_i
                # days < 0 (만료) → urgency_i = 0 (합산하지 않음)

        return urgency_sum / total

    def _missing_penalty(self, recipe: dict, fridge: Fridge) -> float:
        """레시피 재료 중 냉장고에 없는 재료의 비율을 계산합니다.

        Args:
            recipe: RECIPE_DB의 단일 레시피 딕셔너리
            fridge: Fridge 인스턴스

        Returns:
            float: 0.0 ~ 1.0 (부족 재료 수 / 전체 재료 수)
        """
        total = len(recipe["ingredients"])
        if total == 0:
            return 0.0

        missing = sum(
            1 for ing in recipe["ingredients"]
            if ing["name"] not in fridge.items
        )
        return missing / total

    # ── 점수 계산 & 추천 ─────────────────────────────────────────

    def score(
        self,
        recipe: dict,
        fridge: Fridge,
        w1: float = 0.5,
        w2: float = 0.4,
        w3: float = 0.1,
    ) -> float:
        """레시피 추천 점수를 계산합니다.

        공식:
            score = w1 × match_ratio + w2 × urgency - w3 × missing_penalty

        Args:
            recipe: RECIPE_DB의 단일 레시피 딕셔너리
            fridge: Fridge 인스턴스
            w1: match_ratio 가중치 (기본 0.5)
            w2: urgency 가중치 (기본 0.4)
            w3: missing_penalty 가중치 (기본 0.1)

        Returns:
            float: 추천 점수 (높을수록 지금 만들기 적합한 레시피)
        """
        match   = self._match_ratio(recipe, fridge)      # 보유 재료 비율
        urgency = self._urgency(recipe, fridge)           # 임박도 평균
        penalty = self._missing_penalty(recipe, fridge)   # 부족 재료 비율

        # score = w1×보유비율 + w2×임박도 - w3×부족패널티
        return w1 * match + w2 * urgency - w3 * penalty

    def recommend(self, fridge: Fridge, top_n: int = 3) -> list[tuple]:
        """점수 기준 상위 N개 레시피를 반환합니다.

        sorted() + lambda로 점수 기준 내림차순 정렬 후 상위 top_n개를 선택합니다.

        Args:
            fridge: Fridge 인스턴스
            top_n: 반환할 추천 개수 (기본 3)

        Returns:
            list[tuple]: (recipe_dict, score) 튜플 리스트, 점수 내림차순
        """
        scored = [
            (recipe, self.score(recipe, fridge))
            for recipe in RECIPE_DB
        ]
        # lambda로 점수(인덱스 1) 기준 내림차순 정렬
        scored = sorted(scored, key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    # ── 출력 ─────────────────────────────────────────────────────

    def print_recommendation(self, fridge: Fridge, top_n: int = 3) -> None:
        """추천 레시피를 상세하게 출력합니다.

        점수·보유/부족 재료·임박 재료 강조·1인분 영양 정보·조리법 포함.

        Args:
            fridge: Fridge 인스턴스
            top_n: 추천 개수 (기본 3)
        """
        results = self.recommend(fridge, top_n)

        if not results:
            print("  추천할 레시피가 없습니다.")
            return

        print(f"\n  🍳 요리 추천 TOP {top_n}")
        print("  " + "=" * 52)

        for rank, (recipe, sc) in enumerate(results, start=1):
            name      = recipe["name"]
            servings  = recipe["servings"]
            ings      = recipe["ingredients"]

            # 보유·부족 재료 분류
            have    = [i for i in ings if i["name"] in fridge.items]
            missing = [i for i in ings if i["name"] not in fridge.items]

            # 임박 재료: 보유 중이면서 남은 일수 ≤ 3일
            urgent = [
                i for i in have
                if fridge.items[i["name"]].days_left() <= 3
            ]

            print(f"\n  [{rank}위] 🍽️  {name}  (점수: {sc:.3f})")
            print(f"       인분: {servings}인분")
            print(f"       📊 공식: 0.5×보유비율 + 0.4×임박도 - 0.1×부족패널티")
            print(f"            → match={self._match_ratio(recipe, fridge):.2f}, "
                  f"urgency={self._urgency(recipe, fridge):.2f}, "
                  f"penalty={self._missing_penalty(recipe, fridge):.2f}")

            # 보유 재료 목록
            have_str = ", ".join(
                f"{i['name']}({i['amount']}{i['unit']})" for i in have
            ) or "없음"
            print(f"       ✅ 보유: {have_str}")

            # 임박 재료 강조
            if urgent:
                urgent_str = ", ".join(
                    f"⚠️ {i['name']}({fridge.items[i['name']].days_left()}일)" for i in urgent
                )
                print(f"       🔥 임박: {urgent_str}")

            # 부족 재료 목록
            if missing:
                miss_str = ", ".join(
                    f"{i['name']}({i['amount']}{i['unit']})" for i in missing
                )
                print(f"       ❌ 부족: {miss_str}")

            # 1인분 영양 정보
            self._print_nutrition(recipe, servings)

            # 조리법
            print(f"\n       📋 조리법:")
            print(f"          {recipe['instructions']}")
            print("  " + "-" * 52)

    def _print_nutrition(self, recipe: dict, servings: int) -> None:
        """레시피 1인분 기준 영양 정보를 출력합니다.

        단위가 g인 재료만 계산합니다. (개·대 등 단위 재료는 제외)

        Args:
            recipe: 레시피 딕셔너리
            servings: 총 인분 수
        """
        total_kcal    = 0.0
        total_protein = 0.0
        total_carb    = 0.0
        total_fat     = 0.0
        calculated    = False

        for ing in recipe["ingredients"]:
            nutrition = NUTRITION_DB.get(ing["name"])
            # 단위가 'g'인 재료만 100g 기준으로 계산
            if nutrition and ing["unit"] == "g":
                ratio = ing["amount"] / 100.0
                total_kcal    += nutrition["kcal"]    * ratio
                total_protein += nutrition["protein"] * ratio
                total_carb    += nutrition["carb"]    * ratio
                total_fat     += nutrition["fat"]     * ratio
                calculated = True

        if calculated:
            print(
                f"       🥗 1인분 영양: "
                f"{total_kcal / servings:.0f} kcal | "
                f"단백질 {total_protein / servings:.1f}g | "
                f"탄수화물 {total_carb / servings:.1f}g | "
                f"지방 {total_fat / servings:.1f}g"
            )
