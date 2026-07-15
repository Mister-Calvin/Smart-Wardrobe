# Smart Wardrobe

Smart Wardrobe is an AI-powered wardrobe management system developed as a capstone project in Software Engineering and AI Engineering. The application combines a traditional web app for managing clothing items with a retrieval and LLM pipeline that creates specific outfit recommendations from the existing wardrobe.

The project demonstrates not only CRUD functionality, but also the use of embeddings, vector search, structured LLM responses, guardrails against hallucinations, and a small agent logic for context-dependent styling guidance.

## Project idea

Many outfit recommendation systems suggest generic clothing. Smart Wardrobe instead works with the user's actual clothing items. An outfit may only contain items that exist in the database.

The user can:

- Create, edit, delete, and view clothing items in the digital wardrobe
- Enter outfit requests with context, e.g. occasion, weather, season, location, and mood
- Filter the wardrobe before the AI selection, e.g. by color, score, condition, or text search
- Receive AI-generated outfit recommendations based on semantically matching wardrobe items

## Core features

- FastAPI web application with Jinja2 templates
- Digital wardrobe UI with categories, item cards, and responsive styling
- CRUD for clothing items, including automatic embedding updates on create and update
- PostgreSQL data model with SQLAlchemy ORM
- pgvector column for 1536-dimensional OpenAI embeddings
- Embedding generation with `text-embedding-3-small`
- Semantic similarity search via `embedding <-> query_vector`
- Dynamic database filters for colors, score, condition, name, description, and free text
- OpenAI Responses API with structured Pydantic output
- Prompt and schema design for exactly three outfit recommendations
- Validation of the LLM response against allowed item IDs
- Retry mechanism for invalid or hallucinated LLM responses
- LangGraph-based agent logic for weather, occasion, and mood guidance
- JSON debug artifacts for pipeline traceability

## AI pipeline

Outfit generation is structured as a multi-stage pipeline:

1. The user sends an outfit request via `/input`.
2. Context data such as weather, occasion, and mood is passed to a LangGraph state graph.
3. The agent creates rule-based `style_hints`, e.g. waterproof shoes for rain or neutral colors for a minimalist style.
4. Structured filters first reduce the possible database items.
5. A query text is built from the user request, context, and `style_hints`.
6. The query text is converted into a vector with OpenAI embeddings.
7. PostgreSQL/pgvector searches the filtered candidate pool for the semantically most suitable clothing items.
8. The LLM receives only these candidates plus an `allowed_ids` list.
9. The OpenAI Responses API generates a typed response according to a Pydantic schema.
10. The application checks whether all used IDs are actually contained in `allowed_ids`.
11. If the response is valid, the IDs are resolved back into item names and rendered as an outfit recommendation.

Short form:

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

## Guardrails against LLM hallucinations

An important part of the project is that the LLM is not allowed to freely invent clothing. Several safeguards were implemented for this purpose:

- The model receives only a reduced candidate list of real database items.
- Each outfit must use only IDs from `allowed_ids`.
- The response is parsed with Pydantic into a fixed JSON schema.
- After the response, all used IDs are collected and validated against `allowed_ids`.
- If IDs are hallucinated, generation is repeated up to three times.
- If too few suitable items are available, a dedicated domain exception is raised.

## Data model

The central table is `wardrobe`.

| Field | Meaning |
| --- | --- |
| `id` | Primary key |
| `name` | Name of the clothing item |
| `description` | Description, material, cut, or distinctive features |
| `color` | Color or color combination |
| `condition` | Condition, e.g. new, good, very good |
| `type` | Category, e.g. hoodie, trousers, shoes, coat |
| `score` | Personal rating or relevance |
| `embedding` | pgvector embedding for semantic search |

## Web routes

| Route | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Wardrobe view with all items |
| `/json` | GET | Output of all wardrobe items as JSON |
| `/items/create` | GET/POST | Create a clothing item |
| `/items/{item_id}/edit` | GET/POST | Edit a clothing item |
| `/items/{item_id}/delete` | POST | Delete a clothing item |
| `/input` | GET/POST | Enter an outfit request, context, and filters |

