# Smart Wardrobe

Smart Wardrobe ist ein AI-gestuetztes Wardrobe-Management-System als Abschlussprojekt im Bereich Software Engineering und AI Engineering. Die Anwendung kombiniert eine klassische Web-App zur Verwaltung von Kleidungsstuecken mit einer Retrieval- und LLM-Pipeline, die aus dem vorhandenen Kleiderschrank konkrete Outfit-Vorschlaege erstellt.

Das Projekt zeigt nicht nur CRUD-Funktionalitaet, sondern auch den Einsatz von Embeddings, Vektor-Suche, strukturierten LLM-Antworten, Guardrails gegen Halluzinationen und einer kleinen Agentenlogik fuer kontextabhaengige Styling-Hinweise.

## Projektidee

Viele Outfit-Recommendation-Systeme schlagen generische Kleidung vor. Smart Wardrobe arbeitet dagegen mit den tatsaechlich vorhandenen Kleidungsstuecken des Users. Ein Outfit darf nur Items enthalten, die in der Datenbank existieren.

Der User kann:

- Kleidungsstuecke erfassen, bearbeiten, loeschen und im digitalen Kleiderschrank ansehen
- Outfitwuensche mit Kontext eingeben, z. B. Anlass, Wetter, Saison, Location und Stimmung
- den Kleiderschrank vor der AI-Auswahl filtern, z. B. nach Farbe, Score, Zustand oder Textsuche
- AI-generierte Outfit-Vorschlaege erhalten, die auf semantisch passenden Wardrobe-Items basieren

## Kernfunktionen

- FastAPI-Webanwendung mit Jinja2-Templates
- Digitale Kleiderschrank-UI mit Kategorien, Item-Cards und responsivem Styling
- CRUD fuer Kleidungsstuecke inklusive automatischer Embedding-Aktualisierung bei Create und Update
- PostgreSQL-Datenmodell mit SQLAlchemy ORM
- pgvector-Spalte fuer 1536-dimensionale OpenAI-Embeddings
- Embedding-Erstellung mit `text-embedding-3-small`
- Semantische Aehnlichkeitssuche ueber `embedding <-> query_vector`
- Dynamische Datenbankfilter fuer Farben, Score, Zustand, Name, Beschreibung und Freitext
- OpenAI Responses API mit strukturiertem Pydantic-Output
- Prompt- und Schema-Design fuer genau drei Outfit-Vorschlaege
- Validierung der LLM-Antwort gegen erlaubte Item-IDs
- Retry-Mechanismus bei ungueltigen oder halluzinierten LLM-Antworten
- LangGraph-basierte Agentenlogik fuer Wetter-, Anlass- und Mood-Hinweise
- JSON-Debug-Artefakte zur Nachvollziehbarkeit der Pipeline

## AI-Pipeline

Die Outfit-Erstellung ist als mehrstufige Pipeline aufgebaut:

1. Der User sendet einen Outfitwunsch ueber `/input`.
2. Kontextdaten wie Wetter, Anlass und Stimmung werden an einen LangGraph-State-Graph uebergeben.
3. Der Agent erzeugt daraus regelbasierte `style_hints`, z. B. wasserfeste Schuhe bei Regen oder neutrale Farben bei minimalistischem Stil.
4. Strukturierte Filter reduzieren zuerst die moeglichen Datenbank-Items.
5. Aus Userwunsch, Kontext und `style_hints` wird ein Query-Text gebaut.
6. Der Query-Text wird mit OpenAI Embeddings in einen Vektor umgewandelt.
7. PostgreSQL/pgvector sucht die semantisch passendsten Kleidungsstuecke aus dem gefilterten Kandidatenpool.
8. Das LLM bekommt nur diese Kandidaten plus eine `allowed_ids`-Liste.
9. Die OpenAI Responses API erzeugt eine typisierte Antwort nach Pydantic-Schema.
10. Die Anwendung prueft, ob alle verwendeten IDs wirklich in `allowed_ids` enthalten sind.
11. Wenn die Antwort valide ist, werden die IDs wieder in Item-Namen aufgeloest und als Outfit-Vorschlag gerendert.

