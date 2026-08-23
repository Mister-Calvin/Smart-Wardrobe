"""
Einfacher LangGraph-"Agent" für Outfit-Ideen (DE).

Verhalten:
- Benötigt: weather (Wetter), event_type (Anlass), mood (Stimmung/Stil)
- Wenn etwas fehlt -> Interrupt mit einer Frage
- Resume mit Command(resume=...) bis alles vorhanden ist
- Dann erzeugt er eine Outfit-Idee (regelbasiert, ohne LLM)

Installation:
  pip install -U langgraph

Start:
  python agentic_ai.py
"""

from typing_extensions import TypedDict, Optional, List, Literal, Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

from json_manager import wirte_json
import uuid
from ai_models.shared.item_category_mapper import (
    ItemCategory,
)
from ai_models.shared.retrieval_preferences import (
    build_retrieval_preferences,
)

# ----------------------------
# 1) State definieren
# ----------------------------
class OutfitState(TypedDict, total=False):
    weather: Optional[str]          # Wetter (Freitext)
    event_type: Optional[str]       # Anlass (Freitext)
    mood: Optional[str]             # Mood/Stil (Freitext)
    recommendation: str             # Finale Ausgabe (DE)
    style_hints: List[str]          # "Probier:"-Liste (DE) -> gut für Vector Query Expansion

    priority_categories: List[ItemCategory]
    category_limit_overrides: Dict[
        ItemCategory,
        int,
    ]


REQUIRED_FIELDS = ["weather", "event_type", "mood"]


# ----------------------------
# 2) Routing / Nodes
# ----------------------------
def route_missing(state: OutfitState) -> Literal["ask", "recommend"]:
    """
    Entscheidet, ob der Agent weiter nachfragen muss oder ob er schon
    eine Empfehlung erstellen kann.

    Wichtig: Router-Funktionen sollten den State NICHT mutieren.
    """
    missing = [k for k in REQUIRED_FIELDS if not state.get(k)]
    return "ask" if missing else "recommend"


def ask_for_one_missing(state: OutfitState) -> Dict[str, Any]:
    """
    Fragt genau EIN fehlendes Feld ab und pausiert per interrupt().
    Die Antwort kommt beim Resume (Command(resume=...)) zurück.
    """
    missing = [k for k in REQUIRED_FIELDS if not state.get(k)]
    if not missing:
        return {}

    field = missing[0]

    prompts = {
        "weather": "Wie ist das Wetter morgen? (z.B. sonnig, regnerisch, kalt, warm, windig)",
        "event_type": "Was ist der Anlass? (z.B. Arbeit, Büro, Date, Training, casual, formal)",
        "mood": "Welche Stimmung / welcher Stil? (z.B. gemütlich, minimalistisch, selbstbewusst, verspielt)",
    }

    payload = {"field": field, "question": prompts[field]}
    answer = interrupt(payload)
    return {field: str(answer).strip()}


