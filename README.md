# Smart Wardrobe

Smart Wardrobe is a local AI-powered wardrobe application that generates context-aware outfit suggestions using only clothing items that actually exist in the database.

The project combines a FastAPI CRUD application with provider-specific embeddings, PostgreSQL vector search, structured LLM responses, validation guardrails, and a rule-based LangGraph workflow.

> **Status:** Functional local prototype and portfolio project.  
> The Gemini workflow has been manually verified end to end. An isolated OpenAI workflow remains available as an optional compatibility path.

## Project idea

Generic fashion assistants can recommend clothing that the user does not own. Smart Wardrobe instead works with a real digital wardrobe stored in PostgreSQL.

Users can:

- Create, view, update, and delete wardrobe items
- Select Gemini or OpenAI on the landing page
- Enter an outfit request with event, location, season, weather, and mood
- Restrict the wardrobe using structured filters
- Receive three outfit suggestions assembled from real wardrobe IDs
- See the selected IDs resolved back into readable clothing names

The LLM never receives the complete database. It receives only a compact, preselected candidate pool to reduce token usage and limit hallucinations.

## Feature highlights

- FastAPI backend with Jinja2 templates
- Responsive wardrobe interface
- Complete CRUD flow for clothing items
- Explicit Gemini or OpenAI provider selection
- Signed browser session for the selected provider
- No hidden default provider
- PostgreSQL database with SQLAlchemy
- pgvector-based semantic similarity search
- Provider-specific item and query embeddings
- Automatic embedding creation and updates for the selected provider
- Transactional item and embedding writes
- SQL filters applied before vector retrieval
- Rule-based LangGraph styling hints
- Provider-neutral retrieval preferences
- Category-balanced Gemini candidate selection
- Adaptive Gemini retrieval fallback
- Token-reduced candidate payloads
- Structured Pydantic model output
- Authoritative `allowed_ids` validation
- Category and outfit-slot validation
- Dress and top/bottom structure validation
- Validation of three unique outfit bases
- Retry handling for invalid model output
- Resolution of generated IDs back to wardrobe names

## Provider architecture

The provider is selected on the landing page and stored in the signed browser session as either `gemini` or `openai`.

The same selected provider controls:

1. Item embedding creation
2. Item embedding updates
3. Outfit-request embeddings
4. Vector similarity search
5. LLM outfit generation

API keys are never stored in the browser session. They remain server-side in `.env`.

```text
Landing page
    |
    v
POST /provider
    |
    v
Signed session: "gemini" or "openai"
    |
    +---------------- CRUD request ----------------+
    |                                               |
    |                                               v
    |                                         DataManager
    |                                               |
    |                                               v
    |                                  Embedding writer router
    |                                               |
    |                              +----------------+----------------+
    |                              |                                 |
    |                              v                                 v
    |                    Gemini embedding                   OpenAI embedding
    |                              |                                 |
    |                              v                                 v
    |          wardrobe_gemini_embeddings              wardrobe.embedding
    |
    +--------------- Outfit request ----------------+
                                                    |
                                                    v
                                           Provider router
                                                    |
                              +---------------------+--------------------+
                              |                                          |
                              v                                          v
                       Gemini pipeline                             OpenAI pipeline
```

Gemini and OpenAI vectors are deliberately stored separately. A Gemini query vector is never compared with an OpenAI item vector, or vice versa.

## Provider comparison

| Area | Gemini | OpenAI |
| --- | --- | --- |
| Current role | Primary verified workflow | Optional compatibility workflow |
| Generation model | Configured through `GEMINI_GENERATION_MODEL` | `gpt-4o-mini` |
| Embedding model | Configured through `GEMINI_EMBEDDING_MODEL` | `text-embedding-3-small` |
| Vector dimensions | Configured through `GEMINI_EMBEDDING_DIMENSIONS` | 1536 |
| Vector storage | `wardrobe_gemini_embeddings` | `wardrobe.embedding` |
| Similarity retrieval | Balanced candidates with adaptive fallback | Existing top-30 similarity flow |
| Candidate payload | ID, name, color, normalized category | ID, name, color, original type |
| Validation | IDs, categories, slots, outfit structure, unique bases | Allowed-ID validation |
| Retry behavior | Up to three invalid generations | Up to three invalid generations |

The providers are intentionally isolated and do not currently have identical capabilities.

Provider availability, model access, pricing, and free-tier quotas are controlled by the external API providers and may change.

## Gemini outfit pipeline

The primary Gemini flow uses the following stages:

