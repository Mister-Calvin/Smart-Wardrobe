from pydantic import BaseModel, Field


class OutfitSlots(BaseModel):
    # Bei einem Kleid enthält top_id die ID des Kleides.
    # bottom_id bleibt dann leer.
    top_id: int
    bottom_id: int | None = None
    shoes_id: int

    headwear_id: int | None = None
    outerwear_id: int | None = None
    socks_id: int | None = None
    bag_id: int | None = None
    accessory_id: int | None = None


class OutfitSuggestion(BaseModel):
    name: str
    how_to_wear: str
    rationale: str
    slots: OutfitSlots


class OutfitSuggestions(BaseModel):
    outfits: list[OutfitSuggestion] = Field(
        min_length=3,
        max_length=3,
    )