"""Normalize wardrobe types into shared outfit categories."""

from typing import Literal, TypeAlias


ItemCategory: TypeAlias = Literal[
    "top",
    "bottom",
    "dress",
    "shoes",
    "outerwear",
    "headwear",
    "socks",
    "bag",
    "accessory",
]


CATEGORY_ALIASES: dict[ItemCategory, set[str]] = {
    "top": {
        "top",
        "shirt",
        "hemd",
        "hoodie",
        "bluse",
        "pullover",
        "strick",
    },
    "bottom": {
        "bottom",
        "hose",
        "jeans",
        "rock",
    },
    "dress": {
        "dress",
        "kleid",
    },
    "shoes": {
        "shoes",
        "schuhe",
        "stiefel",
        "boots",
        "sneaker",
        "sandalen",
        "loafer",
    },
    "outerwear": {
        "outerwear",
        "jacke",
        "mantel",
        "weste",
        "blazer",
        "parka",
        "coat",
    },
    "headwear": {
        "headwear",
        "kopfbedeckung",
        "mütze",
        "muetze",
        "beanie",
        "cap",
        "hut",
    },
    "socks": {
        "socks",
        "socken",
    },
    "bag": {
        "bag",
        "tasche",
        "rucksack",
    },
    "accessory": {
        "accessory",
        "accessoire",
    },
}


HEADWEAR_WORDS = {
    "mütze",
    "muetze",
    "beanie",
    "cap",
    "hut",
    "sturmhaube",
}

BAG_WORDS = {
    "tasche",
    "rucksack",
    "bag",
    "daypack",
    "drybag",
}

SOCK_WORDS = {
    "socke",
    "socken",
}

SPORT_SHOE_WORDS = {
    "schuh",
    "schuhe",
    "sneaker",
    "stiefel",
    "boots",
}

SPORT_BOTTOM_WORDS = {
    "hose",
    "leggings",
    "shorts",
    "rock",
}

SPORT_TOP_WORDS = {
    "shirt",
    "top",
    "oberteil",
    "pullover",
    "hoodie",
}

SPORT_OUTERWEAR_WORDS = {
    "jacke",
    "windbreaker",
    "weste",
    "mantel",
}


def normalize_text(value: object) -> str:
    """Convert a value to stripped case-insensitive text."""
    return str(value or "").strip().casefold()


def contains_any(
    text: str,
    words: set[str],
) -> bool:
    """Return whether any supplied word occurs in the text."""
    return any(
        word in text
        for word in words
    )


def classify_item_category(
    item_type: object,
    item_name: object = "",
    description: object = "",
) -> ItemCategory | None:
    """Classify an item from its type, name, and description."""
    normalized_type = normalize_text(item_type)

    searchable_text = " ".join(
        part
        for part in (
            normalize_text(item_name),
            normalize_text(description),
        )
        if part
    )


    if normalized_type in {
        "accessory",
        "accessoire",
    }:
        if contains_any(
            searchable_text,
            HEADWEAR_WORDS,
        ):
            return "headwear"

        if contains_any(
            searchable_text,
            BAG_WORDS,
        ):
            return "bag"

        if contains_any(
            searchable_text,
            SOCK_WORDS,
        ):
            return "socks"

        return "accessory"


    if normalized_type in {
        "unterwäsche",
        "unterwaesche",
        "underwear",
    }:
        if contains_any(
            searchable_text,
            SOCK_WORDS,
        ):
            return "socks"

        return None


    if normalized_type == "sport":
        if contains_any(
            searchable_text,
            SPORT_SHOE_WORDS,
        ):
            return "shoes"

        if contains_any(
            searchable_text,
            SPORT_OUTERWEAR_WORDS,
        ):
            return "outerwear"

        if contains_any(
            searchable_text,
            SPORT_BOTTOM_WORDS,
        ):
            return "bottom"

        if contains_any(
            searchable_text,
            SPORT_TOP_WORDS,
        ):
            return "top"

        return None

    for category, aliases in CATEGORY_ALIASES.items():
        if normalized_type in aliases:
            return category

    return None


def get_item_category(
    item: dict,
) -> ItemCategory | None:
    """Return the normalized category for a wardrobe item."""
    if not isinstance(item, dict):
        raise TypeError(
            "item muss ein Dictionary sein."
        )

    return classify_item_category(
        item_type=item.get("type"),
        item_name=item.get("name"),
        description=item.get("description"),
    )