1. The browser sends an outfit request to `/input`.
2. SQL filters create a hard list of permitted wardrobe IDs.
3. A rule-based LangGraph workflow derives styling hints from weather, event, and mood.
4. The workflow derives provider-neutral retrieval priorities.
5. Internal retrieval controls are separated from the data sent to Gemini.
6. One Gemini query embedding is generated.
7. Similarity search joins wardrobe items only with matching Gemini embeddings.
8. Results are categorized into tops, bottoms, dresses, shoes, outerwear, headwear, socks, bags, and accessories.
9. Category-based round-robin selection creates a balanced candidate pool.
10. The pool is checked for shoes and at least three viable outfit bases.
11. If necessary, similarity search is expanded while preserving the original hard filters.
12. At most 20 candidates are reduced to ID, name, color, and normalized category.
13. Gemini receives the compact candidates and the authoritative `allowed_ids`.
14. Pydantic requires exactly three structured outfits.
15. The response is validated for allowed IDs, correct categories, valid slots, dress structure, and unique outfit bases.
16. Invalid responses are retried up to three times.
17. Valid IDs are resolved to wardrobe names in one database query.
18. The readable outfit recommendations are rendered in the browser.

Short form:

```text
User request
    -> SQL filters
    -> LangGraph styling and retrieval hints
    -> Gemini query embedding
    -> Gemini pgvector search
    -> Balanced candidate retrieval
    -> Adaptive fallback if required
    -> Compact candidate whitelist
    -> Structured Gemini output
    -> ID, category, and structure validation
    -> Retry when invalid
    -> Resolve IDs to wardrobe names
    -> Rendered answer
```

## Guardrails and token efficiency

Smart Wardrobe does not allow the LLM to freely invent clothing.

The Gemini flow uses several safeguards:

- Only real database candidates are sent to the model.
- The candidate payload excludes unnecessary database fields.
- Every candidate has an authoritative database ID.
- The model may only use IDs from `allowed_ids`.
- Each ID must appear in a compatible outfit slot.
- A dress cannot also have a separate bottom.
- A normal top requires a bottom.
- Three valid and unique base combinations are required.
- The response must match a Pydantic schema.
- Invalid responses are rejected and retried.
- Item names are loaded from the database after validation.

These checks reduce hallucinations, but they do not guarantee that every external model response will be valid.

## Data model

### `wardrobe`

The central table stores clothing metadata and the optional OpenAI vector.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `name` | Clothing item name |
| `description` | Material, cut, or other details |
| `color` | Color or color combination |
| `condition` | Current condition |
| `type` | Original wardrobe category |
| `score` | Personal rating |
| `embedding` | Nullable 1536-dimensional OpenAI vector |

### `wardrobe_gemini_embeddings`

Gemini embeddings are stored in a dedicated table.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `wardrobe_id` | Foreign key to `wardrobe.id` |
| `model` | Gemini embedding model |
| `dimensions` | Vector dimensions |
| `embedding` | Gemini vector |

The combination of `wardrobe_id`, `model`, and `dimensions` is unique.

Deleting a wardrobe item also deletes its Gemini embedding through `ON DELETE CASCADE`.

## Web routes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/` | Display the wardrobe and provider selection |
| `POST` | `/provider` | Store the selected provider in the session |
| `GET` | `/json` | Return all wardrobe items as JSON |
| `GET` | `/items/create` | Display the create-item form |
| `POST` | `/items/create` | Create an item and its selected-provider embedding |
| `GET` | `/items/{item_id}/edit` | Display the update form |
| `POST` | `/items/{item_id}/edit` | Update the item and selected-provider embedding |
| `POST` | `/items/{item_id}/delete` | Delete an item |
| `GET` | `/input` | Display the outfit request form |
| `POST` | `/input` | Filter items and run the selected AI pipeline |

## Project structure

```text
.
├── ai_models/
│   ├── embedding_writer_router.py
│   ├── provider_router.py
│   ├── provider_session.py
│   │
│   ├── shared/
│   │   ├── balanced_candidate_retrieval.py
│   │   ├── candidate_pool_validation.py
│   │   ├── item_category_mapper.py
│   │   └── retrieval_preferences.py
│   │
│   ├── gemini/
│   │   ├── gemini_client.py
│   │   ├── gemini_embedding_model.py
│   │   ├── item_embedding_gemini.py
│   │   ├── item_embedding_writer_gemini.py
│   │   ├── create_embedding_data_gemini.py
│   │   ├── query_embedding_gemini.py
│   │   ├── similarity_search_gemini.py
│   │   ├── adaptive_candidate_retrieval_gemini.py
│   │   ├── candidate_preparation_gemini.py
│   │   ├── outfit_schema_gemini.py
│   │   ├── outfit_prompt_gemini.py
│   │   ├── outfit_generation_gemini.py
│   │   ├── outfit_response_validation_gemini.py
│   │   ├── outfit_retry_gemini.py
│   │   ├── outfit_pipeline_gemini.py
│   │   ├── outfit_answer_gemini.py
│   │   └── main_gemini.py
│   │
│   └── openai/
│       ├── data_into_vector.py
│       ├── similarity_search.py
│       ├── openai_model.py
│       ├── extend_llm_answer.py
│       ├── main.py
│       ├── item_embedding_openai.py
│       ├── item_embedding_writer_openai.py
│       └── create_embedding_data.py
│
├── scripts/
│   └── bootstrap_database.py
├── templates/
├── static/
├── agentic_ai.py
├── data_manager.py
├── db_filters.py
├── fast_api.py
├── json_manager.py
├── models.py
├── requirements.txt
└── .env.example
```

