from collections.abc import Iterable

from ai_models.shared.item_category_mapper import (
    ItemCategory,
    get_item_category,
)


DEFAULT_CATEGORY_LIMITS: dict[ItemCategory, int] = {
    "top": 4,
    "bottom": 4,
    "dress": 2,
    "shoes": 3,
    "outerwear": 2,
    "headwear": 1,
    "socks": 1,
    "bag": 1,
    "accessory": 2,
}


CORE_CATEGORY_ORDER: tuple[ItemCategory, ...] = (
    "top",
    "bottom",
    "shoes",
    "dress",
)


OPTIONAL_CATEGORY_ORDER: tuple[ItemCategory, ...] = (
    "outerwear",
    "headwear",
    "socks",
    "bag",
    "accessory",
)


def build_category_order(
    priority_categories: Iterable[ItemCategory] | None = None,
) -> tuple[ItemCategory, ...]:
    ordered_categories: list[ItemCategory] = []
    seen_categories: set[ItemCategory] = set()

    def add_category(category: ItemCategory) -> None:
        if category in seen_categories:
            return

        ordered_categories.append(category)
        seen_categories.add(category)

    # Basisteile bleiben immer zuerst.
    for category in CORE_CATEGORY_ORDER:
        add_category(category)

    # Später kann agentic_ai hier beispielsweise
    # outerwear oder headwear priorisieren.
    for category in priority_categories or ():
        add_category(category)

    for category in OPTIONAL_CATEGORY_ORDER:
        add_category(category)

    return tuple(ordered_categories)


def build_category_limits(
    category_limits: dict[ItemCategory, int] | None = None,
) -> dict[ItemCategory, int]:
    limits = DEFAULT_CATEGORY_LIMITS.copy()

    if category_limits is None:
        return limits

    for category, limit in category_limits.items():
        if category not in limits:
            raise ValueError(
                f"Unbekannte Kategorie: {category}"
            )

        if not isinstance(limit, int):
            raise TypeError(
                f"Das Limit für {category} muss "
                "eine Ganzzahl sein."
            )

        if limit < 0:
            raise ValueError(
                f"Das Limit für {category} darf "
                "nicht negativ sein."
            )

        limits[category] = limit

    return limits


def group_items_by_category(
    items: list[dict],
) -> dict[ItemCategory, list[dict]]:
    if not isinstance(items, list):
        raise TypeError(
            "items muss eine Liste sein."
        )

    grouped_items: dict[ItemCategory, list[dict]] = {
        category: []
        for category in DEFAULT_CATEGORY_LIMITS
    }

    seen_ids: set[int] = set()

    for item in items:
        if not isinstance(item, dict):
            raise TypeError(
                "Jedes Item muss ein Dictionary sein."
            )

        item_id = item.get("id")

        if not isinstance(item_id, int):
            raise ValueError(
                "Jedes Item benötigt eine ganzzahlige ID."
            )

        if item_id in seen_ids:
            continue

        seen_ids.add(item_id)

        category = get_item_category(item)

        if category is None:
            continue

        grouped_items[category].append(item)

    return grouped_items


def count_pool_categories(
    items: list[dict],
) -> dict[ItemCategory, int]:
    counts: dict[ItemCategory, int] = {
        category: 0
        for category in DEFAULT_CATEGORY_LIMITS
    }

    for item in items:
        category = get_item_category(item)

        if category is not None:
            counts[category] += 1

    return counts


def build_balanced_candidate_pool(
    search_results: list[dict],
    max_candidates: int = 20,
    category_limits: dict[ItemCategory, int] | None = None,
    priority_categories: Iterable[ItemCategory] | None = None,
) -> list[dict]:
    if not isinstance(max_candidates, int):
        raise TypeError(
            "max_candidates muss eine Ganzzahl sein."
        )

    if max_candidates <= 0:
        raise ValueError(
            "max_candidates muss größer als 0 sein."
        )

    limits = build_category_limits(
        category_limits
    )

    category_order = build_category_order(
        priority_categories
    )

    grouped_items = group_items_by_category(
        search_results
    )

    category_positions: dict[ItemCategory, int] = {
        category: 0
        for category in limits
    }

    selected_counts: dict[ItemCategory, int] = {
        category: 0
        for category in limits
    }

    selected_items: list[dict] = []

    # Round-Robin-Auswahl:
    # erst ein Top, dann ein Bottom, dann Schuhe usw.
    # Danach beginnt die nächste Runde.
    while len(selected_items) < max_candidates:
        item_added = False

        for category in category_order:
            if len(selected_items) >= max_candidates:
                break

            if selected_counts[category] >= limits[category]:
                continue

            position = category_positions[category]
            category_items = grouped_items[category]

            if position >= len(category_items):
                continue

            selected_items.append(
                category_items[position]
            )

            category_positions[category] += 1
            selected_counts[category] += 1
            item_added = True

        if not item_added:
            break

    return selected_items