Kurzform:

```text
User Input
  -> Context + LangGraph style_hints
  -> SQL Filter
  -> OpenAI Embedding
  -> pgvector Similarity Search
  -> Candidate Whitelist
  -> Structured LLM Output
  -> Hallucination Check
  -> Rendered Outfit Answer
```

## Guardrails gegen LLM-Halluzinationen

Ein wichtiger Teil des Projekts ist, dass das LLM nicht frei Kleidung erfinden darf. Dafuer wurden mehrere Schutzmechanismen eingebaut:

- Das Modell erhaelt nur eine reduzierte Kandidatenliste aus realen Datenbank-Items.
- Jedes Outfit muss ausschliesslich IDs aus `allowed_ids` verwenden.
- Die Antwort wird mit Pydantic in ein festes JSON-Schema geparst.
- Nach der Antwort werden alle verwendeten IDs gesammelt und gegen `allowed_ids` validiert.
- Bei halluzinierten IDs wird die Erstellung bis zu drei Mal wiederholt.
- Wenn zu wenige passende Items vorhanden sind, wird eine eigene Domain-Exception ausgeloest.

## Datenmodell

Die zentrale Tabelle ist `wardrobe`.

| Feld | Bedeutung |
| --- | --- |
| `id` | Primaerschluessel |
| `name` | Name des Kleidungsstuecks |
| `description` | Beschreibung, Material, Schnitt oder Besonderheiten |
| `color` | Farbe oder Farbkombination |
| `condition` | Zustand, z. B. neu, gut, sehr gut |
| `type` | Kategorie, z. B. hoodie, hose, schuhe, mantel |
| `score` | persoenliche Bewertung oder Relevanz |
| `embedding` | pgvector-Embedding fuer semantische Suche |

## Web-Routen

| Route | Methode | Zweck |
| --- | --- | --- |
| `/` | GET | Kleiderschrank-Ansicht mit allen Items |
| `/json` | GET | Ausgabe aller Wardrobe-Items als JSON |
| `/items/create` | GET/POST | Kleidungsstueck anlegen |
| `/items/{item_id}/edit` | GET/POST | Kleidungsstueck bearbeiten |
| `/items/{item_id}/delete` | POST | Kleidungsstueck loeschen |
| `/input` | GET/POST | Outfitwunsch, Kontext und Filter eingeben |

## Projektstruktur

```text
.
├── fast_api.py              # FastAPI-App, Routen, Templates, Error Handler
├── models.py                # SQLAlchemy-Modell, DB-Session, Seed-Daten
├── data_manager.py          # CRUD-Logik und Embedding-Updates fuer Items
├── db_filters.py            # Dynamische SQL-Filter fuer den Kandidatenpool
├── data_into_vector.py      # Query-Text -> OpenAI Embedding
├── similarity_search.py     # pgvector Similarity Search
├── openai_model.py          # LLM-Aufruf, Pydantic-Schema, allowed_ids-Validierung
├── main.py                  # Orchestrierung, Retry-Logik, Domain-Exceptions
├── agentic_ai.py            # LangGraph-State-Graph fuer Style-Hints
├── extend_llm_answer.py     # Aufloesen von IDs zu lesbaren Item-Namen
├── create_embedding_data.py # Batch-Erstellung fehlender Embeddings
├── json_manager.py          # Hilfsfunktionen fuer Debug-JSON
├── templates/               # Jinja2-Seiten
└── static/style.css         # Responsive Wardrobe-UI
```

Einige JSON-Dateien im Repository sind Debug-Snapshots aus der Pipeline, z. B. gefilterte IDs, Similarity-Search-Ergebnisse, LLM-Payloads und validierte Antworten. Sie machen die Zwischenschritte der AI-Pipeline nachvollziehbar.

## Technologie-Stack

- Python
- FastAPI
- Jinja2
- SQLAlchemy
- PostgreSQL
- pgvector
- psycopg2
- OpenAI API
- LangChain OpenAI Embeddings
- LangGraph
- Pydantic
- HTML/CSS