The Gemini implementation lives in `ai_models/gemini/`, while the OpenAI implementation lives in `ai_models/openai/`.

The `shared` package contains provider-neutral retrieval logic. Provider-specific API calls, embeddings, searches, prompts, and response handling remain inside their own packages.

## Technology stack

- Python 3.13
- FastAPI
- Uvicorn
- Jinja2
- Starlette sessions
- SQLAlchemy
- PostgreSQL
- pgvector
- psycopg2
- Google Gen AI SDK
- OpenAI SDK
- LangChain OpenAI Embeddings
- LangGraph
- Pydantic
- HTML and CSS

## Local setup

The documented quick start uses Gemini. OpenAI is optional.

### Prerequisites

The project was developed and tested locally with:

- Python 3.13
- PostgreSQL 16
- The server-side PostgreSQL `vector` extension
- A Gemini API key

An OpenAI API key is required only when using the OpenAI provider.

The Python package named `pgvector` does not install the PostgreSQL server extension. The extension must also be installed for the PostgreSQL server.

### 1. Clone the repository

```bash
git clone https://github.com/Mister-Calvin/Smart-Wardrobe.git
cd Smart-Wardrobe
```

### 2. Create and activate a virtual environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

### 4. Create the PostgreSQL database

For the default PostgreSQL user:

```bash
createdb -U postgres wardrobe
```

Alternatively:

```bash
psql -U postgres -c "CREATE DATABASE wardrobe;"
```

The local PostgreSQL username may be different. The username and database name must match the later `DATABASE_URL`.

### 5. Configure the environment

Create the local configuration file:

```bash
cp .env.example .env
```

Generate a random session secret:

```bash
openssl rand -hex 32
```

Open `.env` and configure the values:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/wardrobe

SESSION_SECRET=PASTE_YOUR_GENERATED_SESSION_SECRET_HERE

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_GENERATION_MODEL=gemini-3.1-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
GEMINI_EMBEDDING_DIMENSIONS=1536

OPENAI_API_KEY=YOUR_OPENAI_API_KEY_IF_USED
```

Database URL format:

```text
postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE
```

Characters such as `@`, `:`, `/`, or `#` inside a database password must be URL-encoded.

The same `DATABASE_URL` is used by SQLAlchemy and the direct psycopg2 queries.

Never commit `.env`. It contains local credentials and is excluded by `.gitignore`.

### 6. Bootstrap the database schema

Run:

```bash
python -m scripts.bootstrap_database
```

The bootstrap command:

- Connects to the existing database from `DATABASE_URL`
- Enables the `vector` extension if necessary
- Registers the wardrobe and Gemini embedding models
- Creates missing tables
- Preserves existing wardrobe rows
- Can be run repeatedly

It does not:

- Install PostgreSQL
- Install the server-side pgvector extension
- Create the database or database user
- Insert seed data
- Update existing columns like a migration system
- Delete or overwrite wardrobe items

The database user must have permission to enable the `vector` extension.

### 7. Add optional demonstration data

The outfit pipeline needs several different tops, bottoms or dresses, and shoes.

For a fresh, empty database, the existing demonstration data can be inserted with:

```bash
python - <<'PY'
from models import (
    create_item,
    create_item_colorful_50,
    create_item_weather_50,
)

create_item()
create_item_colorful_50()
create_item_weather_50()

print("Demo wardrobe created.")
PY
```

Run this command only once on an empty database. The seed functions do not detect duplicate rows and do not create embeddings.

### 8. Generate missing Gemini embeddings

For a rate-limit-friendly batch:

```bash
python - <<'PY'
from ai_models.gemini.create_embedding_data_gemini import (
    create_missing_gemini_embeddings,
)

created = create_missing_gemini_embeddings(
    limit=20
)

print("Created Gemini embeddings:", created)
PY
```

Repeat the command until every item has a matching Gemini embedding.

To process all currently missing items in one run, omit the limit:

