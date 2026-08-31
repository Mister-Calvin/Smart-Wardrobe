"""Configure the FastAPI wardrobe and outfit application."""

import os
from pathlib import Path

from dotenv import load_dotenv

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
from starlette.middleware.sessions import (
    SessionMiddleware,
)

from agentic_ai import run_agent_from_payload
from data_manager import DataManager
from db_filters import (
    build_filter_kwargs_from_strings,
    filter_db_dynamic,
)
from ai_models.provider_router import (
    AIProviderGenerationError,
    AIProviderHallucinationError,
    AIProviderRequestError,
    UnknownAIProviderError,
    build_outfit_with_provider,
)
from ai_models.provider_session import (
    AIProviderNotSelectedError,
    get_selected_ai_provider,
    require_selected_ai_provider,
    set_selected_ai_provider,
)


ENV_PATH = (
    Path(__file__)
    .resolve()
    .with_name(".env")
)

load_dotenv(
    dotenv_path=ENV_PATH
)


SESSION_SECRET = os.getenv(
    "SESSION_SECRET"
)

if not SESSION_SECRET:
    raise RuntimeError(
        "SESSION_SECRET fehlt in der .env."
    )


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie=(
        "smart_wardrobe_session"
    ),
    same_site="lax",
    https_only=False,
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/provider")
def select_ai_provider(
    request: Request,
    ai_provider: str = Form(...),
):
    """Store the selected AI provider and redirect to the wardrobe."""
    set_selected_ai_provider(
        request=request,
        provider=ai_provider,
    )

    return RedirectResponse(
        url="/",
        status_code=HTTP_303_SEE_OTHER,
    )


@app.get('/json')
def index():
    """Return all wardrobe items as JSON-compatible dictionaries."""
    manager = DataManager()
    items = manager.get_all_items()
    return [item.to_dict() for item in items]

@app.get("/")
def landingpage(
    request: Request,
):
    """Render the wardrobe landing page and selected provider."""
    selected_ai_provider = (
        get_selected_ai_provider(
            request
        )
    )

    manager = DataManager()
    items = manager.get_all_items()

    return templates.TemplateResponse(
        "wardrobe.html",
        {
            "request": request,
            "items": items,
            "selected_ai_provider": (
                selected_ai_provider
            ),
        },
    )

@app.get("/items/create")
def show_create_form(
    request: Request,
):
    """Render the item creation form for the selected provider."""
    selected_provider = (
        require_selected_ai_provider(
            request
        )
    )

    return templates.TemplateResponse(
        "create_item.html",
        {
            "request": request,
            "selected_ai_provider": (
                selected_provider
            ),
        },
    )


@app.post("/items/create")
def create_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    color: str = Form(...),
    condition: str = Form(...),
    type: str = Form(...),
    score: int = Form(...),
):
    """Create an item with the selected provider's embedding."""
    selected_provider = (
        require_selected_ai_provider(
            request
        )
    )

    manager = DataManager(
        embedding_provider=(
            selected_provider
        )
    )

    created = manager.create_item(
        name=name,
        description=description,
        color=color,
        condition=condition,
        type=type,
        score=score,
    )

    if not created:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": (
                    "Das Kleidungsstück konnte "
                    f"mit {selected_provider.upper()} "
                    "nicht gespeichert werden. "
                    "Bitte prüfe API-Key und Limit."
                ),
            },
            status_code=500,
        )

    return RedirectResponse(
        url="/",
        status_code=HTTP_303_SEE_OTHER,
    )

@app.post("/items/{item_id}/delete")
def delete_item(item_id: int):
    """Delete an item and redirect to the wardrobe."""
    manager = DataManager()
    manager.delete_item(item_id)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@app.get("/items/{item_id}/edit")
def show_edit_formular(
    request: Request,
    item_id: int,
):
    """Render the item edit form or a not-found response."""
    selected_provider = (
        require_selected_ai_provider(
            request
        )
    )

    manager = DataManager(
        embedding_provider=(
            selected_provider
        )
    )

    item = manager.get_item_by_id(
        item_id
    )

    if item is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": (
                    "Das Kleidungsstück wurde "
                    "nicht gefunden."
                ),
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        "update_item.html",
        {
            "request": request,
            "item": item,
            "selected_ai_provider": (
                selected_provider
            ),
        },
    )


