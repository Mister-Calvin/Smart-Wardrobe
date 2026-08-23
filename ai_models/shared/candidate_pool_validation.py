from typing import TypedDict

from ai_models.shared.balanced_candidate_retrieval import (
    group_items_by_category,
)
from ai_models.shared.item_category_mapper import (
    ItemCategory,
)


class CandidatePoolAnalysis(TypedDict):
    category_counts: dict[ItemCategory, int]
    base_variants: int
    required_outfits: int
    has_shoes: bool
    is_feasible: bool


def analyze_candidate_pool(
    items: list[dict],
    required_outfits: int = 3,
) -> CandidatePoolAnalysis:
    if (
        isinstance(required_outfits, bool)
        or not isinstance(required_outfits, int)
    ):
        raise TypeError(
            "required_outfits muss eine Ganzzahl sein."
        )

    if required_outfits <= 0:
        raise ValueError(
            "required_outfits muss größer als 0 sein."
        )

    grouped_items = group_items_by_category(
        items
    )

    category_counts: dict[ItemCategory, int] = {
        category: len(category_items)
        for category, category_items
        in grouped_items.items()
    }

    normal_outfit_variants = (
        category_counts["top"]
        * category_counts["bottom"]
    )

    dress_outfit_variants = (
        category_counts["dress"]
    )

    base_variants = (
        normal_outfit_variants
        + dress_outfit_variants
    )

    has_shoes = (
        category_counts["shoes"] >= 1
    )

    is_feasible = (
        has_shoes
        and base_variants >= required_outfits
    )

    return {
        "category_counts": category_counts,
        "base_variants": base_variants,
        "required_outfits": required_outfits,
        "has_shoes": has_shoes,
        "is_feasible": is_feasible,
    }


def has_enough_candidates_for_outfits(
    items: list[dict],
    required_outfits: int = 3,
) -> bool:
    analysis = analyze_candidate_pool(
        items=items,
        required_outfits=required_outfits,
    )

    return analysis["is_feasible"]