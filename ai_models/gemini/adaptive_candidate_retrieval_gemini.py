"""Retrieve balanced Gemini candidates with an adaptive fallback."""

from collections.abc import Iterable
from typing import TypedDict

from ai_models.gemini.similarity_search_gemini import (
    search_similar_items,
)
from ai_models.shared.balanced_candidate_retrieval import (
    build_balanced_candidate_pool,
)
from ai_models.shared.candidate_pool_validation import (
    CandidatePoolAnalysis,
    analyze_candidate_pool,
)
from ai_models.shared.item_category_mapper import (
    ItemCategory,
)


class AdaptiveCandidateRetrievalResult(
    TypedDict
):
    """Describe candidate retrieval results and fallback diagnostics."""
    candidate_items: list[dict]
    pool_analysis: CandidatePoolAnalysis
    initial_pool_analysis: CandidatePoolAnalysis

    initial_limit: int
    final_limit: int

    initial_result_count: int
    final_result_count: int

    filtered_scope_size: int | None
    fallback_used: bool
    fallback_reason: str


def validate_positive_integer(
    value: object,
    name: str,
) -> int:
    """Validate and return a positive integer setting."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
    ):
        raise TypeError(
            f"{name} muss eine Ganzzahl sein."
        )

    if value <= 0:
        raise ValueError(
            f"{name} muss größer als 0 sein."
        )

    return value


def build_candidate_state(
    search_results: list[dict],
    candidate_limit: int,
    category_limits: (
        dict[ItemCategory, int] | None
    ),
    priority_categories: (
        Iterable[ItemCategory] | None
    ),
) -> tuple[
    list[dict],
    CandidatePoolAnalysis,
]:
    """Balance search results and analyze whether they can form enough outfits."""
    candidate_items = (
        build_balanced_candidate_pool(
            search_results=search_results,
            max_candidates=candidate_limit,
            category_limits=category_limits,
            priority_categories=(
                priority_categories
            ),
        )
    )

    pool_analysis = analyze_candidate_pool(
        items=candidate_items,
        required_outfits=3,
    )

    return (
        candidate_items,
        pool_analysis,
    )


def retrieve_adaptive_gemini_candidates(
    input_vector: list[float],
    filtered_ids: list[int] | None = None,
    retrieval_limit: int = 100,
    fallback_retrieval_limit: int = 500,
    candidate_limit: int = 20,
    category_limits: (
        dict[ItemCategory, int] | None
    ) = None,
    priority_categories: (
        Iterable[ItemCategory] | None
    ) = None,
) -> AdaptiveCandidateRetrievalResult:
    """Retrieve candidates and expand the search when the first pool is insufficient."""
    retrieval_limit = (
        validate_positive_integer(
            retrieval_limit,
            "retrieval_limit",
        )
    )

    fallback_retrieval_limit = (
        validate_positive_integer(
            fallback_retrieval_limit,
            "fallback_retrieval_limit",
        )
    )

    candidate_limit = (
        validate_positive_integer(
            candidate_limit,
            "candidate_limit",
        )
    )

    normalized_priorities = tuple(
        priority_categories or ()
    )

    initial_search_results = (
        search_similar_items(
            input_vector=input_vector,
            filtered_ids=filtered_ids,
            limit=retrieval_limit,
        )
    )

    (
        initial_candidate_items,
        initial_pool_analysis,
    ) = build_candidate_state(
        search_results=(
            initial_search_results
        ),
        candidate_limit=candidate_limit,
        category_limits=category_limits,
        priority_categories=(
            normalized_priorities
        ),
    )

    filtered_scope_size = (
        len(set(filtered_ids))
        if filtered_ids is not None
        else None
    )

    fallback_used = False
    fallback_reason = (
        "initial_pool_feasible"
    )

    final_limit = retrieval_limit
    final_search_results = (
        initial_search_results
    )
    final_candidate_items = (
        initial_candidate_items
    )
    final_pool_analysis = (
        initial_pool_analysis
    )

    if not initial_pool_analysis[
        "is_feasible"
    ]:
        if filtered_scope_size is not None:
            fallback_target = (
                filtered_scope_size
            )
        else:
            fallback_target = max(
                retrieval_limit,
                fallback_retrieval_limit,
            )

        if fallback_target <= retrieval_limit:
            fallback_reason = (
                "no_larger_search_scope"
            )

        elif (
            len(initial_search_results)
            < retrieval_limit
        ):
            fallback_reason = (
                "search_scope_exhausted"
            )

        else:
            fallback_used = True
            fallback_reason = (
                "expanded_search"
            )
            final_limit = fallback_target

            final_search_results = (
                search_similar_items(
                    input_vector=input_vector,
                    filtered_ids=filtered_ids,
                    limit=final_limit,
                )
            )

            (
                final_candidate_items,
                final_pool_analysis,
            ) = build_candidate_state(
                search_results=(
                    final_search_results
                ),
                candidate_limit=(
                    candidate_limit
                ),
                category_limits=(
                    category_limits
                ),
                priority_categories=(
                    normalized_priorities
                ),
            )

    return {
        "candidate_items": (
            final_candidate_items
        ),
        "pool_analysis": (
            final_pool_analysis
        ),
        "initial_pool_analysis": (
            initial_pool_analysis
        ),
        "initial_limit": retrieval_limit,
        "final_limit": final_limit,
        "initial_result_count": len(
            initial_search_results
        ),
        "final_result_count": len(
            final_search_results
        ),
        "filtered_scope_size": (
            filtered_scope_size
        ),
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
    }