@app.post("/items/{item_id}/edit")
def edit_item(
    request: Request,
    item_id: int,
    name: str = Form(...),
    description: str = Form(...),
    color: str = Form(...),
    condition: str = Form(...),
    type: str = Form(...),
    score: int = Form(...),
):
    """Update an item and its selected-provider embedding."""
    selected_provider = (
        require_selected_ai_provider(
            request
        )
    )

    manager = DataManager(
        embedding_provider=(
            selected_provider
        )
    )

    updated = manager.update_item(
        item_id,
        name=name,
        description=description,
        color=color,
        condition=condition,
        type=type,
        score=score,
    )

    if not updated:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": (
                    "Das Kleidungsstück konnte "
                    f"mit {selected_provider.upper()} "
                    "nicht aktualisiert werden."
                ),
            },
            status_code=500,
        )

    return RedirectResponse(
        url="/",
        status_code=HTTP_303_SEE_OTHER,
    )


@app.get("/input")
def show_input_bar(
    request: Request,
):
    """Render the outfit request form for the selected provider."""
    selected_provider = (
        require_selected_ai_provider(
            request
        )
    )

    return templates.TemplateResponse(
        "input_for_llm.html",
        {
            "request": request,
            "selected_ai_provider": (
                selected_provider
            ),
        },
    )

@app.post("/input")
def get_input_and_built_answer(
    request: Request,



    user_input: str = Form(...),
    event_input: str = Form(...),
    location_input: str = Form(...),
    season_input: str = Form(...),
    weather_input: str = Form(...),
    mood_input: str = Form(...),


    colors_any: str = Form(""),
    colors_all: str = Form(""),
    score: str = Form(""),
    score_min: str = Form(""),
    score_max: str = Form(""),
    condition_any: str = Form(""),
    name_contains: str = Form(""),
    description_contains: str = Form(""),
    text_all: str = Form(""),
    text_any: str = Form(""),
    limit: str = Form(""),
):
    """Filter wardrobe items and render outfits from the selected provider."""
    selected_provider = (
        require_selected_ai_provider(
            request
        )
    )


    filter_kwargs = build_filter_kwargs_from_strings(
        colors_any=colors_any,
        colors_all=colors_all,
        score=score,
        score_min=score_min,
        score_max=score_max,
        condition_any=condition_any,
        name_contains=name_contains,
        description_contains=description_contains,
        text_all=text_all,
        text_any=text_any,
        limit=limit,
    )


    filtered_ids = filter_db_dynamic(**filter_kwargs)

    if not filtered_ids:
        return templates.TemplateResponse("error.html", {"request": request,
                                                         "message": "Filter liefern gar keine Items - Filter anpassen"})

    if len(filtered_ids) < 5:
        return templates.TemplateResponse("error.html", {"request": request, "message": "nicht genügend Items zum Erstellen eines Outfits"})



    state = run_agent_from_payload(weather_input=weather_input, event_input=event_input, mood_input=mood_input)



    payload = {
        "user_input": user_input,
        "context": {
            "event_input": event_input,
            "location_input": location_input,
            "season_input": season_input,
            "weather_input": weather_input,
            "mood_input": mood_input,
            "styling_hints": state[
                "style_hints"
            ],
        },
        "retrieval": {
            "priority_categories": (
                state.get(
                    "priority_categories",
                    [],
                )
            ),
            "category_limit_overrides": (
                state.get(
                    "category_limit_overrides",
                    {},
                )
            ),
        },
    }
    answer_text = build_outfit_with_provider(
        provider=selected_provider,
        payload=payload,
        filtered_ids=filtered_ids,
    )

    return templates.TemplateResponse(
        "answer.html",
        {
            "request": request,
            "answer_text": answer_text,
        },
    )

@app.exception_handler(UnknownAIProviderError)
async def handle_unknown_ai_provider(
    request: Request,
    exc: UnknownAIProviderError,
):
    """Render an error page for an unknown provider."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "message": str(exc),
        },
        status_code=400,
    )


@app.exception_handler(AIProviderRequestError)
async def handle_ai_provider_request_error(
    request: Request,
    exc: AIProviderRequestError,
):
    """Render an error page for an invalid provider request."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "message": str(exc),
        },
        status_code=422,
    )


@app.exception_handler(AIProviderHallucinationError)
async def handle_ai_provider_hallucination(
    request: Request,
    exc: AIProviderHallucinationError,
):
    """Render an error page for invalid generated item IDs."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "message": str(exc),
        },
        status_code=422,
    )


@app.exception_handler(AIProviderGenerationError)
async def handle_ai_provider_generation_error(
    request: Request,
    exc: AIProviderGenerationError,
):
    """Render an error page when outfit generation fails."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "message": str(exc),
        },
        status_code=500,
    )

@app.exception_handler(
    AIProviderNotSelectedError
)
async def handle_missing_ai_provider(
    request: Request,
    exc: AIProviderNotSelectedError,
):
    """Redirect home when no AI provider is selected."""
    return RedirectResponse(
        url="/",
        status_code=HTTP_303_SEE_OTHER,
    )