def recommend_outfit(state: OutfitState) -> Dict[str, Any]:
    """
    Regelbasierte Outfit-Idee (Deutsch).
    Output:
      - recommendation: schöner Text
      - style_hints: Liste der "Probier:"-Bulletpoints (gut für similarity_search / Query-Expansion)

    """
    weather = (state.get("weather") or "").lower()
    event = (state.get("event_type") or "").lower()
    mood = (state.get("mood") or "").lower()

    pieces: List[str] = []

    # ----------------------------
    # Wetter-Regeln (DE Keywords)
    # ----------------------------
    # Regen
    if any(w in weather for w in ["regen", "regnerisch", "nass", "schauer", "sprühregen"]):
        pieces += ["eine wasserfeste Jacke", "wasserfeste/robuste Schuhe"]

    # Kalt / Schnee / Frost
    if any(w in weather for w in ["kalt", "kühl", "frost", "frostig", "schnee", "eisig", "frieren"]):
        pieces += ["ein warmer Mantel", "eine Strickschicht (Pullover/Hoodie)", "dickere Socken"]

    # Warm / Heiß / Schwül
    if any(w in weather for w in ["warm", "heiß", "hitze", "schwül"]):
        pieces += ["ein atmungsaktives Oberteil", "leichte Stoffe", "bequeme Sneaker oder Sandalen"]

    # Wind
    if any(w in weather for w in ["wind", "windig", "sturm", "stürmisch"]):
        pieces += ["eine winddichte Schicht (Windbreaker/leichte Jacke)"]

    # ----------------------------
    # Anlass-Regeln (DE Keywords)
    # ----------------------------
    # Arbeit / Büro
    if any(e in event for e in ["arbeit", "büro", "office", "meeting", "termin", "kunden"]):
        pieces += ["smart-casual Hose", "sauberes Hemd oder strukturiertes Top"]

    # Formal
    elif any(e in event for e in ["formal", "hochzeit", "gala", "anzug", "feierlich"]):
        pieces += ["ein schickes, gut sitzendes Outfit (Anzug/Kleid)", "elegante Schuhe"]

    # Sport / Training
    elif any(e in event for e in ["gym", "fitness", "training", "workout", "laufen", "joggen", "sport"]):
        pieces += ["Sportkleidung", "Trainingsschuhe"]

    # Date / Essen
    elif any(e in event for e in ["date", "dinner", "essen", "restaurant"]):
        pieces += ["ein ‘edles’ Teil (Jacke/Schuhe/Accessoire als Upgrade)"]

    # Default
    else:
        pieces += ["ein entspannter Casual-Look mit passenden schuhen, top und bottom"]

    # ----------------------------
    # Mood/Stil-Regeln (DE Keywords)
    # ----------------------------
    # Gemütlich / entspannt
    if any(m in mood for m in ["gemütlich", "comfy", "entspannt", "chillig", "cozy", "locker"]):
        pieces += ["weiche Materialien", "etwas weiterer Schnitt"]

    # Selbstbewusst / mutig
    if any(m in mood for m in ["selbstbewusst", "mutig", "bold", "auffällig", "statement"]):
        pieces += ["ein Statement-Piece (Farbe/Schnitt/Accessoire)"]

    # Minimalistisch / clean
    if any(m in mood for m in ["minimal", "minimalistisch", "clean", "schlicht", "basic"]):
        pieces += ["neutrale Farben", "klare Silhouette"]

    # Verspielt / fun
    if any(m in mood for m in ["verspielt", "fun", "bunt", "fröhlich", "spielerisch"]):
        pieces += ["ein Farbakzent", "ein verspieltes Accessoire"]

    # Dedupe (Reihenfolge behalten)
    seen = set()
    cleaned: List[str] = []
    for p in pieces:
        if p not in seen:
            cleaned.append(p)
            seen.add(p)

    style_hints = cleaned[:8]

    retrieval_preferences = (
        build_retrieval_preferences(
            weather=weather,
            event=event,
            mood=mood,
        )
    )

    rec = (
        "Outfit-Idee für morgen:\n"
        f"- Wetter: {state.get('weather')}\n"
        f"- Anlass: {state.get('event_type')}\n"
        f"- Stimmung/Stil: {state.get('mood')}\n\n"
        "Probier:\n- " + "\n- ".join(style_hints)
    )

    return {
        "recommendation": rec,
        "style_hints": style_hints,
        "priority_categories": (
            retrieval_preferences[
                "priority_categories"
            ]
        ),
        "category_limit_overrides": (
            retrieval_preferences[
                "category_limit_overrides"
            ]
        ),
    }


# ----------------------------
# 3) Graph bauen
# ----------------------------
builder = StateGraph(OutfitState)

builder.add_node("ask", ask_for_one_missing)
builder.add_node("recommend", recommend_outfit)

builder.add_conditional_edges(
    START,
    route_missing,
    {"ask": "ask", "recommend": "recommend"},
)
builder.add_conditional_edges(
    "ask",
    route_missing,
    {"ask": "ask", "recommend": "recommend"},
)

builder.add_edge("recommend", END)

memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)


# ----------------------------
# 4) CLI Runner (Human-in-the-loop)
# ----------------------------


def run_agent_from_payload(weather_input, event_input, mood_input, *, thread_id: str | None = None) -> OutfitState:
    initial_state: OutfitState = {
        "weather": weather_input or None,
        "event_type": event_input or None,
        "mood": mood_input or None,
    }

    for k in ["weather", "event_type", "mood"]:
        if initial_state.get(k) is not None:
            initial_state[k] = str(initial_state[k]).strip()  # type: ignore[assignment]

    tid = thread_id or f"outfit-{uuid.uuid4().hex}"
    thread = {"configurable": {"thread_id": tid}}

    result = graph.invoke(initial_state, config=thread)

    if "__interrupt__" in result:
        state_now = graph.get_state(
            thread
        ).values

        missing = [
            key
            for key in REQUIRED_FIELDS
            if not state_now.get(key)
        ]

        return {
            **state_now,
            "recommendation": (
                state_now.get(
                    "recommendation",
                    "",
                )
            ),
            "style_hints": (
                state_now.get(
                    "style_hints",
                    [],
                )
            ),
            "priority_categories": (
                state_now.get(
                    "priority_categories",
                    [],
                )
            ),
            "category_limit_overrides": (
                state_now.get(
                    "category_limit_overrides",
                    {},
                )
            ),
            "missing": missing,
        }
    return graph.get_state(thread).values


