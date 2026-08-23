from typing import cast

from ai_models.gemini.query_embedding_gemini import (
    input_to_vector,
)

from ai_models.gemini.candidate_preparation_gemini import (
    prepare_candidates_for_gemini,
)
from ai_models.gemini.outfit_retry_gemini import (
    generate_valid_gemini_outfit_result,
)
from ai_models.shared.balanced_candidate_retrieval import (
    DEFAULT_CATEGORY_LIMITS,
)

from ai_models.shared.item_category_mapper import (
    ItemCategory,
)
from ai_models.gemini.adaptive_candidate_retrieval_gemini import (
    retrieve_adaptive_gemini_candidates,
)


def split_gemini_input_data(
    input_data: dict,
) -> tuple[
    dict,
    list[ItemCategory],
    dict[ItemCategory, int],
]:
    if not isinstance(input_data, dict):
        raise TypeError(
            "input_data muss ein Dictionary sein."
        )

    retrieval_data = input_data.get(
        "retrieval",
        {},
    )

    if retrieval_data is None:
        retrieval_data = {}

    if not isinstance(retrieval_data, dict):
        raise TypeError(
            "input_data['retrieval'] muss "
            "ein Dictionary sein."
        )

    raw_priority_categories = (
        retrieval_data.get(
            "priority_categories",
            [],
        )
    )

    if raw_priority_categories is None:
        raw_priority_categories = []

    if not isinstance(
        raw_priority_categories,
        list,
    ):
        raise TypeError(
            "priority_categories muss "
            "eine Liste sein."
        )

    raw_limit_overrides = (
        retrieval_data.get(
            "category_limit_overrides",
            {},
        )
    )

    if raw_limit_overrides is None:
        raw_limit_overrides = {}

    if not isinstance(
        raw_limit_overrides,
        dict,
    ):
        raise TypeError(
            "category_limit_overrides muss "
            "ein Dictionary sein."
        )

    valid_categories = set(
        DEFAULT_CATEGORY_LIMITS
    )

    priority_categories: list[
        ItemCategory
    ] = []

    for category in raw_priority_categories:
        if (
            not isinstance(category, str)
            or category not in valid_categories
        ):
            raise ValueError(
                "Unbekannte Prioritätskategorie: "
                f"{category!r}"
            )

        normalized_category = cast(
            ItemCategory,
            category,
        )

        if (
            normalized_category
            not in priority_categories
        ):
            priority_categories.append(
                normalized_category
            )

    category_limit_overrides: dict[
        ItemCategory,
        int
    ] = {}

    for category, limit in (
        raw_limit_overrides.items()
    ):
        if (
            not isinstance(category, str)
            or category not in valid_categories
        ):
            raise ValueError(
                "Unbekannte Kategorie im "
                f"Limit: {category!r}"
            )

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
        ):
            raise TypeError(
                f"Das Limit für {category} muss "
                "eine Ganzzahl sein."
            )

        if limit < 0:
            raise ValueError(
                f"Das Limit für {category} darf "
                "nicht negativ sein."
            )

        normalized_category = cast(
            ItemCategory,
            category,
        )

        category_limit_overrides[
            normalized_category
        ] = limit

    generation_input_data = {
        key: value
        for key, value in input_data.items()
        if key != "retrieval"
    }

    return (
        generation_input_data,
        priority_categories,
        category_limit_overrides,
    )


def create_gemini_outfit_result(
    input_data: dict,
    filtered_ids: list[int] | None = None,
    search_limit: int | None = None,
    max_generation_tries: int = 3,
    *,
    retrieval_limit: int = 100,
    candidate_limit: int = 20,
) -> dict:
    (
        generation_input_data,
        priority_categories,
        category_limit_overrides,
    ) = split_gemini_input_data(
        input_data
    )

    effective_retrieval_limit = (
        search_limit
        if search_limit is not None
        else retrieval_limit
    )

    query_vector = input_to_vector(
        generation_input_data
    )

    retrieval_result = (
        retrieve_adaptive_gemini_candidates(
            input_vector=query_vector,
            filtered_ids=filtered_ids,
            retrieval_limit=(
                effective_retrieval_limit
            ),
            candidate_limit=candidate_limit,
            category_limits=(
                category_limit_overrides
            ),
            priority_categories=(
                priority_categories
            ),
        )
    )

    balanced_search_results = (
        retrieval_result[
            "candidate_items"
        ]
    )

    pool_analysis = retrieval_result[
        "pool_analysis"
    ]

    if (
        retrieval_result[
            "final_result_count"
        ]
        == 0
    ):
        raise ValueError(
            "Die Gemini-Suche hat keine "
            "Kandidaten gefunden."
        )

    if not balanced_search_results:
        raise ValueError(
            "Die Gemini-Suche hat keine "
            "kategorisierbaren Kandidaten "
            "gefunden."
        )

    if not pool_analysis["is_feasible"]:
        raise ValueError(
            "Auch der adaptive Such-Fallback "
            "hat nicht genügend erlaubte "
            "Kleidungsstücke gefunden. "
            f"Kategorien: "
            f"{pool_analysis['category_counts']}. "
            f"Mögliche Basiskombinationen: "
            f"{pool_analysis['base_variants']} "
            f"von "
            f"{pool_analysis['required_outfits']}. "
            f"Schuhe vorhanden: "
            f"{pool_analysis['has_shoes']}. "
            f"Fallback verwendet: "
            f"{retrieval_result['fallback_used']}. "
            f"Fallback-Grund: "
            f"{retrieval_result['fallback_reason']}."
        )

    candidates, allowed_ids = (
        prepare_candidates_for_gemini(
            balanced_search_results
        )
    )

    result = generate_valid_gemini_outfit_result(
        input_data=generation_input_data,
        candidates=candidates,
        allowed_ids=allowed_ids,
        max_tries=max_generation_tries,
    )

    result["retrieval_diagnostics"] = {
        "retrieved_items": (
            retrieval_result[
                "final_result_count"
            ]
        ),
        "candidate_items": len(
            balanced_search_results
        ),
        "priority_categories": (
            priority_categories
        ),
        "category_limit_overrides": (
            category_limit_overrides
        ),
        "category_counts": (
            pool_analysis[
                "category_counts"
            ]
        ),
        "initial_limit": (
            retrieval_result[
                "initial_limit"
            ]
        ),
        "final_limit": (
            retrieval_result[
                "final_limit"
            ]
        ),
        "initial_retrieved_items": (
            retrieval_result[
                "initial_result_count"
            ]
        ),
        "initial_category_counts": (
            retrieval_result[
                "initial_pool_analysis"
            ]["category_counts"]
        ),
        "fallback_used": (
            retrieval_result[
                "fallback_used"
            ]
        ),
        "fallback_reason": (
            retrieval_result[
                "fallback_reason"
            ]
        ),
        "filtered_scope_size": (
            retrieval_result[
                "filtered_scope_size"
            ]
        ),
        "retrieval_passes": (
            2
            if retrieval_result[
                "fallback_used"
            ]
            else 1
        ),
        "hard_filters_preserved": True,
    }
    return result