## Setup

### 1. Virtuelle Umgebung erstellen

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Dependencies installieren

```bash
pip install fastapi uvicorn jinja2 python-multipart sqlalchemy psycopg2-binary python-dotenv pgvector langchain-openai openai pydantic langgraph typing-extensions
```

### 3. Environment Variablen setzen

Lege eine `.env`-Datei an:

```env
OPENAI_API_KEY=your_openai_api_key
POSTGRESQL_KEY=postgresql+psycopg2://postgres:your_password@localhost:5432/wardrobe
POSTGRESQL_KEY_ONLY=your_password
```

Hinweis: Die direkten `psycopg2`-Helper gehen aktuell von `dbname=wardrobe` und `user=postgres` aus. Wenn ein anderer Datenbankname oder User verwendet wird, muessen `db_filters.py` und `similarity_search.py` entsprechend angepasst werden.

### 4. PostgreSQL-Datenbank vorbereiten

```bash
createdb wardrobe
psql -d wardrobe -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 5. Tabellen erstellen

```bash
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

### 6. Seed-Daten einfuegen

Nur auf einer leeren Datenbank ausfuehren:

```bash
python -c "from models import create_item, create_item_colorful_50, create_item_weather_50; create_item(); create_item_colorful_50(); create_item_weather_50()"
```

### 7. Embeddings erzeugen

```bash
python -c "from create_embedding_data import create_embedding_column_and_seed_data; create_embedding_column_and_seed_data()"
```

### 8. App starten

```bash
uvicorn fast_api:app --reload
```

Danach ist die App erreichbar unter:

```text
http://127.0.0.1:8000
```

## Beispielablauf

1. Ein Kleidungsstueck im Web-Frontend anlegen.
2. Beim Speichern wird automatisch ein Embedding fuer dieses Item berechnet.
3. Unter `/input` einen Wunsch eingeben, z. B. "Was kann ich fuer ein Meeting bei Regen anziehen?"
4. Optional Filter setzen, z. B. nur schwarze oder gut bewertete Kleidung.
5. Die App sucht semantisch passende Items im Kleiderschrank.
6. Das LLM erstellt drei konkrete Outfit-Vorschlaege aus real vorhandenen Items.
7. Die Antwort wird validiert und mit lesbaren Item-Namen angezeigt.

## Was dieses Projekt demonstriert

Dieses Projekt zeigt praktische Faehigkeiten in mehreren Bereichen:

- Backend-Entwicklung mit FastAPI, Routing, Formularverarbeitung und Error Handling
- Datenmodellierung mit SQLAlchemy und PostgreSQL
- CRUD-Architektur mit sauberer Trennung zwischen Web-Layer und Datenzugriff
- AI Engineering mit Embeddings, Vektor-Suche und LLM-Orchestrierung
- Retrieval-Augmented Generation auf eigenen Daten
- Prompt Engineering und strukturierte Modellantworten
- Pydantic-Schemas fuer validierbare AI-Ausgaben
- Guardrails zur Reduktion von Halluzinationen
- Agentic-AI-Grundlagen mit LangGraph-State-Management
- Debugging und Nachvollziehbarkeit durch gespeicherte Pipeline-Artefakte
- Frontend-Grundlagen mit Jinja2, HTML und responsivem CSS

## Projektstatus

Smart Wardrobe ist ein funktionsfaehiger Prototyp fuer ein Abschlussprojekt. Die Kernidee ist umgesetzt: Der User verwaltet reale Kleidungsstuecke, und die AI erstellt daraus kontextbezogene, validierte Outfit-Vorschlaege.

Moegliche naechste Ausbaustufen:

- Authentifizierung und User-spezifische Kleiderschraenke
- Upload von Kleidungsbildern und Vision-basierte Attributerkennung
- Tests fuer Filterlogik, LLM-Validierung und API-Routen
- Deployment mit Docker
- UI-Verbesserungen fuer den Outfit-Input und die Antwortseite
- Persistente Chat-Funktion zum iterativen Anpassen von Outfits
