import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DB_KEY = os.getenv("POSTGRESQL_KEY_ONLY")


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
    conn = psycopg2.connect(f"dbname=wardrobe user=postgres password={DB_KEY}")
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


def create_filter_input() -> dict:
    """
    Sammelt dynamischen Input und baut ein kwargs-dict für filter_db_dynamic(**kwargs).

    WICHTIG: description_contains / text_any etc. werden hier wirklich gesetzt,
    je nachdem was du eintippst.
    """
    kwargs: dict = {}

    input_colors_any = input("wähle Farbe oder Farben (OR) z.B. 'schwarz, blau' (leer = skip): ")
    colors_any = _split_terms(input_colors_any)
    if colors_any:
        kwargs["colors_any"] = colors_any

    input_colors_all = input("wähle Farbkombinationen (AND) z.B. 'schwarz weiß' (leer = skip): ")
    colors_all = _split_terms(input_colors_all)
    if colors_all:
        kwargs["colors_all"] = colors_all

    input_score = input("wähle einen festen score (z.B. 7) (leer = skip): ")
    score = _parse_int(input_score)
    if score is not None:
        kwargs["score"] = score

    input_score_min = input("wähle den min. Score (z.B. 6) (leer = skip): ")
    score_min = _parse_int(input_score_min)
    if score_min is not None:
        kwargs["score_min"] = score_min

    input_score_max = input("wähle den max. Score (z.B. 9) (leer = skip): ")
    score_max = _parse_int(input_score_max)
    if score_max is not None:
        kwargs["score_max"] = score_max

    input_condition_any = input("wähle den Zustand oder Zustände (OR) z.B. 'neu, gut' (leer = skip): ")
    condition_any = _split_terms(input_condition_any)
    if condition_any:
        kwargs["condition_any"] = condition_any

    # ✅ deine gewählte Beschreibung wird als description_contains genutzt
    input_name_contains = input("suche nach namen (AND, nur name) z.B. 'hoodie oversized' (leer = skip): ")
    name_contains = _split_terms(input_name_contains)
    if name_contains:
        kwargs["name_contains"] = name_contains

    input_description_contains = input("suche nach beschreibungen (AND, nur description) z.B. 'baumwolle' (leer = skip): ")
    description_contains = _split_terms(input_description_contains)
    if description_contains:
        kwargs["description_contains"] = description_contains

    input_text_all = input("jeder Term muss in name ODER description vorkommen (AND) z.B. 'hoodie wolle' (leer = skip): ")
    text_all = _split_terms(input_text_all)
    if text_all:
        kwargs["text_all"] = text_all

    input_text_any = input("mindestens ein Term muss in name ODER description vorkommen (OR) z.B. 'hoodie, wolle' (leer = skip): ")
    text_any = _split_terms(input_text_any)
    if text_any:
        kwargs["text_any"] = text_any

    input_limit = input("wähle ein Limit der Items (z.B. 20) (leer = skip): ")
    limit = _parse_int(input_limit)
    if limit is not None:
        kwargs["limit"] = limit

    return kwargs


