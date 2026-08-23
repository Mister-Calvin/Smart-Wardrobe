from typing import TypedDict

from ai_models.shared.balanced_candidate_retrieval import (
    DEFAULT_CATEGORY_LIMITS,
)
from ai_models.shared.item_category_mapper import (
    ItemCategory,
)


class RetrievalPreferences(TypedDict):
    priority_categories: list[ItemCategory]
    category_limit_overrides: dict[
        ItemCategory,
        int,
    ]


def normalize_text(
    value: object,
) -> str:
    return str(value or "").strip().casefold()


def contains_any(
    text: str,
    keywords: set[str],
) -> bool:
    return any(
        keyword in text
        for keyword in keywords
    )


def build_retrieval_preferences(
    weather: object = "",
    event: object = "",
    mood: object = "",
) -> RetrievalPreferences:
    normalized_weather = normalize_text(
        weather
    )
    normalized_event = normalize_text(
        event
    )
    normalized_mood = normalize_text(
        mood
    )

    priority_categories: list[
        ItemCategory
    ] = []

    category_limit_overrides: dict[
        ItemCategory,
        int
    ] = {}

    def prioritize(
        category: ItemCategory,
        extra_items: int = 1,
    ) -> None:
        if category not in priority_categories:
            priority_categories.append(
                category
            )

        new_limit = (
            DEFAULT_CATEGORY_LIMITS[category]
            + extra_items
        )

        current_limit = (
            category_limit_overrides.get(
                category,
                DEFAULT_CATEGORY_LIMITS[
                    category
                ],
            )
        )

        category_limit_overrides[category] = (
            max(
                current_limit,
                new_limit,
            )
        )

    # Kälte benötigt zusätzliche Schutzschichten.
    if contains_any(
        normalized_weather,
        {
            "kalt",
            "kühl",
            "frost",
            "frostig",
            "schnee",
            "eisig",
            "frieren",
        },
    ):
        prioritize("outerwear")
        prioritize("headwear")
        prioritize("socks")

    # Regen und Wind benötigen mehr Oberbekleidung.
    # Wasserfestigkeit selbst bewertet die Similarity Search.
    if contains_any(
        normalized_weather,
        {
            "regen",
            "regnerisch",
            "nass",
            "schauer",
            "sprühregen",
            "wind",
            "windig",
            "sturm",
            "stürmisch",
        },
    ):
        prioritize("outerwear")

    # Für Arbeit können Blazer oder Jacken relevant sein.
    if contains_any(
        normalized_event,
        {
            "arbeit",
            "büro",
            "office",
            "meeting",
            "termin",
            "kunden",
        },
    ):
        prioritize("outerwear")

    # Formelle Anlässe profitieren von mehr Auswahl
    # bei Kleidern und ergänzenden Teilen.
    elif contains_any(
        normalized_event,
        {
            "formal",
            "hochzeit",
            "gala",
            "anzug",
            "feierlich",
        },
    ):
        prioritize("dress")
        prioritize("outerwear")
        prioritize("bag")
        prioritize("accessory")

    # Bei Date oder Restaurant sind ergänzende
    # Teile besonders relevant.
    elif contains_any(
        normalized_event,
        {
            "date",
            "dinner",
            "essen",
            "restaurant",
        },
    ):
        prioritize("bag")
        prioritize("accessory")

    # Bei gemütlichen Looks sind zusätzliche
    # Socken sinnvoll, nicht zusätzliche Basisteile.
    if contains_any(
        normalized_mood,
        {
            "gemütlich",
            "comfy",
            "entspannt",
            "chillig",
            "cozy",
            "locker",
        },
    ):
        prioritize("socks")

    # Auffällige Looks profitieren von Accessoires.
    if contains_any(
        normalized_mood,
        {
            "selbstbewusst",
            "mutig",
            "bold",
            "auffällig",
            "statement",
            "verspielt",
            "fun",
            "bunt",
            "fröhlich",
            "spielerisch",
        },
    ):
        prioritize("accessory")

    return {
        "priority_categories": (
            priority_categories
        ),
        "category_limit_overrides": (
            category_limit_overrides
        ),
    }