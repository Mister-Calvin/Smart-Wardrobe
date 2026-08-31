"""Build and execute PostgreSQL wardrobe filters from form input."""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL fehlt in der .env."
    )


def norm_terms(values):
    """Normalize nonempty values to stripped lowercase strings."""
    if not values:
        return []
    out = []
    for v in values:
        if v is None:
            continue
        s = str(v).strip().lower()
        if s:
            out.append(s)
    return out

def filter_db_dynamic(
    colors_any: list[str] | None = None,
    colors_all: list[str] | None = None,
    score: int | None = None,
    score_min: int | None = None,
    score_max: int | None = None,
    condition_any: list[str] | None = None,
    name_contains: list[str] | None = None,
    description_contains: list[str] | None = None,
    text_all: list[str] | None = None,
    text_any: list[str] | None = None,
    limit: int | None = None,
):
    """Return IDs of wardrobe items matching the supplied filters."""
    conn = psycopg2.connect(
    DATABASE_URL
)
    cur = conn.cursor()

    clauses = []
    params = []


    color_tokens_sql = "regexp_split_to_array(replace(lower(color), '-', ' '), '[,\\s]+')"


    if colors_any:
        clauses.append(f"{color_tokens_sql} && %s::text[]")
        params.append([c.strip().lower() for c in colors_any if c and c.strip()])


    if colors_all:
        clauses.append(f"{color_tokens_sql} @> %s::text[]")
        params.append([c.strip().lower() for c in colors_all if c and c.strip()])


    if condition_any:
        clauses.append("lower(condition) = ANY(%s)")
        params.append([c.strip().lower() for c in condition_any if c and c.strip()])


    if score is not None:
        clauses.append("score = %s")
        params.append(int(score))


    for term in norm_terms(name_contains):
        clauses.append("lower(name) LIKE %s")
        params.append(f"%{term}%")


    for term in norm_terms(description_contains):
        clauses.append("lower(description) LIKE %s")
        params.append(f"%{term}%")


    for term in norm_terms(text_all):
        clauses.append("(lower(name) LIKE %s OR lower(description) LIKE %s)")
        params.extend([f"%{term}%", f"%{term}%"])


    any_terms = norm_terms(text_any)
    if any_terms:
        or_parts = []
        for term in any_terms:
            or_parts.append("lower(name) LIKE %s")
            params.append(f"%{term}%")
            or_parts.append("lower(description) LIKE %s")
            params.append(f"%{term}%")
        clauses.append("(" + " OR ".join(or_parts) + ")")


    if score_min is not None:
        clauses.append("score >= %s")
        params.append(int(score_min))

    if score_max is not None:
        clauses.append("score <= %s")
        params.append(int(score_max))

    where_sql = ""
    if clauses:
        where_sql = " WHERE " + " AND ".join(clauses)

    limit_sql = ""
    if limit is not None:
        limit_sql = " LIMIT %s"
        params.append(int(limit))

    sql = f"""
        SELECT id, name, description, color, condition, score
        FROM wardrobe
        {where_sql}
        ORDER BY id
        {limit_sql};
    """

    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    ids = [row[0] for row in rows]

    conn.close()

    return ids


def _split_terms(s: str) -> list[str]:
    """Split comma- or space-separated input into lowercase terms."""
    if not s:
        return []
    s = s.strip()
    if not s:
        return []
    parts = []
    for chunk in s.replace(",", " ").split():
        token = chunk.strip().lower()
        if token:
            parts.append(token)
    return parts


def _parse_int(s: str) -> int | None:
    """Return an integer or None for empty and invalid input."""
    s = (s or "").strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def build_filter_kwargs_from_strings(
    colors_any: str = "",
    colors_all: str = "",
    score: str = "",
    score_min: str = "",
    score_max: str = "",
    condition_any: str = "",
    name_contains: str = "",
    description_contains: str = "",
    text_all: str = "",
    text_any: str = "",
    limit: str = "",
) -> dict:
    """Build kwargs for filter_db_dynamic(**kwargs) from raw form strings."""
    kwargs: dict = {}

    ca = _split_terms(colors_any)
    if ca:
        kwargs["colors_any"] = ca

    cal = _split_terms(colors_all)
    if cal:
        kwargs["colors_all"] = cal

    sc = _parse_int(score)
    if sc is not None:
        kwargs["score"] = sc

    smin = _parse_int(score_min)
    if smin is not None:
        kwargs["score_min"] = smin

    smax = _parse_int(score_max)
    if smax is not None:
        kwargs["score_max"] = smax

    cond = _split_terms(condition_any)
    if cond:
        kwargs["condition_any"] = cond

    nc = _split_terms(name_contains)
    if nc:
        kwargs["name_contains"] = nc

    dc = _split_terms(description_contains)
    if dc:
        kwargs["description_contains"] = dc

    ta = _split_terms(text_all)
    if ta:
        kwargs["text_all"] = ta

    tany = _split_terms(text_any)
    if tany:
        kwargs["text_any"] = tany

    lim = _parse_int(limit)
    if lim is not None:
        kwargs["limit"] = lim

    return kwargs