```bash
python - <<'PY'
from ai_models.gemini.create_embedding_data_gemini import (
    create_missing_gemini_embeddings,
)

created = create_missing_gemini_embeddings()

print("Created Gemini embeddings:", created)
PY
```

Each completed embedding is committed separately. If an API quota or rate limit interrupts the process, wait according to the provider response and run the command again. Existing embeddings for the configured model and dimensions are skipped.

### 9. Start the application

```bash
python -m uvicorn fast_api:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Select Gemini on the landing page before opening the create, update, or outfit-request pages.

There is no automatically selected provider.

## Manual Gemini smoke test

A complete manual test can be performed as follows:

1. Open `http://127.0.0.1:8000`.
2. Select Gemini on the landing page.
3. Confirm that the wardrobe items are displayed.
4. Create a test item.
5. Confirm that the new item appears in the wardrobe.
6. Update its condition or score.
7. Confirm that the update is displayed.
8. Open the outfit request form.
9. Enter event, location, season, weather, and mood.
10. Use broad filters or leave the optional filters empty.
11. Submit the request.
12. Confirm that three readable outfits are returned.
13. Delete the test item.
14. Confirm that it and its Gemini embedding are removed.

The current project uses manual integration and end-to-end checks. A committed automated test suite has not yet been added.

## Optional OpenAI setup

The OpenAI implementation remains available under `ai_models/openai/`.

To use it:

1. Add a valid `OPENAI_API_KEY` to `.env`.
2. Generate missing OpenAI embeddings.
3. Select OpenAI on the landing page.

Generate missing OpenAI embeddings with:

```bash
python - <<'PY'
from ai_models.openai.create_embedding_data import (
    create_embedding_column_and_seed_data,
)

create_embedding_column_and_seed_data(
    batch_size=50
)
PY
```

OpenAI embeddings are stored in `wardrobe.embedding`. They do not reuse Gemini vectors.

## Important embedding behavior

Creating or updating an item writes only the embedding belonging to the provider currently selected in the browser session.

For example:

- Creating an item with Gemini creates a Gemini embedding but no OpenAI embedding.
- Creating an item with OpenAI creates an OpenAI embedding but no Gemini embedding.
- Updating an item with Gemini refreshes only its Gemini embedding.
- Updating an item with OpenAI refreshes only its OpenAI embedding.

The backfill commands create only missing embeddings. They do not automatically refresh an existing embedding that became stale after the item was edited using the other provider.

If both providers must remain fully synchronized, the item currently has to be updated once with each provider or a dedicated cross-provider refresh command must be added.

## Development diagnostics

Some application paths write intermediate JSON diagnostics locally, including filtered IDs, provider payloads, vector-search results, and model responses.

These files:

- Are runtime development artifacts
- Are ignored by Git
- May contain user prompts or wardrobe information
- Should not be committed to GitHub

## What this project demonstrates

Smart Wardrobe demonstrates practical knowledge in:

- Backend development with FastAPI
- Server-side HTML rendering with Jinja2
- Form handling and HTTP routing
- SQLAlchemy data modeling and transactions
- PostgreSQL and pgvector
- Dynamic SQL filtering
- Embedding generation and vector similarity search
- Retrieval-augmented LLM workflows
- Multi-provider software architecture
- Provider routing and dependency isolation
- Token-conscious model input design
- Pydantic structured responses
- LLM output validation and retry strategies
- Hallucination reduction through candidate whitelists
- Category-aware retrieval
- Rule-based LangGraph state workflows
- Signed browser sessions
- Secure environment configuration
- Reproducible local project setup
- Git-based incremental refactoring

## Current limitations

Smart Wardrobe is a local prototype and is not production-ready.

Current limitations include:

- No authentication or user-specific wardrobes
- All browser sessions use the same database wardrobe
- No automated test suite or CI pipeline
- No Alembic database migrations
- No Docker or deployment configuration
- No clothing image upload or computer-vision analysis
- No persistent chat workflow
- OpenAI does not yet have every Gemini retrieval and validation feature
- Only the selected provider embedding is updated during create or edit
- External provider requests can fail because of quotas or rate limits
- Hard filters can still leave too few suitable clothing categories
- Session cookies are configured for local HTTP development
- Runtime diagnostic JSON files are still generated locally

## Possible next steps

- Add unit and integration tests
- Add route tests with a temporary test database
- Add Alembic migrations
- Add authentication and per-user wardrobes
- Add a command for refreshing both embedding providers
- Improve provider-specific error handling for rate limits
- Add clothing image upload and vision-based attribute extraction
- Add Docker and deployment configuration
- Add screenshots and a short demo video
- Add continuous integration
- Complete or remove the unfinished chat prototype