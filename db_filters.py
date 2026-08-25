import psycopg2
import os
from dotenv import load_dotenv
import json

load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL fehlt in der .env."
    )


def norm_terms(values):
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
    colors_any: list[str] | None = None,   # OR: mindestens eine Farbe enthalten
    colors_all: list[str] | None = None,   # AND: alle Farben enthalten
    score: int | None = None,              # exakt
    score_min: int | None = None,
    score_max: int | None = None,
    condition_any: list[str] | None = None,  # OR
    name_contains: list[str] | None = None,  # AND (im name)
    description_contains: list[str] | None = None,  # AND (in description)
    text_all: list[str] | None = None,      # AND: jeder Term muss in name ODER description vorkommen
    text_any: list[str] | None = None,      # OR: mindestens ein Term muss in name ODER description vorkommen
    limit: int | None = None,
):
    conn = psycopg2.connect(
    DATABASE_URL
)
    cur = conn.cursor()

    clauses = []
    params = []



    # ---- Farben tokenisieren: lower + '-' -> ' ' + split on commas/whitespace
    # Ergebnis ist text[] wie ['schwarz','weiß','orange']
    color_tokens_sql = "regexp_split_to_array(replace(lower(color), '-', ' '), '[,\\s]+')"

    # OR-Farben: enthält mindestens eine der Farben
    if colors_any:
        clauses.append(f"{color_tokens_sql} && %s::text[]")
        params.append([c.strip().lower() for c in colors_any if c and c.strip()])

    # AND-Farben: enthält alle Farben
    if colors_all:
        clauses.append(f"{color_tokens_sql} @> %s::text[]")
        params.append([c.strip().lower() for c in colors_all if c and c.strip()])

    # Condition (OR, case-insensitive)
    if condition_any:
        clauses.append("lower(condition) = ANY(%s)")
        params.append([c.strip().lower() for c in condition_any if c and c.strip()])

    # Score exakt (wichtig: is not None statt if score)
    if score is not None:
        clauses.append("score = %s")
        params.append(int(score))

    # ---- Partial Search in name/description (case-insensitive)
    # name_contains: alle angegebenen Begriffe müssen im Namen vorkommen (AND)
    for term in norm_terms(name_contains):
        clauses.append("lower(name) LIKE %s")
        params.append(f"%{term}%")

    # description_contains: alle angegebenen Begriffe müssen in der Beschreibung vorkommen (AND)
    for term in norm_terms(description_contains):
        clauses.append("lower(description) LIKE %s")
        params.append(f"%{term}%")

    # text_all: jeder Term muss in name ODER description vorkommen (AND über Terme)
    for term in norm_terms(text_all):
        clauses.append("(lower(name) LIKE %s OR lower(description) LIKE %s)")
        params.extend([f"%{term}%", f"%{term}%"])

    # text_any: mindestens ein Term muss in name ODER description vorkommen (OR über Terme)
    any_terms = norm_terms(text_any)
    if any_terms:
        or_parts = []
        for term in any_terms:
            or_parts.append("lower(name) LIKE %s")
            params.append(f"%{term}%")
            or_parts.append("lower(description) LIKE %s")
            params.append(f"%{term}%")
        clauses.append("(" + " OR ".join(or_parts) + ")")

    # Score Range
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

    with open("filtered_ids.json", "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)

    return ids


def _split_terms(s: str) -> list[str]:
    """Split input like 'schwarz, blau' or 'schwarz blau' into lowercase tokens."""
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