## Project structure

```text
.
├── fast_api.py              # FastAPI app, routes, templates, error handlers
├── models.py                # SQLAlchemy model, DB session, seed data
├── data_manager.py          # CRUD logic and embedding updates for items
├── db_filters.py            # Dynamic SQL filters for the candidate pool
├── data_into_vector.py      # Query text -> OpenAI embedding
├── similarity_search.py     # pgvector similarity search
├── openai_model.py          # LLM call, Pydantic schema, allowed_ids validation
├── main.py                  # Orchestration, retry logic, domain exceptions
├── agentic_ai.py            # LangGraph state graph for style hints
├── extend_llm_answer.py     # Resolve IDs into readable item names
├── create_embedding_data.py # Batch generation of missing embeddings
├── json_manager.py          # Helper functions for debug JSON
├── templates/               # Jinja2 pages
└── static/style.css         # Responsive wardrobe UI
```

Some JSON files in the repository are debug snapshots from the pipeline, e.g. filtered IDs, similarity search results, LLM payloads, and validated responses. They make the intermediate steps of the AI pipeline traceable.

## Technology stack

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

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn jinja2 python-multipart sqlalchemy psycopg2-binary python-dotenv pgvector langchain-openai openai pydantic langgraph typing-extensions
```

### 3. Set environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
POSTGRESQL_KEY=postgresql+psycopg2://postgres:your_password@localhost:5432/wardrobe
POSTGRESQL_KEY_ONLY=your_password
```

Note: The direct `psycopg2` helpers currently assume `dbname=wardrobe` and `user=postgres`. If a different database name or user is used, `db_filters.py` and `similarity_search.py` must be adjusted accordingly.

### 4. Prepare the PostgreSQL database

```bash
createdb wardrobe
psql -d wardrobe -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 5. Create tables

```bash
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

### 6. Insert seed data

Run only on an empty database:

```bash
python -c "from models import create_item, create_item_colorful_50, create_item_weather_50; create_item(); create_item_colorful_50(); create_item_weather_50()"
```

### 7. Generate embeddings

```bash
python -c "from create_embedding_data import create_embedding_column_and_seed_data; create_embedding_column_and_seed_data()"
```

### 8. Start the app

```bash
uvicorn fast_api:app --reload
```

The app is then available at:

```text
http://127.0.0.1:8000
```

## Example workflow

1. Create a clothing item in the web frontend.
2. When it is saved, an embedding is calculated automatically for this item.
3. Enter a request under `/input`, e.g. "What can I wear to a meeting in the rain?"
4. Optionally set filters, e.g. only black or highly rated clothing.
5. The app searches the wardrobe for semantically matching items.
6. The LLM creates three specific outfit recommendations from items that actually exist.
7. The response is validated and displayed with readable item names.

## What this project demonstrates

This project demonstrates practical skills in several areas:

- Backend development with FastAPI, routing, form processing, and error handling
- Data modeling with SQLAlchemy and PostgreSQL
- CRUD architecture with a clean separation between the web layer and data access
- AI engineering with embeddings, vector search, and LLM orchestration
- Retrieval-augmented generation on custom data
- Prompt engineering and structured model responses
- Pydantic schemas for validatable AI outputs
- Guardrails to reduce hallucinations
- Agentic AI fundamentals with LangGraph state management
- Debugging and traceability through stored pipeline artifacts
- Frontend fundamentals with Jinja2, HTML, and responsive CSS

## Project status

Smart Wardrobe is a functional prototype for a capstone project. The core idea has been implemented: The user manages real clothing items, and the AI creates context-aware, validated outfit recommendations from them.

Possible next stages:

- Authentication and user-specific wardrobes
- Upload of clothing images and vision-based attribute recognition
- Tests for filter logic, LLM validation, and API routes
- Deployment with Docker
- UI improvements for the outfit input and response page
- Persistent chat functionality for iteratively adjusting outfits
