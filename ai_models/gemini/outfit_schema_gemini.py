"""Define structured schemas for Gemini outfit responses."""

from pydantic import BaseModel, Field


class OutfitSlots(BaseModel):


    """Define the required and optional wardrobe ID slots for one outfit."""
    top_id: int
    bottom_id: int | None = None
    shoes_id: int

    headwear_id: int | None = None
    outerwear_id: int | None = None
    socks_id: int | None = None
    bag_id: int | None = None
    accessory_id: int | None = None


class OutfitSuggestion(BaseModel):
    """Represent one outfit suggestion and its wardrobe slots."""
    name: str
    how_to_wear: str
    rationale: str
    slots: OutfitSlots


class OutfitSuggestions(BaseModel):
    """Require a response containing exactly three outfit suggestions."""
    outfits: list[OutfitSuggestion] = Field(
        min_length=3,
        max_length=3,
    )